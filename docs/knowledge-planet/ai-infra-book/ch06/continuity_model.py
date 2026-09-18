"""Chapter-six execution model on an HGX H100 server.

Dense TP comparison: Qwen3-32B decode at the 128K YaRN context, H100 SXM HBM from
calculations/configs/hardware.json, NVLink 4 through NVSwitch, per-round latency
measured on the same platform (MSCCL++ Table 1), and the two-server AllReduce time
measured by nccl-tests (experiment 7-3).  Every other block (dense/MoE capacity,
rack power) reads archived result files or declared specs listed in PARAMS.
"""
from pathlib import Path
import csv, json, math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CALC = ROOT / 'calculations'


def _hardware(device_id):
    table = json.loads((CALC / 'configs/hardware.json').read_text())
    items = table if isinstance(table, list) else table.get('devices', table)
    device = next(d for d in items if d['id'] == device_id)
    rate = next(r for r in device['peak_rates'] if r['input_precision'] in ('BF16', 'FP16')
                and r['sparsity'] == 'dense' and r['execution_unit'] == 'tensor')
    return dict(id=device_id, capacity_bytes=int(device['memory']['nominal_capacity'] * 1e9),
                hbm_Bps=device['memory']['bandwidth_bytes_per_second'],
                matrix_flops_per_s=rate['tera_ops_per_second'] * 1e12, power_w=device['power_watts'])


def _measured_allreduce(size_bytes, run='hgx2', mode='out_of_place'):
    """Smallest archived nccl-tests message not below size_bytes (experiment 7-3 rows)."""
    rows = [r for r in csv.DictReader((ROOT / 'experiments/ch07/07-03/rows.csv').open())
            if r['run'] == run and r['mode'] == mode and r['row_correct'] == 'True']
    row = min((r for r in rows if int(r['size_bytes']) >= size_bytes), key=lambda r: int(r['size_bytes']))
    return dict(run=run, mode=mode, size_bytes=int(row['size_bytes']), nranks=int(row['nranks']),
                time_s=float(row['time_us']) * 1e-6, source='experiments/ch07/07-03/' + row['source'],
                line=int(row['line']))


H100 = _hardware('h100-sxm')
CONFIG = json.loads((CALC / 'configs/models/qwen3-32b/config.json').read_text())
PARAMS = dict(
    model='qwen3-32b', device='h100-sxm', gpus_per_server=8,
    history=131064, steps=8, sessions=4, workspace_bytes=2 ** 31,
    history_32k=32760,
    nvlink_Bps=450e9,          # H100 whitepaper: 18 NVLink4 links x 25 GB/s each direction
    nvlink_alpha_s=822e-9,     # MSCCL++ (ASPLOS'26) Table 1, H100 NVLink latency, nvbandwidth
    ib_Bps=50e9,               # ConnectX-7 400 Gb/s
    ib_alpha_s=3.76e-6,        # MSCCL++ Table 1, InfiniBand latency, RDMA perftest
    deadline_s=0.130, single_deadline_s=0.050, required_fraction=0.75,
    fault_at_ms=20.0, stall_ms=40.0,
    server_power_w=10200,      # DGX H100 system power, standard configuration (max)
)
L = CONFIG['num_hidden_layers']; H = CONFIG['hidden_size']; F = CONFIG['intermediate_size']
QH = CONFIG['num_attention_heads']; KVH = CONFIG['num_key_value_heads']; D = CONFIG['head_dim']
V = CONFIG['vocab_size']; E = 2
ATTN_BYTES = (2 * H * QH * D + 2 * H * KVH * D) * E
FFN_BYTES = 3 * H * F * E
HEAD_BYTES = V * H * E
WEIGHT_READ = L * (ATTN_BYTES + FFN_BYTES) + HEAD_BYTES
KV_TOKEN = 2 * L * KVH * D * E
MESSAGE = H * E                      # one token's BF16 hidden vector
ALLREDUCES = 2 * L
KV_TRANSFER = D * E                  # one KV head's K (or V) vector for one token and layer
NORM_BYTES = (L * (2 * H + 2 * D) + H) * E
WEIGHT_RESIDENT = WEIGHT_READ + V * H * E + NORM_BYTES   # + embedding table + norms


def ring(p, m, alpha, bw):
    return 2 * (p - 1) * alpha + 2 * (p - 1) / p * m / bw


def tree(p, m, alpha, bw):
    return 2 * math.log2(p) * (alpha + m / bw)


def allreduce(p, fabric='nvlink'):
    if p == 1:
        return 0.
    if fabric == 'nvlink':
        return ring(p, MESSAGE, PARAMS['nvlink_alpha_s'], PARAMS['nvlink_Bps'])
    if fabric == 'measured_two_servers':
        m = _measured_allreduce(MESSAGE)
        assert m['nranks'] == p
        return m['time_s']
    raise ValueError(fabric)


def step(p, history, fabric='nvlink'):
    kv_read = KV_TOKEN * (history + 1)
    kv_shards = min(p, KVH)
    local_bytes = WEIGHT_READ / p + kv_read / kv_shards
    local = local_bytes / H100['hbm_Bps']
    flops = WEIGHT_READ + 4 * QH * D * (history + 1) * L     # 2 FLOPs per weight element; QK and PV
    compute = flops / p / H100['matrix_flops_per_s']
    comm = ALLREDUCES * allreduce(p, fabric)
    return dict(tp=p, history=history, fabric=fabric, weight_read_bytes=WEIGHT_READ, kv_read_bytes=kv_read,
                per_card_hbm_bytes=local_bytes, local_s=local, compute_s=compute,
                local_bound='memory' if local >= compute else 'compute',
                allreduce_s=allreduce(p, fabric), communication_s=comm,
                serial_s=0., total_s=max(local, compute) + comm)


def per_card_bytes(p, positions, sessions):
    weights = (WEIGHT_RESIDENT - NORM_BYTES) / p + NORM_BYTES
    kv = KV_TOKEN * positions / min(p, KVH) * sessions
    return weights, kv, PARAMS['workspace_bytes']


def max_sessions(p, positions):
    weights, _, workspace = per_card_bytes(p, positions, 0)
    per_session = KV_TOKEN * positions / min(p, KVH)
    return max(0, math.floor((H100['capacity_bytes'] - weights - workspace) / per_session))


def schedule(p, gpus, history, sessions, fault=False):
    instances = gpus // p
    service = sum(step(p, history + j)['total_s'] for j in range(PARAMS['steps'])) * 1000
    clocks = [0.] * instances; ends = []
    for r in range(sessions):
        inst = r % instances
        if fault and inst == 0 and clocks[inst] == 0:
            clocks[inst] = PARAMS['fault_at_ms'] + PARAMS['stall_ms']
        clocks[inst] += service; ends.append(clocks[inst])
    return service, ends


def candidates(history, deadline_s, sessions=4, gpus=8):
    rows = []
    positions = history + PARAMS['steps']
    need = math.ceil(sessions * PARAMS['required_fraction'])
    for p in [1, 2, 4, 8]:
        instances = gpus // p
        per_instance = math.ceil(sessions / instances)
        fits = max_sessions(p, positions) >= per_instance
        service, healthy = schedule(p, gpus, history, sessions)
        _, fault = schedule(p, gpus, history, sessions, fault=True)
        row = dict(tp=p, instances=instances, sessions_per_instance=per_instance,
                   max_sessions_per_instance=max_sessions(p, positions), capacity_fits=fits,
                   step_times_s=[step(p, history + j)['total_s'] for j in range(PARAMS['steps'])],
                   service_ms=service, healthy_completion_ms=healthy, fault_completion_ms=fault)
        for phase, ends in [('healthy', healthy), ('fault', fault)]:
            ontime = sum(t <= deadline_s * 1000 for t in ends)
            gpu_s = gpus * max(ends) / 1000
            row[phase + '_gpu_seconds'] = gpu_s
            row[phase + '_energy_j'] = PARAMS['server_power_w'] * gpus / PARAMS['gpus_per_server'] * max(ends) / 1000
            row[phase + '_ontime'] = ontime
            row[phase + '_eligible'] = fits and ontime >= need
            row[phase + '_gpu_seconds_per_ontime'] = gpu_s / ontime if ontime else None
        rows.append(row)
    return rows


def dense_moe_capacity():
    """Resident weights, per-request state and fit counts for three same-class models on H100."""
    res = CALC / 'results'
    def load(name):
        return json.loads((res / (name + '.json')).read_text())
    models = []
    for name, b1, b64 in [('qwen3-32b', 'qwen3-32b-decode-b1-s32768', 'qwen3-32b-decode-b64-s32768'),
                          ('qwen3-30b-a3b', 'qwen3-30b-a3b-decode-b1-s32768', 'qwen3-30b-a3b-decode-b64-s32768-balanced')]:
        one, many = load(b1)['summary'], load(b64)['summary']
        models.append(dict(model=name, kind='dense' if name == 'qwen3-32b' else 'moe_gqa',
                           weight_resident_bytes=one['weight_resident_bytes'],
                           kv_bytes_per_token=one['kv_bytes_per_token_per_request'], fixed_state_bytes=0,
                           weight_read_b1=one['weight_read_once_per_operator_bytes'],
                           weight_read_b64=many['weight_read_once_per_operator_bytes'],
                           matrix_flops_b64=many['matrix_flops'],
                           state_read_b64=many['kv_attention_unique_payload_bytes'],
                           sources=[b1, b64]))
    one, many = load('qwen36-decode-b1-s32768'), load('qwen36-decode-b64-s32768')
    cap = load('qwen36-capacity-b1-n131072')['summary']['budget_components_bytes']
    fixed = cap['recurrent_fp32_bytes'] + cap['convolution_bf16_bytes']
    kv_token = cap['full_attention_kv_bytes'] // 131072
    st = many['state']
    models.append(dict(model='qwen3.6-35b-a3b', kind='moe_hybrid',
                       weight_resident_bytes=one['summary']['base_checkpoint_bytes'],
                       kv_bytes_per_token=kv_token, fixed_state_bytes=fixed,
                       weight_read_b1=one['summary']['weight_read_bytes'],
                       weight_read_b64=many['summary']['weight_read_bytes'],
                       matrix_flops_b64=many['summary']['matrix_flops'],
                       state_read_b64=st['full_kv_after_bytes'] + st['linear_recurrent_fp32_bytes'] + st['linear_conv_slot_bytes'],
                       sources=['qwen36-decode-b1-s32768', 'qwen36-decode-b64-s32768', 'qwen36-capacity-b1-n131072']))
    for m in models:
        m['state_per_request'] = {str(n): m['kv_bytes_per_token'] * n + m['fixed_state_bytes'] for n in (32768, 131072, 262144)}
        m['b64_state_read_s'] = m['state_read_b64'] / H100['hbm_Bps']
        m['b64_weight_read_s'] = m['weight_read_b64'] / H100['hbm_Bps']
        fits = {}
        for cards in (1, 2):
            for n in (32768, 131072):
                free = cards * (H100['capacity_bytes'] - PARAMS['workspace_bytes']) - m['weight_resident_bytes']
                fits[f'{cards}x{n}'] = max(0, math.floor(free / m['state_per_request'][str(n)]))
        m['requests_fit_h100'] = fits
    return dict(device=H100['id'], capacity_bytes=H100['capacity_bytes'], workspace_bytes=PARAMS['workspace_bytes'],
                fit_rule='floor((cards*(80 GB - 2 GiB) - resident weights) / per-request state); weights and state spread evenly',
                models=models)


def memory_pool():
    """Four H100 80 GB nodes; one job borrows HBM on another node through a ConnectX-7 path."""
    cap = H100['capacity_bytes']; demand = [100e9, 60e9, 40e9, 40e9]
    borrowed = demand[0] - cap
    placed = [cap, demand[1] + borrowed, demand[2], demand[3]]
    path = PARAMS['ib_Bps']; latency = 2 * PARAMS['ib_alpha_s']; q = KV_TRANSFER
    window = lambda u: u * q / latency
    rows = []
    for u in (128, 4096):
        usable = min(path, window(u))
        rows.append(dict(in_flight=u, window_Bps=window(u), usable_Bps=usable, read_s=borrowed / usable,
                         max_reads_per_s=usable / borrowed))
    freq = [1 / 60, 1, 20]
    repeat = 10
    return dict(node_capacity_bytes=cap, demand_bytes=demand, borrowed_bytes=borrowed, physical_after_bytes=placed,
                free_before_bytes=[cap - d for d in demand[1:]], free_after_bytes=sum(cap - x for x in placed),
                path_Bps=path, read_latency_s=latency, transaction_bytes=q,
                min_in_flight=math.ceil(path * latency / q), windows=rows,
                frequency_per_s=freq, demand_Bps=[borrowed * f for f in freq],
                repeat=repeat, remote_repeat_s=repeat * borrowed / path,
                fetch_then_local_s=borrowed / path + repeat * borrowed / H100['hbm_Bps'],
                local_read_s=borrowed / H100['hbm_Bps'])


def rack_power(budget_kw=120, air_kw=40):
    per_server = PARAMS['server_power_w'] / 1000
    rows = [dict(gpus=g, servers=g // 8, power_kw=g // 8 * per_server, within_budget=g // 8 * per_server <= budget_kw)
            for g in (64, 72, 96)]
    return dict(server_power_kw=per_server, per_gpu_kw=per_server / 8, budget_kw=budget_kw, air_cooling_kw=air_kw,
                max_servers=math.floor(budget_kw / per_server), max_gpus=8 * math.floor(budget_kw / per_server),
                max_servers_air=math.floor(air_kw / per_server), max_gpus_air=8 * math.floor(air_kw / per_server),
                four_servers_kw=4 * per_server, rows=rows)


def generate():
    base = [step(p, PARAMS['history']) for p in [1, 2, 4, 8]]
    ring8 = ring(8, MESSAGE, PARAMS['nvlink_alpha_s'], PARAMS['nvlink_Bps'])
    tree8 = tree(8, MESSAGE, PARAMS['nvlink_alpha_s'], PARAMS['nvlink_Bps'])
    prefill = 8192 * MESSAGE
    a, b = PARAMS['nvlink_alpha_s'], PARAMS['nvlink_Bps']
    crossover = 8 * a * b / (6 - 1.75)
    out = dict(
        kind='hgx_h100_dense_tp_model', parameters=PARAMS, device=H100,
        model=dict(name=PARAMS['model'], layers=L, hidden=H, intermediate=F, query_heads=QH, kv_heads=KVH,
                   head_dim=D, vocab=V, attention_bytes_per_layer=ATTN_BYTES, ffn_bytes_per_layer=FFN_BYTES,
                   head_bytes=HEAD_BYTES, weight_read_bytes=WEIGHT_READ, weight_resident_bytes=WEIGHT_RESIDENT,
                   kv_bytes_per_token=KV_TOKEN, message_bytes=MESSAGE, allreduces_per_step=ALLREDUCES),
        capacity={str(p): dict(zip(['weights', 'kv', 'workspace'], per_card_bytes(p, PARAMS['history'] + PARAMS['steps'], 1)),
                               max_sessions_128k=max_sessions(p, PARAMS['history'] + PARAMS['steps']),
                               max_sessions_32k=max_sessions(p, 32768)) for p in [1, 2, 4, 8, 16]},
        first_steps=base,
        collectives=dict(participants=8, alpha_s=a, bandwidth_Bps=b, ring_s=ring8, tree_s=tree8,
                         prefill_bytes=prefill, ring_prefill_s=ring(8, prefill, a, b), tree_prefill_s=tree(8, prefill, a, b),
                         crossover_bytes=crossover,
                         bandwidth_doubled_saving_s=ALLREDUCES * (ring8 - ring(8, MESSAGE, a, 2 * b)),
                         alpha_halved_saving_s=ALLREDUCES * (ring8 - ring(8, MESSAGE, a / 2, b)),
                         alpha_total_s=ALLREDUCES * 14 * a),
        two_servers=dict(measured=_measured_allreduce(MESSAGE), tp16=step(16, PARAMS['history'], 'measured_two_servers'),
                         flat_ring_ib_s=ring(16, MESSAGE, PARAMS['ib_alpha_s'], PARAMS['ib_Bps']),
                         nvlink_domain_tp16=step(16, PARAMS['history'], 'nvlink')),
        candidates=candidates(PARAMS['history'], PARAMS['deadline_s']),
        candidates_32k=candidates(PARAMS['history_32k'], PARAMS['deadline_s']),
        single_session=[dict(tp=p, service_ms=schedule(p, 8, PARAMS['history'], 1)[0]) for p in [1, 2, 4, 8]]
                       + [dict(tp=16, fabric='measured_two_servers',
                               service_ms=sum(step(16, PARAMS['history'] + j, 'measured_two_servers')['total_s']
                                              for j in range(PARAMS['steps'])) * 1000)],
        dense_moe=dense_moe_capacity(),
        rack=rack_power(),
        memory_pool=memory_pool(),
    )
    (HERE / 'continuity-model.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
    return out


if __name__ == '__main__':
    d = generate()
    for x in d['first_steps']:
        print('TP', x['tp'], 'local %.4f comm %.4f total %.4f ms' % (x['local_s'] * 1e3, x['communication_s'] * 1e3, x['total_s'] * 1e3), x['local_bound'])
    for c in d['candidates']:
        print(c['tp'], c['capacity_fits'], c['max_sessions_per_instance'], round(c['service_ms'], 3), [round(t, 2) for t in c['healthy_completion_ms']],
              [round(t, 2) for t in c['fault_completion_ms']], c['healthy_ontime'], c['fault_ontime'],
              round(c['healthy_gpu_seconds'], 4), c['healthy_gpu_seconds_per_ontime'], c['fault_gpu_seconds_per_ontime'])
    print(json.dumps(d['collectives'], indent=1)); print(json.dumps(d['two_servers'], indent=1)[:1500])
    print(d['single_session']); print(json.dumps(d['rack']))
