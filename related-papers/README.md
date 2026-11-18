# Related papers

A reading list for **finding and explaining Omni inference bottlenecks**, then choosing an optimization. Start with the model and runtime; read the systems paper that matches the delay seen in a request trace.

**Checked on 2026-11-17.** Dates below distinguish first release from later revisions. These are linked primary papers, with BibTeX in this directory. The suggested experiments are our reading of their relevance, not results measured in this repository. An arXiv listing does not by itself establish peer review.

## Reading route

| What you need to understand | Read |
| --- | --- |
| How MiniCPM-o combines perception and speech | [MiniCPM-o 4.5](#model-and-runtime) |
| Why a multimodal model needs more than one decode loop | [M*](#model-and-runtime) |
| Text and speech requests competing on one GPU | [HorizonServe](#horizonserve) |
| A long image/video request delaying a short request | [RPS-Serve](#rps-serve) |
| Speech starts late or playback stalls | [VoxServe](#voxserve) |
| Live conversations, interruptions and next-turn KV reuse | [OmniCast](#omnicast) |
| Long streams growing KV and memory traffic | [OmniTide](#omnitide) |
| Multimodal generation spends most of its time decoding | [Uni-LaSpec](#uni-laspec) |

## Model and runtime

- **[MiniCPM-o 4.5: Towards Real-Time Full-Duplex Omni-Modal Interaction](https://arxiv.org/abs/2604.27393)** — April 2026. Explains the encoders, language backbone and speech branch, and time-aligned incoming/outgoing streams. Read to distinguish one offline answer from ongoing perception and response. Its **Omni-Flow** interaction framework is distinct from the acoustic Flow stage inside Code2Wav.
- **[M*: A Modular, Extensible, Serving System for Multimodal Models](https://arxiv.org/abs/2606.12688v2)** — June 2026, v2. Represents composite models as Walk Graphs, separating component composition from placement and execution. Use it to reason about dependencies, data transfers and which chain of work actually delays a response.
- **[vLLM-Omni Technical Report: A Unified Serving Runtime for Omni-Modality Generation](https://arxiv.org/abs/2610.09307)** — October 2026. A recent runtime comparison: an orchestrator connects specialized engines, stage replicas, data transport and session control. Useful for comparing abstractions with SGLang Omni; it is a different implementation, not evidence that either runtime is faster on an A6000.

## Recent systems work

### HorizonServe

**[HorizonServe: Coordinating Request Scheduling with GPU Sharing for Omni-Model Serving](https://arxiv.org/abs/2608.01785)** — August 2026.

- **Problem:** Text-only and speech-generating requests share an initial model stage, then take different paths. They compete for one GPU while needing different first-response deadlines.
- **Idea:** Coordinate request admission and path rotation with the GPU resources given to the shared stage when downstream generators are active.
- **Use here:** Compare each task alone with the same task in a text/speech mixture. Measure first text/audio, queue waits and overlapping GPU work. This directly matches the single-GPU research setting.
- **Boundary:** The paper's memory-activity signal is a proxy, not a direct bandwidth measurement. Its policies need stage-level integration and hardware support; they are not a ready-made MiniCPM-o setting.

### RPS-Serve

**[Rocks, Pebbles and Sand: Modality-aware Scheduling for Multimodal Large Language Model Inference](https://arxiv.org/abs/2603.26498v3)** — March 2026; v3 revised **October 29, 2026**.

- **Problem:** Expensive multimodal requests can delay light requests at the front of a shared queue.
- **Idea:** Estimate request time and memory cost, group requests by that cost, and schedule with priorities that rise as requests wait. The groups are not simply “all videos / all images / all text.”
- **Use here:** Mix short text questions with long media inputs; inspect per-class waiting and response tails, not only aggregate throughput.
- **Boundary:** The evaluation concerns multimodal understanding and includes multi-GPU setups. Extending the idea to speech output requires accounting for Talker and vocoder work too.

### VoxServe

**[VoxServe: Streaming-Centric Serving System for Speech Language Models](https://arxiv.org/abs/2602.00269v2)** — January 2026; v2 revised **October 31, 2026**.

- **Problem:** A speech-token generator and a waveform codec need different GPU resources. Maximizing token production alone does not ensure prompt, uninterrupted audio.
- **Idea:** Separate LM, background-codec and urgent execution lanes. First chunks and chunks near their playback deadlines receive urgent treatment; less urgent codec work can batch and overlap with generation.
- **Use here:** Measure time to first playable audio, gaps between chunks and playback stalls. Compare isolated component execution with co-running execution.
- **Boundary:** The revised paper studies Qwen3-TTS and GPU partitioning. MiniCPM-o's offline whole-waveform path does not expose the same chunk deadlines; a streaming path and compatible GPU/runtime support are prerequisites.

### OmniCast

**[OmniCast: Interaction-Aware Serving for Real-Time Omni-Modal LLMs](https://arxiv.org/abs/2606.22983v2)** — June 2026; v2 revised **November 1, 2026**. The earlier version was titled *LiveServe*.

- **Problem:** Generating far ahead of playback wastes work when users interrupt. Evicting session KV at the wrong time adds a reload delay to the next turn.
- **Idea:** Use playback, speech-activity and interruption signals to control generation; choose KV eviction by expected next use and preload state during user speech.
- **Use here:** For a future live workload, record generated-versus-played audio, wasted work after interruption, KV reload time and next-turn response delay.
- **Boundary:** Implemented on vLLM-Omni. Offline single-turn latency cannot validate this method; client/session signals and reusable conversation state are required.

### OmniTide

**[OmniTide: Co-Designing Algorithms and Systems for Efficient On-Device Omni-LLM Streaming](https://arxiv.org/abs/2609.34653v2)** — September 2026, v2.

- **Problem:** Continuous multimodal input grows attention history; discarding logical entries does not necessarily produce compact physical storage.
- **Idea:** Retain important multimodal units with OmniPick, then organize and compact surviving KV with OmniPage.
- **Use here:** Separate useful retained history, occupied physical KV storage and compaction cost as a session grows. This is especially relevant to later memory-constrained device experiments.
- **Boundary:** Eviction changes the available context and can affect answers. Evaluate long-session quality as well as latency; do not infer a benefit when KV capacity and attention cost are already small.

### Uni-LaSpec

**[Seeing What Matters, Verifying What Pays: Load-Adaptive Speculative Decoding for Vision-Language Models](https://arxiv.org/abs/2611.01617v2)** — November 2026; v2 revised **November 6, 2026**.

- **Problem:** A small draft model needs useful visual evidence, but processing every visual token is expensive. The benefit of verifying extra guesses also changes with serving load.
- **Idea:** Select a small set of visual features for the drafter and adapt the verification structure to available GPU capacity.
- **Use here:** If Thinker decoding is on the critical path, compare draft acceptance, draft/verification cost and complete-request latency across concurrency levels.
- **Boundary:** This is VLM text generation, not a demonstrated MiniCPM-o speech optimization. It needs a compatible trained drafter and verification path; it does not directly speed up Flow or HiFT.

## Input processing, caching and placement

| Paper | Bottleneck and method | Useful question and scope |
| --- | --- | --- |
| **[Enabling Disaggregated Multi-Stage MLLM Inference via GPU-Internal Scheduling and Resource Sharing](https://arxiv.org/abs/2512.17574)** — December 2025 | FlashCodec targets video decoding; UnifiedServe separates stage execution logically while sharing physical GPU resources. | Does video decoding starve the encoder, or do encoders interfere with language generation? FlashCodec's multi-GPU decoding design is not directly reproducible on one A6000. |
| **[ElasticMM: Efficient Multimodal LLMs Serving with Elastic Multimodal Parallelism](https://arxiv.org/abs/2507.10069v3)** — July 2025; v3 November 2025 | Modality groups, elastic stage parallelism, multimodal prefix reuse and nonblocking encoding. | Does repeated media really avoid work, and which stage needs more capacity? Separate cache-hit savings from resource-placement savings. Cluster elasticity is a later direction, not a prerequisite for local profiling. |

## Supporting foundations

Use these when a specific mechanism needs deeper study.

| Mechanism | Paper | What to take from it |
| --- | --- | --- |
| Prompt/decode interference | [Sarathi-Serve](https://arxiv.org/abs/2403.02310), 2024 | Chunk long prefills to reduce disruption to ongoing decoding. |
| KV allocation | [PagedAttention / vLLM](https://arxiv.org/abs/2309.06180), 2023 | Allocate and share attention state in blocks; distinguish fragmentation from active demand. |
| Prefix reuse | [SGLang / RadixAttention](https://arxiv.org/abs/2312.07104), 2023 preprint | Reuse shared prompt KV; encoder features and voice-reference caches are separate mechanisms. |
| Speculative decoding | [Leviathan et al.](https://proceedings.mlr.press/v202/leviathan23a.html), 2023 | Propose tokens cheaply and verify with the target; acceptance must outweigh extra work. |
| Separate prefill/decode resources | [DistServe](https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin), 2024 | Trade stage isolation against transfer cost and available hardware. |
| Weight compression | [AWQ](https://arxiv.org/abs/2306.00978), 2023 preprint | Reduce weight storage and reads; check supported kernels, speed and quality. |

For speech architecture, read **[CosyVoice 2](https://arxiv.org/abs/2412.10117)** (2024), particularly speech codes and chunk-aware flow matching. For a second Omni model, read **[Qwen3-Omni](https://arxiv.org/abs/2509.17765)** (2025): its multi-codebook speech generation and causal convolutional waveform decoder differ from MiniCPM-o's Flow/HiFT path.

## Turn a paper into a test

Write down **the observed delay → the proposed cause → one controlled change → the metric and quality check**. Include a result that would disprove the hypothesis. Check [upstream work](../docs/upstream.md) before implementing a mechanism that may already exist.

Published speedups belong to their original model, workload, hardware and software revision. This list supplies candidate explanations and methods; it does not establish a bottleneck in the current deployment.

[BibTeX references](references.bib) · [Profiling guide](../docs/profiling.md).
