#!/usr/bin/env python3
"""Chapter-only checks: coverage, locked evidence, figure labels, arithmetic and links."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json,re,math
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit,unquote
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];checks=[]
def check(name,value):checks.append({'check':name,'passed':bool(value)})
def read(p):return json.loads(p.read_text())
def close(a,b):return math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10)
import sys;sys.path.insert(0,str(HERE.parent));from preview_output import preview_path
md=HERE.parent/'11-资源调度与运行环境.md';s=md.read_text();o=next(p for p in [ROOT/'outlines'/md.name,ROOT/'archive/outlines'/md.name] if p.exists()).read_text();page=preview_path(md).read_text()
head=lambda text:re.findall(r'^#{2,3} (11\.\d+(?:\.\d+)?) ',text,re.M)
check('all five sections and eighteen subsection numbers match outline',head(s)==head(o) and len(head(s))==23)
check('ten exercises in order',re.findall(r'^\d+\. \*\*实验 11-(\d+)',s,re.M)==[str(i) for i in range(1,11)])
check('core exercises 1 2 10',re.findall(r'^\d+\. \*\*实验 11-(\d+)〔核心〕',s,re.M)==['1','2','10'])
figure_count=len(read(HERE/'figure-index.json'))
check('sequential external captions',re.findall(r'^\*图 11-(\d+)：',s,re.M)==[str(i) for i in range(1,figure_count+1)] and page.count('<figcaption>')==figure_count)
imgs=re.findall(r'!\[[^\]]*\]\(([^)]+)\)',s);check('active illustrations',len(imgs)==figure_count)
for image in imgs:
 p=md.parent/image;text=''.join(ET.parse(p).getroot().itertext())
 check('no internal figure numbering: '+p.stem,re.search(r'图\s*\d+\s*[-－–]\s*\d+',text) is None)
 check('SVG PNG PDF available: '+p.stem,all(p.with_suffix(e).exists() for e in ['.svg','.png','.pdf']))
missing=[]
for p in [md,HERE/'README.md',HERE/'reading-notes.md']:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
  u=urlsplit(link)
  if not u.scheme and u.path and (p.parent/unquote(u.path)).resolve() != (HERE/'validation.json').resolve() and not (p.parent/unquote(u.path)).exists():missing.append((str(p),link))
check('local links exist',not missing)
defs=re.findall(r'^\[\^([^\]]+)\]:',s,re.M);refs=re.findall(r'\[\^([^\]]+)\](?!:)',s)
check('all footnotes used and defined once',set(defs)==set(refs) and len(defs)==len(set(defs)))
for name,key in [('sources.json','sources'),('manifest.json','outputs')]:
 mismatches=[row['path'] for row in read(HERE/name)[key] if hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()!=row['sha256']]
 check(name+' integrity',not mismatches)
 if mismatches:checks[-1]['mismatches']=mismatches
check('no formula errors',not read(HERE/'math-validation.json')['errors'] and 'MATHPLACEHOLDER' not in page and 'katex-error' not in page)
check('book-size figure layout',all(r['width_pt']==420 and r['min_label_pt']>=11 and not r['text_extent_warnings'] for r in read(HERE/'teaching-layout-validation.json')))
d=read(HERE/'figure-data.json');c=read(ROOT/'calculations/results/environment-lifecycle-default.json')
check('CPU and memory distinct',d['11-1']['rounds']*d['11-1']['tool_core_seconds_per_round']==3 and d['11-1']['resident_gib_seconds']==2*30)
check('local capacities convert from locked result',[round(x['total_local_bytes']/2**30,2) for x in c['clone_placements']]==[200.39,50.39,12.89,37.89])
check('prewarm expectation matches result',F(3,4)*1+F(1,4)*2==F(c['prewarm_budget']['expected_call_preparation_wait_exact_seconds']))
v=d['11-5'];check('shared outlet bound',close(v['all_transfer_lower_seconds'],max(v['weight_bytes']*8/v['receiver_bits_per_second'],v['weight_bytes']*v['receivers']*8/v['sender_bits_per_second'])))
check('finite verification recurrence',max(20+10,10+10,0+10)==v['stream_completion_seconds'] and 20+3*10==v['batch_completion_seconds'])
check('conditional remaining time example',sum([1]*9+[100])/10==10.9 and sum(x-10 for x in [1]*9+[100] if x>10)/sum(x>10 for x in [1]*9+[100])==90)
check('thinking cost and cache worked examples',F(10000*2+1200*10,10**6)==F(32,1000) and F(10000*2+300*10,10**6)==F(23,1000) and F(8000*25+2000*20,10**7)+9*F(8000*2+2000*20,10**7)==F(744,10000))
x=d['11-7'];check('routing curve independent formula',all(close(y,(.043-.0342*h)/.98) for h,y in zip(x['h'],x['cost_B'])) and close(x['cost_crossover'],10879/13680) and close(x['joint_target_hit'],45/49))
check('list prices reproduce thinking, cache and retry costs',F(2500*2+500*10,10**6)==F('.010') and F(1500*2+300*10,10**6)==F('.006') and F(3000*5+600*25,10**6)==F('.030') and (1000*1+19000*F(1,10)+2000*5)/F(10**6)==F('.0129') and (1000*2+19000*F(1,5)+300*10)/F(10**6)==F('.0088'))
prob=[F(4,5),F(9,125),F(147,3125),F(3,3125),F(49,625),F(1,625)];cost=list(map(F,['.010','.016','.046','.046','.040','.040']));tm=[10,14,22,22,18,18];success=[1,1,1,0,1,0]
rs=read(ROOT/'calculations/results/retry-paths-book.json')['summary'];total=sum(p*c for p,c in zip(prob,cost));pq=sum(p for p,q in zip(prob,success) if q);pd=sum(p for p,q,t in zip(prob,success,tm) if q and t<=20)
check('retry tree independent enumeration',sum(prob)==1 and total==F(rs['expected_resources_per_submission']['cost']) and pq==F(rs['success_probability_exact']) and pd==F(rs['quality_and_deadline_probability_exact']))
check('retry figure includes failures and late success',close(sum(d['11-8']['contributions'].values()),float(total)) and close(d['11-8']['contributions']['失败路径'],float(prob[3]*cost[3]+prob[5]*cost[5])))
check('resource moments match teaching table',F(rs['expected_resources_per_submission']['cpu_seconds'])==F('3.376') and F(rs['expected_resources_per_submission']['resident_byte_seconds'])/2**30==F('23.008'))
check('purchase assumptions and audit source retained','OPTIMIZATION-AUDIT.md' in s and '逐层固定开销和周期全量重建为给定输入' in s)
check('residency comparison',2*9==18 and 2*(1+1)==4 and 18-4==14)
check('placement completion comparison',[12+20,4+20,1+32]==[32,24,33])
check('serial RL speedup',close(85/65,17/13) and close(85/45,17/9))
check('preparation saturation and extra residency',[.75*max(2-L,0)+.25*2 for L in [0,1,2,3]]==[2,1.25,.5,.5] and .75*2*1==1.5)
check('new retry bars from exact results',all(close(a,b) for a,b in zip(d['11-8']['policy_costs'],[.01/.8,float(total/pq),float(total/pd)])))
check('same trajectory expansion comparison',27+3/2==28.5 and 27/2+3==16.5)
design=read(HERE/'platform-design.json'); rows=design['options']
check('event sweep resource integrals',[(F(r['cpu_core_seconds']),F(r['memory_gib_seconds']),F(r['model_slot_seconds'])) for r in rows]==[(3,60,27),(F('3.3'),18,27),(3,42,18),(F('3.3'),18,18)])
check('steady schedule peaks agree with demand rates',all([F(x) for x in r['peak_cpu_memory_slots']]==[10*F(r[k]) for k in ['cpu_core_seconds','memory_gib_seconds','model_slot_seconds']] for r in rows))
check('four design costs', [F(r['submission_cost']) for r in rows]==list(map(F,['.006677625','.006492825','.0087185','.0086147'])))
check('model call time from 4xB200 V4-Flash estimate',[round(v,1) for v in design['model_service']['exact_call_seconds'].values()]==[9.0,6.0] and [r['call_seconds'] for r in rows[::2]]==[9,6])
check('fast service needs 12 replicas; resident fast exceeds m5d.metal memory',rows[3]['model_replicas_needed']==12 and rows[1]['model_replicas_needed']==9 and not rows[2]['tool_host_within_capacity'] and rows[3]['tool_host_within_capacity'])
check('deadline excludes ordinary service', [r['cost_per_on_time_quality'] is None for r in rows]==[True,True,False,False])
feasible=[r for r in rows if r['tool_host_within_capacity'] and F(r['on_time_quality_probability'])>=F('.95')]
check('chosen feasible minimum cost',min(feasible,key=lambda r:F(r['submission_cost']))['environment']=='jit')
g=F(design['inter_call_gap_cost_crossover_seconds'])
check('environment policy crossover',g==F(97,45) and 2*g*F('.0000045')==F('.0000194') and 2*2*F('.0000045')<F('.0000194')<2*6*F('.0000045'))
check('phase precedence and preparation overlap',all(p['model'][1]==p['tool'][0] and (p['prepare'] is None or p['model'][0]<=p['prepare'][0]<p['prepare'][1]==p['tool'][0]) for r in rows for p in r['phases']))
check('resource comparison uses task demand',d['capacity']['demand_9']==[30,270,600] and d['capacity']['demand_12']==[30,360,780])
check('page figure matches locked footprints',d['pages']['local_mib']==[round(x['total_local_bytes']/100/2**20) for x in c['clone_placements']])
check('pause and rebuild areas',d['pause']['paused_gib_seconds']==2*(2*4+1)==d['pause']['resident_gib_seconds'] and d['residency']['gib_seconds']==[2*30,3*2*3])
pu=d['purchase'];check('reserved versus on-demand B200 crossover',close(pu['fixed'],4*720*6.79) and close(pu['api_per_task'],.0081) and close(pu['capacity'],3072000) and close(pu['crossover']/pu['capacity'],6.79/8.64))
q=d['queue'];check('queue figure represents same work and different wait',sum(q['service_seconds'])==10 and sum(t-a for t,a in zip(q['start'],q['arrival_even']))==0 and sum(t-a for t,a in zip(q['start'],q['arrival_burst']))/10==4.5)
check('RL stage lengths match totals',[sum(r) for r in d['rl-stages']['stage_seconds']]==[85,65])
check('thinking cost stacks',all(close(sum(r),v) for r,v in zip(d['thinking']['cost_parts'],[.032,.023])))
check('retry diagram matches independent tree',list(map(F,d['retry-tree']['terminal_probabilities']))==prob and d['retry-tree']['terminal_seconds']==tm)
check('final timeline matches design',[r['duration_seconds'] for r in rows[::2]]==d['decision']['task_seconds'])
result={'passed':all(x['passed'] for x in checks),'checks':checks,'missing_links':missing,'scope':'Chapter 11; no new cloud/GPU measurement, no whole-book completion claim.'};(HERE/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'checks':len(checks),'failures':[x for x in checks if not x['passed']]},ensure_ascii=False,indent=2));raise SystemExit(0 if result['passed'] else 1)
