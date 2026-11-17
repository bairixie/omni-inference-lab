# Related papers

Start with the model and serving architecture. Then choose a paper that matches the limitation seen in a trace. The questions below are research ideas, not measured improvements in this repository.

## Start here

1. **[MiniCPM-o 4.5: Towards Real-Time Full-Duplex Omni-Modal Interaction](https://arxiv.org/abs/2604.27393)** — Cui et al., 2026. Explains how the model aligns incoming and outgoing streams to see, listen and speak together. Read for the component dependencies and the difference between offline answers and live interaction. Its **Omni-Flow** interaction framework is distinct from the speech decoder's Flow stage.
2. **[M*: A Modular, Extensible, Serving System for Multimodal Models](https://arxiv.org/abs/2606.12688)** — Jha et al., 2026. Represents composite models as dataflow graphs called Walk Graphs. Read for stage composition, placement and runtime coordination. Use it to ask which dependencies or resource-sharing decisions lie on a request's critical path.

## Choose by the problem

| Question from profiling | Paper and key idea | What to investigate |
| --- | --- | --- |
| Do long inputs interrupt ongoing generation? | [Sarathi-Serve](https://arxiv.org/abs/2403.02310), 2024 — chunked prefill and scheduling that avoids decode stalls. | Correlate prefill work with generation gaps. This addresses language-model scheduling, not every encoder or speech-stage queue. |
| Does KV allocation restrict batching? | [PagedAttention / vLLM](https://arxiv.org/abs/2309.06180), 2023 — allocate and share KV in blocks to reduce waste. | Separate reserved capacity, active slots, fragmentation and reuse. A large reserved pool alone is not a memory bottleneck. |
| Can repeated prompts avoid work? | [SGLang](https://arxiv.org/abs/2312.07104), 2023 — RadixAttention reuses KV for shared prefixes. | Measure real prefix reuse and avoided prefill work. Media-encoder and voice-reference caches are different mechanisms. |
| Is autoregressive decoding on the critical path? | [Fast Inference from Transformers via Speculative Decoding](https://proceedings.mlr.press/v202/leviathan23a.html), 2023 — propose tokens cheaply, then verify them with the target model. | Measure acceptance, draft/verification cost and complete-request benefit. It does not directly accelerate Flow or HiFT. |
| Would separate resources reduce stage interference? | [DistServe](https://www.usenix.org/conference/osdi24/presentation/zhong-yinmin), 2024 — place prefill and decode on different GPUs. | First establish interference, then compare separation benefits against transfer cost. This is a future multi-GPU direction, not a single-A6000 result. |
| Are weight size or weight reads limiting execution? | [AWQ](https://arxiv.org/abs/2306.00978), 2023 — activation-aware, low-bit weight quantization. | Check supported kernels, actual speed, memory savings and output quality. Smaller weights do not automatically mean lower latency. |

## Speech and model comparisons

- **[CosyVoice 2: Scalable Streaming Speech Synthesis with Large Language Models](https://arxiv.org/abs/2412.10117)** — Du et al., 2024. Explains speech-token generation and chunk-aware causal flow matching. Useful when investigating time to first audio, chunk size and synthesis work. MiniCPM-o uses a related speech design, not an unchanged standalone CosyVoice service.
- **[Qwen3-Omni Technical Report](https://arxiv.org/abs/2509.17765)** — Xu et al., 2025. Describes a Thinker-Talker MoE model and multi-codebook speech generation with a causal convolutional decoder. Useful for testing whether a finding transfers to another Omni architecture; do not assume MiniCPM-o's Flow/HiFT path is present.

For each paper, write down one applicable idea, one required condition and one experiment that could disprove its usefulness. Keep published speedups attached to their original hardware and workload.

[BibTeX references](references.bib) · [Current upstream investigations](../docs/upstream.md). Links and paper identities checked on 2026-11-17.
