# How to investigate a bottleneck

Start with a user-visible problem: a slow complete response, a long wait for speech to start, or too few requests served per second.

## Follow the request

1. **Define the workload.** Record input, task, output and offline or live mode. Pin the model, code, hardware, generation settings and cache policy.
2. **Measure the complete path.** Follow preparation, queues, encoders, generation, speech synthesis and response delivery. Record actual input and output sizes.
3. **Change the load.** Compare single requests, increasing concurrency and mixed request types. Record actual batches and CPU/GPU activity alongside latency and throughput.
4. **Explain the largest relevant delay.** Correlate request events with CPU threads, GPU work, transfers and synchronization. Use a controlled probe to distinguish competing explanations.
5. **Repeat, then improve.** Check independent runs and profiler overhead. Evaluate a targeted change against the same workload and quality requirements.

## Use clear measurement names

| Metric | Meaning |
| --- | --- |
| End-to-end latency | Client sends the request → client receives the complete result |
| First text / first audio | Client sends → first usable streamed text or audio arrives |
| Queue wait | Work is ready or enqueued → it begins execution, with the exact queue stated |
| Stage elapsed time | Wall time inside a stage; it may include CPU work, copies and waits |
| GPU execution | Device-side kernel activity measured in a trace |
| Throughput | Completed requests per second over a stated window; also record failures |

An internal first-token event is not client first-token latency. Overlapping stages cannot be added as if they ran sequentially. Compare both elapsed time and output amount: a shorter answer can finish sooner without faster execution.

## What makes a useful finding?

A long function call or low GPU activity is a clue. A bottleneck report should connect **an observation, its execution mechanism, and its effect on the target metric**. State alternative explanations and the evidence that supports or rejects them.

Use [request-level events](https://sgl-project.github.io/sglang-omni/developer_reference/profiler.html) for the broad picture, then short CPU/GPU traces for attribution. Keep ordinary performance runs separate from heavy profiling.

## Share findings, not entire workspaces

Keep exploratory runs and full logs on the experiment machine. Publish an issue when evidence supports a specific performance limit. Include the workload and versions, reproduction steps, a small results table, an explained trace or figure, limitations, related upstream work and the next optimization test.

Put only the necessary scripts, configuration, small data and figure sources under `evidence/<descriptive-name>/`, linked from that issue. Update the same issue as the investigation progresses. Keep model weights, environments, datasets and full traces out of Git. The README stays focused on the project and architecture.
