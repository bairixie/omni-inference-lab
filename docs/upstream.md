# Upstream investigations worth reading

These are SGLang Omni authors' measurements, not results from this repository. Use them to learn the method and avoid repeating solved work. Check the linked discussion, follow-up changes and your actual code before treating a reported limitation as current.

| Investigation | Why it is useful | What to check locally |
| --- | --- | --- |
| [Video + spoken question → text + speech (#2580)](https://github.com/sgl-project/sglang-omni/issues/2580) | Connects preprocessing time, queue growth and GPU activity to complete-service performance. | Whether the same input path and preprocessing limits still exist in the tested version. |
| [Preprocessing concurrency (#2316)](https://github.com/sgl-project/sglang-omni/pull/2316) and [audio encoder batching (#2320)](https://github.com/sgl-project/sglang-omni/pull/2320) | Shows why preparing requests concurrently and executing them as a batch are separate problems. | Actual worker counts, request arrival at the encoder, batch membership and input padding. |
| [Full-duplex profiling (#3910)](https://github.com/sgl-project/sglang-omni/issues/3910) | Studies streaming interaction and waits within a multi-component service. | Session deadlines and CPU/GPU dependencies; ordinary offline requests use a different timing contract. |
| [Reference and encoder caches (#3034)](https://github.com/sgl-project/sglang-omni/issues/3034) | Examines how reference reuse and cache configuration affect speech-serving work. | Real hit rates, avoided work and remaining preparation/transfer costs. |

An open issue may already have active work; a merged change may still leave other workloads untested. Repeating a published result on another GPU is useful validation, but a new finding needs a clearly different question or mechanism.
