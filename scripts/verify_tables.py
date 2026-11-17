"""Verify archived small tables without importing inference libraries or modifying data."""
from pathlib import Path
import csv,json,statistics,collections
import argparse, os
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--data-dir', type=Path, help='Directory containing the preserved review bundle tables')
parser.add_argument('--workspace', type=Path, default=os.environ.get('OMNI_WORKSPACE'))
args=parser.parse_args()
if args.data_dir is not None:
    p=args.data_dir.parent
    data_dir=args.data_dir
elif args.workspace is not None:
    data_dir=Path(args.workspace)/'deliverables/meeting_2026-11-19/data'
    p=data_dir.parent
else:
    parser.error('Set OMNI_WORKSPACE or provide --workspace or --data-dir')
read=lambda f:list(csv.DictReader((data_dir/f).open()));med=statistics.median
R=read('p3_request_metrics.csv');W=read('p3_run_summary.csv');K=read('p3_key_results.csv');B=read('p3_batch_summary.csv');S=read('p3_stage_summary.csv');L=read('p2_length_metrics.csv');pairs=read('p2_pair_recheck.csv')
assert len(R)==196 and len(L)==62
for k in K:
 c=k['C'];rr=[r for r in R if r['category']=='performance' and r['client_C']==c];ww=[w for w in W if w['category']=='performance' and w['client_C']==c];assert len(rr)==48
 for col,key in [('A_send_to_parse_ms','A_p50_ms_pooled'),('B_admission_to_first_text_ms','B_p50_ms_pooled'),('C_first_to_last_text_ms','C_p50_ms_pooled')]:assert abs(med(float(r[col]) for r in rr)-float(k[key]))<1e-8
 assert abs(48/sum(float(w['window_s']) for w in ww)-float(k['qps_total_success_over_total_window']))<1e-10
 bb=[b for b in B if b['scope']=='pooled_performance' and b['client_C']==c and b['mode']=='DECODE'];assert abs(sum(int(b['logical_batch_size'])*int(b['batch_calls']) for b in bb)/sum(int(b['batch_calls']) for b in bb)-float(k['decode_batch_mean_per_call']))<1e-10
for w in W:
 rr=[r for r in R if r['window_id']==w['window_id']];duration=(max(int(r['end_monotonic_ns']) for r in rr)-min(int(r['start_monotonic_ns']) for r in rr))/1e9
 assert abs(duration-float(w['window_s']))<1e-8
 assert abs(sum((int(r['end_monotonic_ns'])-int(r['start_monotonic_ns']))/1e9 for r in rr)/duration-float(w['average_inflight']))<1e-10
 assert abs(sum(r['success_stop_nonempty']=='True' for r in rr)/duration-float(w['requests_per_s']))<1e-10
for s in S:
 rr=[r for r in R if r['category']=='performance' and r['client_C']==s['client_C']] if s['scope']=='pooled_performance' else [r for r in R if r['window_id']==s['window_id']]
 for k,v in s.items():
  if k.endswith('_p50'):assert abs(med(float(r[k[:-4]]) for r in rr)-float(v))<1e-8
lookup={x['request_id']:x for x in L}
for x in pairs:
 a=lookup[x['short_id']];b=lookup[x['long_id']];ratio=(float(b['C_first_to_last_text_ms'])-float(a['C_first_to_last_text_ms']))/(float(b['A_send_to_parse_ms'])-float(a['A_send_to_parse_ms']));assert abs(ratio-float(x['ratio_delta_C_over_A']))<1e-10
q=json.loads((data_dir/'p2_boundary_outputs.json').read_text())['requests'];assert len(q)==6
assert all(x['output_tokens']==len(x['output_ids'])==71 and x['output_ids']==q[0]['output_ids'] and x['finish_reason']=='stop' and x['max_tokens']==512 for x in q)
assert sum(x['category']=='performance' for x in R)==144 and sum(x['success_stop_nonempty']=='False' for x in R)==1
assert sum(x['category'] in {'screen', 'order_check', 'boundary_screen'} for x in L)==42
print(json.dumps({'pooled_quantiles_throughput_stages_batches_inflight':'passed','paired_time_differences':'passed','boundary_output_identity':'passed','request_category_counts':'passed','new_model_requests':0}))
