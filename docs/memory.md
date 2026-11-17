# Memory and KV lifecycle

## What a memory number means

State the owner, device, sampling boundary, unit, and lifetime before comparing memory values. A GPU driver reports process-wide resident memory. PyTorch reports allocated tensor memory and caching-allocator reservations within a process. A model scheduler reports its own KV allocator. These measurements overlap and cannot simply be added.

| Memory class | What is retained and who owns it | Allocation, reuse and release | Observation limit |
|---|---|---|---|
| Weights | Model parameters in pipeline and speech processes, mainly GPU | Loaded at startup; persist until model/process teardown | Check component tensors or loaded state; driver totals also include other allocations |
| Thinker KV | Attention keys/values for language sequence positions | Pool allocated at startup; slots assigned during prefill/decode; returned or retained as reusable prefix rows | Pool capacity, free slots, request allocation lengths, and unique tensor storage can be read separately |
| Talker KV | Attention state for speech codec generation | Separate allocator and pool; can remain reserved when no speech request runs | Do not count unused speech capacity as active A1 work |
| Prefix reuse | Reusable prompt attention rows and tree metadata | Can keep or share slots in the existing KV pool; eviction returns reusable capacity | Count slot ownership once; tree metadata is a different allocation |
| Encoder cache | Encoded media embeddings | Stage-owned entries keyed by media; CPU/GPU placement and eviction policy matter | Output bytes differ from raw waveform and preprocessing storage |
| Reference-voice cache | Reusable reference conditioning for speech synthesis | Depends on speech task and reference reuse policy | Not part of text-output transcription; may derive from the same source as other caches |
| Temporary activations/workspaces | Intermediate tensors and operator scratch space | Allocated/reused during execution; allocator can retain freed blocks | Process peak minus weights is not an exact temporary-memory measurement |
| CUDA Graph storage | Captured graph resources and stable buffers | Usually retained after capture for replay | Can overlap storage categories in allocator reports; graph batch padding differs from real request count |
| Communication/runtime buffers | Payload transport, staging, CUDA context and library state | Process or connection lifetime; sometimes reused | Driver usage includes memory outside PyTorch accounting |

## Pool capacity versus active allocation

A **slot** is the allocator's unit for token positions; its relationship to bytes depends on layers, key/value heads, head dimension, precision, and page size. For the frozen Thinker, page size is one token. The observer reads `allocator.size`, `available_size()`, deferred free groups, and prefix evictable/protected sizes. `size - available_size()` is unavailable pool capacity at that sampling boundary. It must not be called live request state in a configuration where retained prefixes or deferred frees also occupy it.

The per-request `req.kv.kv_allocated_len` and `kv_committed_len` are allocator/request-state counters, not a value inferred from output text. For an ordinary fully completed autoregressive sequence without retraction or sharing, the last sampled occupied length can equal input positions plus generated IDs minus one: the last emitted token has not yet been fed back for another forward pass. This relationship is a consistency check. The counters, page size, pending release state, and pool readings must still be inspected.

A request release returns ownership or slots to the allocator. Prefix retention preserves reusable state. Neither event necessarily returns the underlying pool tensors to the GPU driver. Likewise, PyTorch may keep freed temporary blocks reserved for reuse. A persistent process footprint alone is not leak evidence. Leak investigation needs repeated comparable requests, quiescent snapshots, and unexplained growth after reusable state is accounted for.

## What the extracted observer can establish

The observer records request allocation lengths, global pool availability at batch boundaries, retraction counts, cache entries/hits/evictions, and process-level PyTorch counters. It deduplicates KV tensor storage by storage pointer before summing bytes. Batch records retain request membership so simultaneous global usage can be examined without adding different requests' individual peaks.

It does not provide a clean decomposition of temporary activations, library workspaces, communication allocations, and graph memory. Process peak counters are cumulative and are not reset at every request. Graph padded execution size is not captured by the logical batch count. These missing measurements remain unknown; no residual subtraction is presented as exact KV or temporary memory.

## Source and configuration

See [the observer](../instrumentation/p1_observe.py), [patch manifest](../patches/manifest.json), and the [frozen configuration](../experiments/minicpmo_a6000_asr/configs/resolved-runtime.json). Upstream stage caching is in `sglang_omni/scheduling/stage_cache.py`; request KV bookkeeping is supplied by SGLang 0.5.22. Prefix reuse and encoder-result caching are disabled in this experiment configuration. Warming the model is a separate operation and does not establish a cache hit.

Cross-startup pool sizes depend on the effective configuration and memory available during allocation. An unexplained difference remains unresolved until those inputs are accounted for. It is neither proof of a leak nor grounds for pooling capacity measurements across different startups.
