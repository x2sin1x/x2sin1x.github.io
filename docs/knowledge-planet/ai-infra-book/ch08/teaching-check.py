#!/usr/bin/env python3
"""Recompute the chapter's worked examples on the RTX PRO 6000 from measured efficiency and exact arithmetic."""
from fractions import Fraction as F
from pathlib import Path
import json,math,statistics,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'calculations/src'))
from infra_calc.models import forward
from infra_calc.schema import Scenario
KiB=2**10;MiB=2**20;GiB=2**30
k=2*36*8*128*2
def load(p):return json.loads((ROOT/p).read_text())
def flops(history,tokens,head='last'):return forward('qwen3-8b',Scenario(history=history,tokens=tokens,output_head=head))['summary']['matrix_flops']
hw={d['id']:d for d in load('calculations/configs/hardware.json')['devices']}['rtx-pro6000-blackwell-ws']
BW=hw['memory']['bandwidth_bytes_per_second'];POWER=hw['power_watts']
PEAK=next(r['tera_ops_per_second'] for r in hw['peak_rates'] if r['input_precision']=='BF16' and r['accumulator_precision']=='FP32' and r['execution_unit']=='tensor' and r['sparsity']=='dense')*1e12
assert (BW,PEAK,POWER)==(1792e9,503.8e12,600)
eff={(r['kind'],r['batch']):r for r in load('experiments/ch08/08-01/efficiency.json')['rows']}
fit=load('experiments/ch08/08-01/efficiency.json')['schedule_fit']
for policy in ['fixed','continuous','chunked']:
 sc=load(f'calculations/scenarios/iteration-batching-pro6000-{policy}.json')
 assert sc['per_causal_pair_ns']==fit['per_causal_pair_ns'] and sc['per_new_token_ns']==round(fit['per_new_token_ns'],-2) and sc['step_base_ns']==round(fit['step_base_ns'],-4)

# Capacity (unchanged by device: 12 GiB KV pool, 16-token pages).
def pages(tokens):return ((tokens+15)//16)*16*k
short=pages(2048+255);long=pages(8192+255);prefix=6144*k;private=pages(8192-6144+255)
assert (short//MiB,long//MiB,prefix//MiB,private//MiB)==(324,1188,864,324)
assert (12*GiB//short,12*GiB//long,(12*GiB-prefix)//private)==(37,10,35)
shared=prefix+16*private
assert shared==6048*MiB and 16*long==19008*MiB
compressed=16*long*F(34,64)
assert compressed==10098*MiB

# 8.1.1 lifecycle: measured batch-1 2K TTFT and client inter-token interval (08-01 summary).
summary={(r['kind'],r['batch']):r for r in load('experiments/ch08/08-01/results/summary.json')['summary']}
ttft=summary[('short',1)]['median_ttft_ms'];itl=summary[('short',1)]['median_time_per_output_ms']
assert round(ttft)==96 and round(itl,1)==26.5
life=.1+.096+255*.0265;assert round(life,2)==6.95 and life<7 and life+.096>7

# 8.6.3 efficiency table and resource seconds.
table=[eff[('short',b)] for b in (1,4,16,64)]
assert [round(r['decode_bandwidth_efficiency']*100) for r in table]==[33,34,41,65]
assert [round(r['prefill_compute_efficiency']*100) for r in table]==[62,61,61,58]
b1=eff[('short',1)];b16=eff[('short',16)];b64=eff[('short',64)];p16=eff[('prefix',16)]
t_round=p16['decode_round_ms']/1e3;prefill_B=p16['prefill_phase_s']
r_P=p16['prefill_rate_new_tokens_per_s'];r_D=16/t_round
resource_s=2048/r_P+255/r_D
assert r_P==16059 and round(r_D)==585 and round(resource_s,3)==.563 and round(16*resource_s,2)==9.01
eta8=p16['prefill_compute_efficiency']
prefill_indep=16*flops(0,8192)/(PEAK*eta8)
read_C=15136811008+16*8192*k*34//64
t_C=(b16['decode_round_ms']+(read_C-b16['nominal_read_bytes'])/(b64['nominal_read_bytes']-b16['nominal_read_bytes'])*(b64['decode_round_ms']-b16['decode_round_ms']))/1e3
assert b64['nominal_read_bytes']==15136811008+16*8192*k
ttft_ratio=F('141.58')/F('129.41')  # 08-05 long_lookup, concurrency 1, DFlash K7 vs AR median TTFT (results/table.md)
dflash=load('experiments/ch08/08-05/results/summary.json')
extra_mib=dflash['dflash-7']['sampled_peak_MiB']-dflash['ar']['sampled_peak_MiB']
assert extra_mib==3188
prefill_D=prefill_B*float(ttft_ratio)
verify_flops=16*flops(8192,8,'all');verify_s=verify_flops/(PEAK*eta8)
assert verify_s<t_round
rows=[]
for name,memory,pre,steps,step in [
 ('A',16*long,prefill_indep,255,b64['decode_round_ms']/1e3),
 ('B',shared,prefill_B,255,t_round),
 ('C',compressed,prefill_indep,255,t_C),
 ('D',shared+extra_mib*MiB,prefill_D,85,t_round),
 ('E',shared,prefill_B,128,t_round+1e-4)]:
 t=pre+steps*step;ok=memory<=12*GiB and t<=7
 rows.append({'name':name,'memory_gib':float(memory/GiB),'prefill_s':pre,'rounds':steps,'round_ms':step*1e3,'time_s':t,'fits_12gib':memory<=12*GiB,'within_7s':t<=7,
              'gpu_seconds_per_qualified_result':t/16 if ok else None,'energy_upper_bound_j_per_result':POWER*t/16 if ok else None})
R={r['name']:r for r in rows}
assert [r['name'] for r in rows[:4] if r['fits_12gib'] and r['within_7s']]==['D']
assert (round(R['B']['time_s'],2),round(R['C']['time_s'],2),round(R['D']['time_s'],2),round(R['A']['time_s'],2))==(9.01,14.55,4.56,14.9)
assert round(prefill_indep,2)==7.34 and round(t_C*1e3,2)==28.26 and round(prefill_D,2)==2.23 and round(R['D']['memory_gib'],2)==9.02
assert round(R['D']['gpu_seconds_per_qualified_result'],3)==.285 and round(R['D']['energy_upper_bound_j_per_result'])==171
short16={'B':prefill_B+15*t_round,'D':prefill_D+5*t_round,'E':prefill_B+8*(t_round+1e-4)}
assert (round(short16['B'],2),round(short16['D'],2),round(short16['E'],2))==(2.45,2.37,2.26)
assert R['B']['memory_gib']<=6<R['D']['memory_gib'] and R['E']['memory_gib']<=6 and R['E']['within_7s']
service={}
for g in load('experiments/ch08/08-09/analysis.json')['groups']:service.setdefault(f"{g['service']}-{g['rate']}",[]).append(g['component_gross_j_per_qualified'])
energy={key:round(statistics.median(v),1) for key,v in service.items()}
assert (energy['continuous-1'],energy['continuous-4'],energy['continuous-16'],energy['serial-4'])==(615.0,652.0,1083.7,1982.3)

# 8.3.3 summary, 8.3.4 cache value, 8.4.2 conversion, 8.4.3 offload and codec.
bw_b1=b1['nominal_read_bytes']/(b1['decode_round_ms']/1e3);bw_b64=b64['nominal_read_bytes']/(b64['decode_round_ms']/1e3)
saving=6144*k/bw_b64;rebuild=flops(0,3072)/(PEAK*b1['prefill_compute_efficiency']);generate=2048*b1['decode_round_ms']/1e3
assert round(saving*1e3,2)==.78 and round(rebuild,3)==.145 and round(generate,1)==53.8 and round(rebuild/saving)==186
def cache(tokens,link):
 tr=flops(0,tokens,'none')/(PEAK*b1['prefill_compute_efficiency']);tf=tokens*k/link
 return tr,tf,F(1,2)*(tr-tf)-tf
A5=cache(6144,64e9);B5=cache(2048,64e9);A4=cache(6144,32e9);B4=cache(2048,32e9)
assert round(A5[0]*1e3,1)==307.9 and round(A5[1]*1e3,1)==14.2 and round(float(A5[2])*1e3,1)==132.7
assert round(float(B5[2])*1e3,1)==40.3 and round(3*float(B5[2])*1e3,1)==120.9 and A5[2]>3*B5[2]
tie=(3*float(B5[2])+A5[1])/(A5[0]-A5[1])
assert round(A5[1]/(A5[0]-A5[1])*100,1)==4.8 and round(A4[1]/(A4[0]-A4[1])*100,1)==10.1
convert=540*MiB/bw_b64;assert round(convert*1e3,3)==.487
copy=9*3*4096*12288*2;assert copy==2717908992
assert round(copy/64e9*1e3,1)==42.5 and round(copy/64e9*255,1)==10.8 and round(copy/450e9*1e3,1)==6.0 and round(copy/450e9*255,2)==1.54
assert round(copy*255/1e9)==693
assert round(64/(1-.25),1)==85.3

# 8.5 speculative decoding at batch 1.
def expected(a,m):return sum(F(a)**j for j in range(m+1))
t0=b1['decode_round_ms'];query=.1
spec={name:(t0+query)/float(expected(a,4)) for name,a in [('AAAA',F(1,4)),('BBBB',F(3,4))]}
assert round(spec['AAAA'],1)==19.8 and round(spec['BBBB'],2)==8.64
cross={name:float(expected(a,4))*t0-t0 for name,a in [('AAAA',F(1,4)),('BBBB',F(3,4))]}
assert round(cross['AAAA'],1)==8.7 and round(cross['BBBB'],1)==53.9
assert round(2000/(t0-spec['BBBB']))==114
drafter=int(F('1.953')*GiB);draft_ms=drafter/bw_b1*1e3
assert round(draft_ms,1)==3.6 and round((4*draft_ms+t0)/3,1)==13.5 and round((draft_ms+t0)/3,1)==9.9 and round((draft_ms+t0)/2,1)==14.9
steps={}
for mode in ['ar','dflash-7']:
 ev=[json.loads(x) for x in (ROOT/f'experiments/ch08/08-05/raw/{mode}/events.jsonl').read_text().splitlines()]
 steps[mode]=statistics.median([e['wall_s']*1e3 for e in ev if e['kind']=='step' and e['phase']!='warmup' and e['concurrency']==1])
assert round(steps['ar'],1)==16.9 and round(steps['dflash-7'],1)==15.2
ex7=[{'block':m,'expected_output':float(expected(F(3,4),m)),'linear_ms_per_token':(26.3+3.6*m)/float(expected(F(3,4),m)),'padded_ms_per_token':(26.3+3.6*4*math.ceil(m/4))/float(expected(F(3,4),m))} for m in [1,2,4,5,8]]
assert min((r for r in ex7 if r['block']!=5),key=lambda r:r['linear_ms_per_token'])['block']==4

out={'kind':'worked examples on RTX PRO 6000 Blackwell Workstation Edition; efficiencies from experiments/ch08/08-01/efficiency.json',
 'device':{'bandwidth_bytes_per_second':BW,'bf16_dense_flops':PEAK,'power_watts':POWER},
 'capacity':{'short_mib':short//MiB,'long_mib':long//MiB,'shared_16_mib':shared//MiB,'independent_16_mib':16*long//MiB,'q8_16_mib':float(compressed/MiB)},
 'lifecycle':{'ttft_ms':ttft,'itl_ms':itl,'completion_s':life,'deadline_s':7},
 'rates_8k_prefix_b16':{'r_P_new_tokens_per_s':r_P,'r_D_calls_per_s':r_D,'resource_seconds_per_request':resource_s},
 'design_candidates':rows,'design_16_output_s':short16,
 'dflash':{'extra_process_mib':extra_mib,'ttft_ratio':float(ttft_ratio),'verify_matrix_flops':verify_flops,'verify_s':verify_s,'step_median_ms':steps},
 'summary_break_even':{'saving_ms_per_step':saving*1e3,'rebuild_s':rebuild,'generate_s':generate,'steps_generate':(generate+rebuild)/saving,'steps_rebuild':rebuild/saving},
 'cache':{'A_gen5':[A5[0],A5[1],float(A5[2])],'B_gen5':[B5[0],B5[1],float(B5[2])],'A_gen4':[A4[0],A4[1],float(A4[2])],'B_gen4':[B4[0],B4[1],float(B4[2])],'exercise_4_A_probability_tie':tie},
 'kv_conversion_saving_ms':convert*1e3,'offload_copy_ms':{'pcie5':copy/64e9*1e3,'gh200_c2c':copy/450e9*1e3},'exercise_5_bandwidth_for_1s_gb_s':copy*255/1e9,
 'speculation':{'ordinary_ms':t0,'ms_per_token':spec,'query_break_even_ms':cross,'index_break_even_tokens':2000/(t0-spec['BBBB']),'drafter_forward_ms':draft_ms},
 'exercise_7':ex7,'energy_per_qualified_j_08_09_median':energy,
 'passed':True}
(HERE/'teaching-validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False,indent=2))
