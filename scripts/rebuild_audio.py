"""Reconstruct archived audio crops from local sources; no network or model calls."""
import argparse
import hashlib
import json
import os
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=os.environ.get('OMNI_WORKSPACE'))
    parser.add_argument('--output-dir', type=Path, required=True,
                        help='A new directory outside this repository')
    args = parser.parse_args()
    if args.workspace is None:
        parser.error('Set OMNI_WORKSPACE or provide --workspace')
    root = Path(__file__).resolve().parents[1]
    output = args.output_dir.resolve()
    if output == root or root in output.parents:
        parser.error('Audio must remain outside the repository')
    manifest = json.loads((root / 'experiments/minicpmo_a6000_asr/manifests/audio-sources.json').read_text())
    # Import only when reconstruction is explicitly requested.
    import soundfile as sf
    from scipy.signal import resample_poly
    recordings = {x['recording_id']: x for x in manifest['recordings']}
    audio = {}
    for key, record in recordings.items():
        source = Path(args.workspace) / record['source_workspace_relative_path']
        assert sha(source) == record['source_sha256'], source.name
        values, rate = sf.read(source, dtype='float64')
        assert rate == record['source_sample_rate_hz'] == 8000 and values.ndim == 1
        audio[key] = values
    output.mkdir(parents=True, exist_ok=False)
    checks = []
    for sample in manifest['samples']:
        values = audio[sample['recording_id']]
        crop = values[sample['source_start_sample']:sample['source_end_sample']]
        rebuilt = resample_poly(crop, 2, 1)
        assert len(rebuilt) == sample['frames']
        path = output / Path(sample['workspace_relative_path']).name
        sf.write(path, rebuilt, sample['sample_rate_hz'], subtype='PCM_16')
        actual = sha(path)
        assert actual == sample['sha256'], sample['id']
        checks.append({'sample_id': sample['id'], 'sha256': actual, 'match': True})
    (output / 'reconstruction-check.json').write_text(json.dumps(checks, indent=2) + '\n')
    print(json.dumps({'sources': len(recordings), 'crops': len(checks),
                      'byte_hashes': 'passed', 'network_requests': 0, 'model_requests': 0}))


if __name__ == '__main__':
    main()
