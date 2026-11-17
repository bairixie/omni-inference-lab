# Architecture and task paths

## The model: understand inputs, then produce an answer

MiniCPM-o 4.5 connects media encoders to a language model and a speech-generation branch. An **encoder** converts media into vectors the language model can use; these vectors occupy positions in its input sequence.

| Component | What it does |
| --- | --- |
| Text tokenizer | Converts the prompt into tokens: units such as words or parts of words. |
| SigLip2 vision encoder | Encodes images and selected video frames. A resampler adapts the features for the language model. |
| Whisper-medium audio encoder | Encodes audio features; projection and pooling prepare them for the language model. |
| Qwen3-8B language backbone, or **Thinker** | Reads the combined inputs and generates the answer. **Prefill** processes the input; **decode** generates successive tokens. |
| Speech branch | The **Talker** generates speech codes. **Flow** turns them into acoustic features; **HiFT** turns those features into a waveform. SGLang Omni groups Flow and HiFT as **Code2Wav**. |

Component families come from the [official model card](https://huggingface.co/openbmb/MiniCPM-o-4_5). For the full model design, see the [technical report](https://arxiv.org/abs/2604.27393) and [official architecture figure](https://raw.githubusercontent.com/OpenBMB/MiniCPM-o/main/assets/minicpm-o-45-framework.png). Speech-stage names follow the [SGLang Omni implementation](https://github.com/sgl-project/sglang-omni/tree/main/sglang_omni/models/minicpm_o).

## Different tasks activate different paths

| Task | Main path |
| --- | --- |
| Text question → text | Text tokens → Thinker → text |
| Image question → text | Image preparation → vision encoder → Thinker with the question → text |
| Audio transcription → text | Audio preparation → audio encoder → Thinker → transcript |
| Spoken question → text answer | Audio preparation → audio encoder → Thinker → answer |
| Spoken question → spoken answer | Audio understanding → Thinker → Talker → Code2Wav → speech, with text output |
| Video + spoken question → answer | Frame and audio preparation → relevant encoders → Thinker → selected output branch |

The prompt and output matter as much as the input format. Transcribing a recording and answering a question about it can generate very different amounts of text. Reading supplied text aloud also differs from first generating an answer.

**Live conversation is another mode.** It keeps session state and processes incoming and outgoing chunks over time. An offline request does not measure whether a live conversation keeps up. See the [serving modes and examples](https://sgl-project.github.io/sglang-omni/cookbook/minicpm_o.html).

## The serving system: decide when and where work runs

SGLang Omni receives the request, routes it between stages, schedules ready work and returns the response. Its autoregressive stages use SGLang for language-generation scheduling and KV management. The CPU handles orchestration and media processing; the GPU runs model operations.

A **stage** is a logical step, not necessarily a separate process or GPU. Multiple stages can share one GPU. A **batch** is work executed together; **concurrency** is the number of requests in flight. Eight concurrent requests do not necessarily form one batch of eight.

Actual placement and overlap depend on the running configuration. Trace that configuration before assigning a delay to a component. [Runtime architecture](https://sgl-project.github.io/sglang-omni/developer_reference/main.html) · [Profiling guide](profiling.md).
