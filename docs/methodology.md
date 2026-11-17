# Measurement methodology

## Define the workload before measuring it

Record input modality, task, output type, service mode, model snapshot, imported source identity, precision, generation settings, CPU resources, and cache policy. Transcription and question answering require different baselines. Offline responses and real-time duplex sessions have different timing contracts. Changing GPU alone does not create a new research contribution.

Classify work as **Measurement setup** (instrument or calibrate), **Local validation** (check an established mechanism in a fixed environment), or **Exploratory extension** (answer a specific question not resolved by the reviewed evidence). An unbounded search cannot prove novelty, and an open upstream issue does not mean nobody has worked on it.

## Time boundaries

| Symbol or interval | Boundary | Interpretation |
|---|---|---|
| A | Client send-start clock to parsed response | End-to-end client wall time, including transport and parsing |
| B | Server admission/start event to first observable nonempty text token in the generation-result hook | Internal first-text latency; not client TTFT for a nonstreaming interface |
| C | Same first-text hook to last observable text-token hook | Generation-related host interval after first text, not pure GPU decode time |
| Encoder host interval | Entry to encoder wrapper through wrapper return | Includes dispatch, Python work, transfers or waits within that scope; not a GPU kernel sum |
| Thinker queue | Recorded scheduler enqueue/admission boundary to scheduling boundary | Only the observed queue, not every possible upstream wait |
| Batch service | Batch launch hook to result-processing hook | Shared batch interval; no request has exclusive ownership of all its time |

For the same request and compatible clocks, B plus C reaches from server admission to the last observed text token. It does not equal A: client transport, admission differences, terminal handling, and parsing lie outside or around that span. Do not add overlapping stages or medians from different requests to draw a fictitious complete timeline. A kernel trace uses another clock domain and needs explicit correlation.

The first generated token may be a special token; the observer's first-text rule decodes each observed token ID and requires a nonempty, non-whitespace piece. This is an operational measurement boundary, not a claim that the client could already render that text. The number of output IDs and the number of such text pieces are different counters.

## Work and memory accounting

Record decoded waveform samples and rate, feature chunk lengths, padded feature shape, media embedding positions, actual Thinker input positions, generated IDs, and termination reason. The HTTP usage field may count only the tokenizer-visible prompt before media expansion; its meaning must be checked against the local response code. Do not treat an HTTP input-token count as the total multimodal context.

Record retractions, evictions, failures, truncations, and output-cap hits. A successful response with `stop` and no length cap does not certify a semantically complete transcript. Published reference words and a separately verified alignment are needed for formal ASR evaluation. A model's own earlier output is not an independent reference.

Measure pool capacity and unavailable slots under the same startup and sampling rules. Keep request, batch, and process metrics distinct. Request peaks from different moments cannot be summed into a simultaneous device peak.

## Concurrency and comparisons

A closed-loop client replaces each completed request while keeping at most C requests in flight. Report the full window from first send to last completion, including fill and drain. Throughput is successful requests divided by that window; failures remain in the window and are reported separately. Pooling rounds uses total successes divided by total windows. Pooled P50 is the median of all eligible request durations, not the average of round medians.

Actual model batch size comes from scheduled request membership. A call-weighted mean counts each model call once; a time-weighted mean answers a different question. Keep prefill, decode, mixed calls, logical request counts, and CUDA Graph padded dimensions separate. Report the actual mean and peak in-flight population during a diagnostic window.

Control input identity, outputs, caches, versions, startup, and observer settings. Reverse condition order when checking a repeatable effect. Repetitions improve timing estimates; they do not create independent recordings. A change in output length can change latency without any change in execution efficiency.

## Observation and issue acceptance

Heavy profiler runs explain mechanisms and are separate from primary performance measurements. Request hooks are lighter, but still have overhead. Preserve the same observer settings within a comparison and measure overhead when its magnitude could change the conclusion. Do not introduce a global CUDA synchronization at every stage just to simplify a plot.

A bottleneck issue needs reproducible evidence that a stage, resource, or dependency limits an explicitly chosen end-to-end metric, deadline, or capacity. A long interval, lower GPU utilization, measurement gap, or slower condition alone is insufficient. Keep confirmed performance limits separate from uncertain underlying causes. The [Issues policy](issues.md) defines the publication boundary.
