# MiniCPM-o audio transcription: frozen experiment support

This directory preserves the setup and reconstruction tools for an existing A6000 audio-to-text transcription study. It does not promote baseline observations or unconfirmed anomalies to bottleneck findings. Complete investigation records and per-request results remain in the original workspace. Their relative paths and SHA-256 values are in [manifests/provenance.json](manifests/provenance.json).

## Frozen identity and controls

Use Omni `30da209c2330eaf50b1838fc82a2975c1ddc78f4` plus the two archived patches, SGLang 0.5.22, PyTorch 2.14.1+cu130, Transformers 5.19.0, and MiniCPM-o snapshot `eb4141de24550a3a1a4082f718be58f46b761728`. The imported scheduler was the isolated package recorded in the environment manifest, not merely the installed wheel or the original checkout's HEAD.

The deployment is speech-capable, on one RTX A6000, but the A1 request asks for text only. Thinker and Talker use BF16; Code2Wav is configured FP32 and is not executed for this task. Triton attention, existing graph settings, process placement, CPU quota 16 and OMP threads 8 are preserved. Prefix reuse and encoder output caching are off. The voice reference is not applicable. Temperature 0, seed 42, repetition penalty 1 and output cap 512 are fixed. See [request.json](configs/request.json), [environment.json](configs/environment.json), [launch-arguments.json](configs/launch-arguments.json), and [resolved-runtime.json](configs/resolved-runtime.json).

The resolved configuration is a labeled projection of the archived full configuration, with unset fields and unused Flow graph shape lists omitted. It is not a complete environment lock. No current upstream default is substituted for the recorded flags.

## Input provenance and reconstruction

The [audio manifest](manifests/audio-sources.json) identifies three small Open Speech Repository recordings, exact hashes, URLs, source attribution/usage statements, source-sample cuts, and resulting WAV hashes. They are published human sentence-list recordings. Crops are continuous prefixes without looping or inserted silence; production editing of the original recording is unknown. Nominal length labels do not replace exact durations and sample counts.

Published Harvard sentence lists provide independent words. List identification used earlier model output to select the corresponding unchanged published list; crop alignment used pauses and sentence order. This is limited reference-consistency checking, not independently certified word timing or formal ASR quality. Raw transcripts and their original reference records remain in the workspace. A successful request, `stop`, or absence of an output-cap hit does not certify completeness or accuracy.

The reconstruction script requires existing source WAV files and writes only to a new directory outside this repository. It does not download a dataset, modify the source audio, or call the model.

## Offline commands checked during R1

Run from the repository root. Set the workspace to the existing run area; the example is intentionally not tied to a particular account.

```bash
export OMNI_WORKSPACE=/path/to/existing/omni
python3 scripts/verify_tables.py --workspace "$OMNI_WORKSPACE"
python3 scripts/verify_patches.py --upstream "$OMNI_WORKSPACE/external/sglang-omni"
python3 scripts/audit_repository.py
"$OMNI_WORKSPACE/sglang-env/bin/python" scripts/inspect_environment.py --workspace "$OMNI_WORKSPACE"
```

The table verifier reads the preserved `deliverables/meeting_2026-11-19/data` files, including request/window tables, paired length records and boundary output-ID records. It recomputes pooled medians, throughput with the full fill/drain window, actual in-flight averages, stage summaries and call-weighted batch statistics. An alternative is `--data-dir /path/to/extracted/bundle/data`. The original bundle need not be placed inside this repository. No summary or raw table is rewritten.

The existing environment supplies the audio and figure dependencies; do not reinstall it:

```bash
"$OMNI_WORKSPACE/sglang-env/bin/python" scripts/rebuild_audio.py   --workspace "$OMNI_WORKSPACE" --output-dir /path/to/new/external/crop-check
"$OMNI_WORKSPACE/sglang-env/bin/python" scripts/draw_architecture.py
```

R1 performed these operations using the actual existing workspace, checked crop byte hashes, and inspected both PNG figures. The first command refuses an existing output directory. Figure generation writes the schematic assets in `docs/figures`; it produces no performance plot or synthetic trace.

## Historical runtime command, adapted paths: not executed in R1

The following arguments were checked against the archived launch and the extracted launcher. This is a reproduction recipe, not a claim that a new GPU run was validated after extraction. Use it only inside a separately authorized valid allocation with the same resources. Inherit `SLURM_JOB_ID` and `CUDA_VISIBLE_DEVICES` from that allocation; do not fabricate their values or reset its deadline.

```bash
export OMNI_WORKSPACE=/path/to/existing/omni
export MODEL_PATH=/path/to/existing/frozen/model/snapshot
export OMNI_SOURCE="$OMNI_WORKSPACE/results/meeting_2026-11-19/p0_20261116T182747-0500/phase3/source"
export RUN_OUTPUT=/path/to/new/run-output
export IPC_PATH=/path/to/unique/ipc-directory
export P3_RUN_ID=unique-run-identifier
export SGLANG_TEST_RETRACT=0
source scripts/runtime/environment.sh
export PYTHONPATH="$OMNI_SOURCE:$PWD/instrumentation:$PWD/scripts/runtime"
"$OMNI_WORKSPACE/sglang-env/bin/python" scripts/runtime/serve_sglang_bench.py   --model-path "$MODEL_PATH" --host 127.0.0.1 --port 18001   --thinker.engine.attention_backend triton --thinker.engine.dtype bfloat16   --thinker.engine.mem_fraction_static 0.60 --thinker.engine.max_running_requests 8   --thinker.engine.cuda_graph_max_bs 8 --no-cache   --talker.engine.attention_backend triton --talker.engine.mem_fraction_static 0.15   --talker.engine.max_running_requests 4 --talker.engine.cuda_graph_max_bs 4   --code2wav.factory.dtype float32 --code2wav.factory.enable_dit_torch_compile false   --code2wav.factory.enable_hift_torch_compile false   --code2wav.factory.enable_flow_cuda_graph false   --config-output "$RUN_OUTPUT/resolved_config.json" --endpoints.base_path "$IPC_PATH"
```

`environment.sh` is the small archived activation recipe with the workspace root parameterized. Runtime adapters and observation code are extracted unchanged. The package itself remains in the original isolated source copy; alternatively reconstruct that exact package in a new location using the patch manifest. Do not apply patches to the original working checkout. The legacy observer name `p1_observe` is intentional.

This command starts the service, not the complete matrix. The historical closed-loop driver is `phase3/scripts/run_p3.py` under the research run in the provenance manifest. Its original launch, resource checks, timeout rules, request construction and gate logic are retained there. It is an archival, workspace-specific driver and is not presented as a portable command for another account. R1 does not rerun it or automatically continue to another research stage. Future benchmarking needs a fresh output location, verified imports, correctness/quality checks, cache verification, and a new same-version baseline.

## Validation boundaries

Offline success establishes file integrity, patch reconstruction, syntax, table arithmetic and crop identity. It does not validate live GPU import behavior after relocation, service startup, concurrency safety in a new deployment, performance, speech quality, or formal ASR accuracy. The old live runtime identity and request-level observation validation remain separately documented in the preserved research record.
