#!/usr/bin/env python3
"""Reconstruct chapter 4 teaching boundaries and finite-slot schedules."""
from pathlib import Path
from fractions import Fraction
import json, math
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def pipeline(slots, compute=128, extra_latency=128):
    rows=[]; port_free=0; matrix_free=0; released=[0]*slots
    for i in range(4):
        slot=i%slots
        issue=max(port_free,released[slot]); transfer_end=issue+64
        ready=transfer_end+extra_latency; start=max(ready,matrix_free); end=start+compute
        rows.append(dict(chunk=i,slot=slot,issue_start=issue,transfer_end=transfer_end,
                         data_ready=ready,compute_start=start,compute_end=end,slot_released=end))
        port_free=transfer_end;matrix_free=end;released[slot]=end
    return dict(input_slots=slots,compute_ticks=compute,extra_latency_ticks=extra_latency,
                input_buffer_bytes=slots*16384,finish_tick=matrix_free,chunks=rows)

def derive():
    base=json.loads((ROOT/'calculations/results/attention-input-base.json').read_text())
    schedules=[pipeline(n) for n in range(1,5)]
    # Check overlapping source cases without modifying their original enumeration.
    keys=list(schedules[0]['chunks'][0])
    for n in [1,2,4]:
        source=next(r for r in base['rows'] if r['mode']=='asynchronous-direct-to-buffer' and r['input_slots']==n)
        expected=schedules[n-1]
        assert source['timing']['finish_tick']==expected['finish_tick']
        assert [{k:r[k] for k in keys} for r in source['timing']['chunks']]==expected['chunks']
    intensity=Fraction(165200000000000,1008000000000)
    crossing=intensity*4096/(4096-2*intensity)
    return dict(source='calculations/results/attention-input-base.json',baseline=schedules,
                matrix_double=[pipeline(n,64) for n in range(1,5)],
                longer_latency=[pipeline(n,128,256) for n in range(1,5)],
                boundaries=dict(roofline_crossing_rows=float(crossing),first_compute_bound_row=math.floor(crossing)+1,
                    asymptotic_intensity=2048,host_reuse_count=math.ceil(Fraction(RTX4090_BW,PCIE4_X16)),
                    message_crossing_bytes=int(ALPHA*H100_NVLINK),first_transfer_dominated_row=math.floor(ALPHA*H100_NVLINK/8192)+1,
                    minimum_baseline_slots=3,minimum_double_matrix_slots=4),
                die_locality=die_locality(),host_link=host_link(),interconnect=interconnect(),
                measured_decode=measured_decode(),energy=energy(),groq_kv=groq_kv(),
                provenance='Tick = one B200 SM clock with FA4 per-SM rates; schedules are derived, not GPU measurements.')

def device(name):
    hw=json.loads((ROOT/'calculations/configs/hardware.json').read_text())['devices']
    return next(d for d in hw if d['id']==name)

# Named-device inputs. Bandwidths and power come from calculations/configs/hardware.json;
# link rates from the archived specifications cited in the chapter footnotes.
RTX4090_BW=int(device('rtx4090')['memory']['bandwidth_bytes_per_second'])        # 1008 GB/s
PCIE4_X16=32*10**9            # PCIe 4.0 x16, 64 GB/s bidirectional = 32 GB/s per direction
H100_NVLINK=450*10**9         # NVLink 4, 900 GB/s bidirectional = 450 GB/s per direction
A100_NVLINK=300*10**9         # NVLink 3, 600 GB/s bidirectional = 300 GB/s per direction
ALPHA=Fraction(2,10**6)       # per-transfer startup, same as the NVLink per-round startup in chapter 7

def die_locality():
    b200=device('b200-sxm')['memory']
    local=Fraction(32*2**30); act=64*2**20
    cases=[]
    for name,die_hbm,link,capacity in [
        ('B200 (HGX)',Fraction(int(b200['bandwidth_bytes_per_second']),2),10*10**12,b200['nominal_capacity']/2),
        ('Ascend 910C',Fraction(1600*10**9),270*10**9,64)]:
        remote_rate=min(die_hbm,link)
        t_local=local/die_hbm; t_remote=local/remote_rate
        cases.append(dict(device=name,die_capacity_GB=capacity,die_hbm_bytes_per_second=float(die_hbm),
            link_bytes_per_second_per_direction=link,link_to_hbm_ratio=float(Fraction(link)/die_hbm),
            local_ms=float(t_local*1000),remote_ms=float(t_remote*1000),serial_ms=float((t_local+t_remote)*1000),
            remote_share=float(t_remote/(t_local+t_remote)),overlapped_ms=float(max(t_local,t_remote)*1000),
            split_ms=float(t_local*1000),activation_us=float(Fraction(act,link)*10**6)))
    return dict(weights_per_die_bytes=int(local),activation_bytes=act,cases=cases)

def host_link():
    v=64*2**20
    return dict(bytes=v,h2d_ms=float(Fraction(v,PCIE4_X16)*1000),gpu_read_us=float(Fraction(v,RTX4090_BW)*10**6),
                ratio=float(Fraction(RTX4090_BW,PCIE4_X16)),min_reuse=math.ceil(Fraction(RTX4090_BW,PCIE4_X16)),
                per_call_at_100_us=float(Fraction(v,PCIE4_X16)/100*10**6))

def interconnect():
    rows=[]
    for payload in (8192,2*2**20):
        rows.append(dict(payload=payload,**{k:float((ALPHA+Fraction(payload,r))*10**6) for k,r in [('a100_us',A100_NVLINK),('h100_us',H100_NVLINK)]},
                         h100_half_alpha_us=float((ALPHA/2+Fraction(payload,H100_NVLINK))*10**6)))
    return dict(alpha_us=float(ALPHA*10**6),rates=[A100_NVLINK,H100_NVLINK],rows=rows,
                crossing_bytes=int(ALPHA*H100_NVLINK),crossing_rows=float(ALPHA*H100_NVLINK/8192))

def measured_decode():
    eff=json.loads((ROOT/'experiments/ch08/08-01/efficiency.json').read_text())
    row=next(r for r in eff['rows'] if r['kind']=='prefix' and r['batch']==1)
    short=next(r for r in eff['rows'] if r['kind']=='short' and r['batch']==1)
    big=next(r for r in eff['rows'] if r['kind']=='short' and r['batch']==64)
    bw=eff['peak_bandwidth_bytes_per_second']; t=row['decode_round_ms']
    bound=row['nominal_read_bytes']/bw*1000
    return dict(device=eff['device'],read_bytes=row['nominal_read_bytes'],bound_ms=bound,bound_128_s=128*bound/1000,
                bound_tokens_per_s=1000/bound,measured_ms=t,measured_runs=row['decode_round_ms_runs'],
                measured_tokens_per_s=1000/t,measured_128_s=128*t/1000,fraction=bound/t,non_read_ms=t-bound,
                short_ms=short['decode_round_ms'],short_read_bytes=short['nominal_read_bytes'],
                extra_read_ms=(row['nominal_read_bytes']-short['nominal_read_bytes'])/bw*1000,
                b64_ms=big['decode_round_ms'],b64_read_bytes=big['nominal_read_bytes'],b64_bound_ms=big['peak_read_ms'],
                b64_effective_bytes_per_second=big['nominal_read_bytes']/(big['decode_round_ms']/1000))

def energy():
    runs=json.loads((ROOT/'experiments/ch04/04-06/results/projection-summary.json').read_text())
    wall={(r['device'],r['m'],r['mode']):r['wall_median_us'] for r in runs}
    watts=device('rtx-pro6000-blackwell-ws')['power_watts']
    calls=[dict(m=m,rtx_us=wall[('cuda',m,'reused')],mac_us=wall[('mps',m,'reused')],
                ratio=wall[('mps',m,'reused')]/wall[('cuda',m,'reused')],
                rtx_mJ=watts*wall[('cuda',m,'reused')]/1000,
                mac_breakeven_W=watts/(wall[('mps',m,'reused')]/wall[('cuda',m,'reused')])) for m in (1,256)]
    step=[]
    for name in ('rtx4090','rtx5090'):
        d=device(name);t=16344770560/d['memory']['bandwidth_bytes_per_second']
        step.append(dict(device=name,watts=d['power_watts'],step_ms=t*1000,joules=d['power_watts']*t))
    return dict(rtx_pro6000_watts=watts,calls=calls,decode_step=step,
                power_ratio=step[1]['watts']/step[0]['watts'],energy_ratio=step[1]['joules']/step[0]['joules'])

def groq_kv():
    chip=220*2**20; kv=1207959552; weights=16381470720
    return dict(chip_sram_bytes=chip,one_request=math.ceil(Fraction(kv,chip)),eight_requests=math.ceil(Fraction(8*kv,chip)),
                eight_requests_32k=math.ceil(Fraction(32*kv,chip)),weights_bf16=math.ceil(Fraction(weights,chip)))

if __name__=='__main__':
    result=derive()
    (HERE/'teaching-data.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Derived finite-slot schedules and resource boundaries.')
