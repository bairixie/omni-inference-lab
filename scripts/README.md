# Tools

- `verify_tables.py`: standard-library-only checks of preserved external per-request tables and aggregate formulas. It reads the original workspace; no data are rewritten.
- `inspect_environment.py`: checks installed dependency metadata and import search-path resolution against archived source identities without importing inference packages.
- `verify_patches.py`: standard-library Python and Git; applies the two patches to temporary baseline blobs and compares archived hashes.
- `rebuild_audio.py`: SoundFile, NumPy and SciPy from the existing environment; reconstructs selected crops from already present source WAV files into a new external directory and verifies byte hashes. It never downloads audio.
- `draw_architecture.py`: Pillow plus the Python standard library; produces the two English schematic PNG/SVG figures from shared geometry. Mermaid sources are separately editable representations of the same topology.
- `audit_repository.py`: standard-library checks of paths, UTF-8 text, unusual characters, local Markdown links, Python syntax, file size, forbidden runtime assets, and common secret patterns. Its machine-readable output is only a check aid; English prose and rendered figure labels also receive manual review.
- `runtime/serve_sglang_bench.py` and `runtime/sglang_bench_factories.py`: exact small adapters from the original workspace. They require the frozen inference environment and patched package. The launcher starts a GPU service unless `--resolve-only` is used. They were not run as a GPU service during repository preparation. `runtime/environment.sh` parameterizes the archived activation paths with `OMNI_WORKSPACE`.

See [experiment instructions](../experiments/minicpmo_a6000_asr/README.md) for explicit commands and validation boundaries.
