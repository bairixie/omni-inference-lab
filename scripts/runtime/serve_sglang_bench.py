#!/usr/bin/env python3
"""Launch an isolated benchmark pipeline with optional encoder cache bypass."""
import argparse
import json
import os
from pathlib import Path

from sglang_omni.config.manager import ConfigManager
from sglang_omni.serve.launcher import launch_server


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-path',required=True)
    parser.add_argument('--text-only',action='store_true')
    parser.add_argument('--no-cache',action='store_true')
    parser.add_argument('--host',default='127.0.0.1')
    parser.add_argument('--port',type=int,default=18000)
    parser.add_argument('--config-output',type=Path,default=Path('docs/performance/sglang-active-config.json'))
    parser.add_argument('--resolve-only',action='store_true')
    args,overrides=parser.parse_known_args()
    assert os.environ.get('SLURM_JOB_ID') and os.environ.get('CUDA_VISIBLE_DEVICES')
    manager=ConfigManager.from_model_path(args.model_path,variant='text' if args.text_only else None)
    if args.no_cache: overrides+=['--thinker.engine.disable_radix_cache','true']
    config=manager.merge_config(manager.parse_extra_args(overrides))
    if args.no_cache:
        for stage in config.stages:
            if stage.name in ['image_encoder','audio_encoder']:
                stage.factory_path=f'sglang_bench_factories.create_{stage.name}_executor'
    args.config_output.parent.mkdir(parents=True,exist_ok=True)
    args.config_output.write_text(config.model_dump_json(indent=2))
    print(json.dumps(dict(pid=os.getpid(),no_cache=args.no_cache,slurm_job_id=os.environ['SLURM_JOB_ID'],config=str(args.config_output))),flush=True)
    if not args.resolve_only:
        launch_server(config,host=args.host,port=args.port,model_name='MiniCPM-o-4_5')

if __name__=='__main__': main()
