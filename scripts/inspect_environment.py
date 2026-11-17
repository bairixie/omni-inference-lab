"""Check installed metadata and source resolution without importing inference packages."""
import argparse
import ast
import hashlib
import importlib.metadata
from importlib.machinery import PathFinder
import json
import os
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=os.environ.get('OMNI_WORKSPACE'))
    args = parser.parse_args()
    if args.workspace is None:
        parser.error('Set OMNI_WORKSPACE or provide --workspace')
    root = Path(__file__).resolve().parents[1]
    base = root / 'experiments/minicpmo_a6000_asr'
    expected = json.loads((base / 'configs/environment.json').read_text())
    provenance = json.loads((base / 'manifests/provenance.json').read_text())
    workspace = Path(args.workspace).resolve()
    source = workspace / provenance['research_run_relative_path'] / 'phase3/source'
    paths = [str(source), str(root / 'instrumentation'), str(root / 'scripts/runtime')] + sys.path
    resolved = {}
    for name in ['sglang_omni', 'p1_observe', 'sglang_bench_factories', 'sglang', 'torch', 'transformers']:
        spec = PathFinder.find_spec(name, paths)
        assert spec is not None and spec.origin, name
        resolved[name] = spec.origin.replace(str(root), '${REPOSITORY}').replace(str(workspace), '${OMNI_WORKSPACE}')
    assert resolved['sglang_omni'].startswith('${OMNI_WORKSPACE}/' + provenance['research_run_relative_path'])
    versions = {name: importlib.metadata.version(name) for name in ['sglang', 'torch', 'transformers']}
    for name, value in versions.items():
        recorded = expected['package_versions'][name]
        assert value == (recorded.split('+')[0] if name == 'torch' else recorded), (name, value)
    torch_path = Path(PathFinder.find_spec('torch', paths).origin).parent / 'version.py'
    torch_assignments = ast.parse(torch_path.read_text()).body
    torch_build = next(ast.literal_eval(node.value) for node in torch_assignments
                       if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '__version__' for t in node.targets))
    assert torch_build == expected['package_versions']['torch']
    processor = workspace / expected['processor_workspace_relative_path']
    assert hashlib.sha256(processor.read_bytes()).hexdigest() == expected['processor_sha256']
    patch = json.loads((root / 'patches/manifest.json').read_text())
    for item in patch['files']:
        assert hashlib.sha256((source / item['path']).read_bytes()).hexdigest() == item['measured_sha256']
    print(json.dumps({'distribution_versions': versions, 'torch_build_version': torch_build, 'resolved_sources': resolved,
                      'processor_and_modified_source_hashes': 'passed',
                      'scope': 'PathFinder resolution and metadata only; no package imports or GPU initialization'}, indent=2))


if __name__ == '__main__':
    main()
