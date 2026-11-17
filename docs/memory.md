# Memory and caches

GPU memory holds more than model weights. To understand a limit, ask **what is stored, who owns it, and when it can be reused or released**.

| Memory | What it stores | Typical lifetime |
| --- | --- | --- |
| Model weights | Learned parameters for encoders, the language model and speech components | While the components are loaded |
| Thinker / Talker KV | Attention keys and values for previously processed positions, so generation can reuse earlier work | During a sequence; some state may remain cached |
| Prefix cache | Reusable attention state for a shared prompt prefix | Until eviction; it can occupy the **same KV pool**, not a second copy |
| Encoder cache | Encoded image or audio representations | Until eviction; benefit depends on repeated media |
| Voice-reference cache | Conditioning derived from a reference voice | Reused across compatible speech requests |
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
