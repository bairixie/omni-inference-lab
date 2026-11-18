# Memory and caches

GPU memory holds more than model weights. To understand a limit, ask **what is stored, who owns it, and when it can be reused or released**.

| Memory | What it stores | Typical lifetime |
| --- | --- | --- |
| Model weights | Learned parameters on each component's assigned device; GPU for the main neural stages | While the components are loaded |
| Thinker / Talker KV | Separate GPU attention state owned by each autoregressive engine | During a sequence; some state may remain cached |
| Prefix cache | Reusable attention state for a matching prompt prefix, managed by its engine | Until eviction; it can occupy the **same KV pool**, not a second copy |
| Encoder cache | Image/audio features; each encoder executor keeps a CPU copy in the pinned implementation | Until eviction; benefit depends on repeated media |
| Voice-reference cache | Code2Wav's prepared prompt codes, speaker embedding and acoustic features on its device | Reused across compatible speech requests; bounded cache with request reservations |
| Temporary memory | Intermediate tensors and operator workspaces | During execution; the allocator may retain freed blocks |
| Graph and runtime buffers | Storage for graph replay, transfers and runtime state | Often retained across requests |

## Reserved does not mean busy

A service may reserve a large KV pool at startup and use only part of it for current requests. Finishing a request can return slots to that pool without reducing the memory reported by `nvidia-smi`.

Record these separately:

- **Pool capacity:** the total available KV space.
- **Active use:** space assigned to current requests.
- **Reusable state:** cached entries that can be evicted or shared.
- **Process memory:** the broader footprint, including weights and runtime storage.

These measurements overlap; do not add them together. Stable reserved memory is not evidence of a leak. Spare KV capacity also says nothing by itself about memory-bandwidth pressure.

For a suspected memory limit, measure concurrent active requests, input/output lengths, cache state and allocation failures under the same configuration. See [PagedAttention](https://arxiv.org/abs/2309.06180) for KV allocation and [SGLang](https://arxiv.org/abs/2312.07104) for prefix reuse; inspect the actual runtime for implementation details.

## Where media enters KV

An encoder output is a feature tensor. When those features occupy positions in the Thinker's input, the Thinker's attention layers create KV for those positions. The encoded tensor and the resulting KV are different objects and avoid different work when reused. Audio duration or video frame count therefore does not directly equal KV usage: preprocessing, slicing, pooling and the model's input layout matter.

The Talker has its own attention layers and sequence, so its KV cannot simply alias the Thinker's KV. In the offline path, Flow/HiFT have intermediate and graph buffers rather than a Thinker-style growing language-history KV pool. A live session can retain additional state across chunks; inspect its separate implementation before applying the offline accounting.

## Source map

The concrete placement above was checked against **SGLang Omni commit `4d47186` on 2026-11-17**. It describes that upstream implementation, not every installed version. Record the resolved configuration and actual import paths when measuring a deployment.

| Fact to verify | Pinned source |
| --- | --- |
| Process grouping and device placement | [`config.py`: `speech_stages`](https://github.com/sgl-project/sglang-omni/blob/4d47186d9517d36f2c69ae44b9fbadb7bca140b4/sglang_omni/models/minicpm_o/config.py#L186) |
| Separate autoregressive schedulers; encoder caches use `cache_device="cpu"` | [`stages.py`](https://github.com/sgl-project/sglang-omni/blob/4d47186d9517d36f2c69ae44b9fbadb7bca140b4/sglang_omni/models/minicpm_o/stages.py) |
| Encoder-cache storage, size limits and eviction | [`stage_cache.py`](https://github.com/sgl-project/sglang-omni/blob/4d47186d9517d36f2c69ae44b9fbadb7bca140b4/sglang_omni/scheduling/stage_cache.py) |
| Reference-cache reservations and reuse | [`code2wav.py`](https://github.com/sgl-project/sglang-omni/blob/4d47186d9517d36f2c69ae44b9fbadb7bca140b4/sglang_omni/models/minicpm_o/components/code2wav.py) |
| Reference tensors constructed on the vocoder's device | [`vocoder.py`: `prepare_prompt`](https://github.com/sgl-project/sglang-omni/blob/4d47186d9517d36f2c69ae44b9fbadb7bca140b4/sglang_omni/models/minicpm_o/components/token2wav/vocoder.py#L249) |

CPU-cached encoder features still need to reach the consuming GPU. Cache hits may save encoder computation while retaining transfer or synchronization costs. Measure both before calling a cache beneficial.
