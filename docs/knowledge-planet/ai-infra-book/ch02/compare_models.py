#!/usr/bin/env python3
"""Render tables B/C from calculations; never compute model resource demands here."""
from pathlib import Path
import hashlib,json,re
H=Path(__file__).resolve().parent;R=H.parents[1]
p=R/'calculations/results/chapter2-model-comparison.json'
d=json.loads(p.read_text());rows=d['models'];order=d['parameter_group_order']
assert len(rows)==5 and rows[0]['model_id']=='deepseek-v4.1-flash'
name=lambda x: x['model'].replace('V4.1 Flash','DeepSeek V4.1 Flash').replace('V4-Flash','DeepSeek V4-Flash')
header='| 模型 | 嵌入与输出头 | 注意力投影 | 稠密／共享 FFN | 路由专家 | Engram | 其他 |'
b=[header,'| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
for x in rows:
 values=[x['parameter_groups'][k] for k in order]
 b.append('| '+name(x)+' | '+' | '.join('$<0.001$' if 0<v<500000 else f'{v/1e9:.3f}' for v in values)+' |')
c=['| 模型 | 8K prefill（TFLOPs） | 单 token 选中路由专家的 BF16 权重（GiB） |','| --- | ---: | ---: |']
for x in rows:
 c.append(f"| {name(x)} | {x['prefill_matrix_flops']/1e12:.2f} | "+(f"{x['selected_routed_expert_bf16_bytes']/2**30:.3f}" if x['selected_routed_expert_bf16_bytes'] else '—')+' |')
md=H.parent/'02-模型架构.md';s=md.read_text()
for marker,table in [('**表 2-B',b),('**表 2-C',c)]:
 start=s.index(marker);match=re.search(r'^\|.*(?:\n\|.*)*',s[start:],re.M);a=start+match.start();z=start+match.end();s=s[:a]+'\n'.join(table)+s[z:]
md.write_text(s)
(H/'model-comparison.md').write_text(s.split('<!-- MODEL-COMPARISON:START -->')[1].split('<!-- MODEL-COMPARISON:END -->')[0].strip()+'\n')
(H/'model-comparison.json').write_text(json.dumps({**d,'source_file':str(p.relative_to(R)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest()},ensure_ascii=False,indent=2)+'\n')
print('Rendered five-model parameter and resource tables.')
