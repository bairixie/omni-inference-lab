"""Check the frozen patch stack without modifying an upstream checkout."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', type=Path, required=True,
                        help='Existing Git checkout containing the pinned baseline')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'patches/manifest.json').read_text())
    with tempfile.TemporaryDirectory(prefix='omni-patch-check-') as directory:
        target = Path(directory)
        for record in manifest['files']:
            data = subprocess.check_output([
                'git', '-C', str(args.upstream), 'show',
                manifest['base_commit'] + ':' + record['path']])
            assert hashlib.sha256(data).hexdigest() == record['base_sha256']
            path = target / record['path']
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        for index, name in enumerate(manifest['apply_order']):
            patch = root / 'patches' / name
            for flag in ['--check', None]:
                cmd = ['git', 'apply'] + ([flag] if flag else []) + [str(patch)]
                subprocess.run(cmd, cwd=target, check=True, capture_output=True)
            key = 'corrected_sha256' if index == 0 else 'measured_sha256'
            for record in manifest['files']:
                data = (target / record['path']).read_bytes()
                assert hashlib.sha256(data).hexdigest() == record[key], record['path']
                ast.parse(data, filename=record['path'])
        for name in reversed(manifest['apply_order']):
            subprocess.run(['git', 'apply', '--reverse', str(root / 'patches' / name)],
                           cwd=target, check=True, capture_output=True)
        for record in manifest['files']:
            assert hashlib.sha256((target / record['path']).read_bytes()).hexdigest() == record['base_sha256']
    observer = root / manifest['observer_module']
    assert hashlib.sha256(observer.read_bytes()).hexdigest() == manifest['observer_sha256']
    print(json.dumps({'patches': len(manifest['apply_order']), 'package_files': len(manifest['files']),
                      'apply_hash_syntax_reverse': 'passed', 'observer_identity': 'passed',
                      'gpu_execution': False}))


if __name__ == '__main__':
    main()
