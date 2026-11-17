# Architecture and execution paths

## Three kinds of evidence

A conceptual model diagram explains the computation. Source code and a resolved configuration explain an intended deployment. Request events identify which path an actual request took. None of these is a substitute for the others. The figures in this directory are diagrams; they contain no invented timing data.

The concrete example uses SGLang Omni commit `30da209c2330eaf50b1838fc82a2975c1ddc78f4`, the MiniCPM-o retraction restoration patch, and the archived request/batch observer. The [environment](../experiments/minicpmo_a6000_asr/configs/environment.json) records the model snapshot and imported scheduler path. Current upstream documentation may describe capabilities or flags absent from that source.

## Components and vocabulary

MiniCPM-o 4.5 combines a Qwen3-8B language backbone, SigLip2 vision encoding, Whisper-medium audio encoding, and a CosyVoice2-based speech path. The local checkpoint configuration describes 36 language layers, a SigLIP-family vision configuration, and a 24-layer Whisper encoder. The official model card supplies the family names; the checkpoint supplies the concrete local configuration. The checkpoint and processor hashes are in the environment manifest.

The vision path resamples/project features into language-compatible embeddings. The audio path extracts mel features, encodes them, projects and pools the output, then places the resulting embeddings at audio positions in the Thinker sequence. More waveform samples do not imply an equal number of text tokens. Feature frames, padded frame slots, media embedding rows, language-model positions, and generated token IDs are separate quantities.

The Thinker performs prompt prefill and autoregressive token generation. The Talker is another autoregressive model and has its own attention state. Flow is a conditional acoustic generator, not a text-token decoder. HiFT produces waveform samples from acoustic features. Code2Wav groups Flow and HiFT in the serving implementation.

## Task paths

| Input and task | Computation and output |
|---|---|
| Text question | Tokenization, Thinker, text detokenization |
| Image question | Image preprocessing, vision encoder/projector, Thinker, text or speech branch |
| Audio transcription | Waveform loading/resampling, audio features, audio encoder/projector, Thinker, written transcript |
| Audio question answering | Similar media path, different instruction and language output workload |
| Text or audio to speech | Thinker conditioning, Talker codec tokens, Flow, HiFT, audio serialization |
| Offline video question | Timed frames and optional audio, modality encoders, Thinker, selected output branch |
| Real-time duplex session | Session state and incremental perception/generation; a different protocol and scheduling path |

These are architectural descriptions. Local functionality records for other modalities remain in the original workspace. The archived performance workload is A1 audio transcription with a text response. It executes neither Talker nor Flow nor HiFT. A speech-capable deployment can nevertheless keep those components resident. Historical Transformers and isolated Flow Graph work are separate studies and do not validate this task's performance or output quality.

## Concrete process and device placement

| OS process role | Logical stages | Placement |
|---|---|---|
| Coordinator | HTTP handling, request lifecycle, routing, result return | CPU |
| Pipeline | Preprocessing, image/audio encoding, Thinker, text detokenization | CPU threads and logical GPU 0 |
| Speech worker | Talker and Code2Wav | CPU scheduling and the same logical GPU 0 |

A logical stage is not an OS process. Preprocessing is configured within the GPU-associated pipeline but includes CPU media operations. The text `decode` stage means detokenization; it is distinct from Thinker autoregressive decode. Code2Wav belongs to the speech process, not the pipeline process.

For A1, the coordinator admits a request, preprocessing builds text and audio inputs, the audio encoder produces embeddings, and Thinker admission waits for its required inputs. The Thinker scheduler handles prefill and subsequent generation batches. The text stage assembles the response, which returns through the coordinator. Request-level events can describe this route. They do not establish that every interval is GPU execution, and separate process clocks must be checked before combining them.

## Frozen source references

Paths below are relative to the upstream repository at the pinned commit; local hook changes are in [patches](../patches/README.md).

- [`models/minicpm_o/config.py`](https://github.com/sgl-project/sglang-omni/blob/30da209c2330eaf50b1838fc82a2975c1ddc78f4/sglang_omni/models/minicpm_o/config.py): `text_stages`, `speech_stages`, stage placement and defaults.
- [`models/minicpm_o/routing.py`](https://github.com/sgl-project/sglang-omni/blob/30da209c2330eaf50b1838fc82a2975c1ddc78f4/sglang_omni/models/minicpm_o/routing.py): modality routing and optional speech branch.
- [`models/minicpm_o/stages.py`](https://github.com/sgl-project/sglang-omni/blob/30da209c2330eaf50b1838fc82a2975c1ddc78f4/sglang_omni/models/minicpm_o/stages.py): stage factories, encoder execution and cache ownership.
- [`components/audio_encoder.py`](https://github.com/sgl-project/sglang-omni/blob/30da209c2330eaf50b1838fc82a2975c1ddc78f4/sglang_omni/models/minicpm_o/components/audio_encoder.py): convolution/pooling length calculations and valid-output selection.
- [`request_builders.py`](https://github.com/sgl-project/sglang-omni/blob/30da209c2330eaf50b1838fc82a2975c1ddc78f4/sglang_omni/models/minicpm_o/request_builders.py): Thinker inputs and request construction.

The processor is checkpoint-provided code loaded through the Transformers module cache. Its exact hash matters independently of the Omni commit. The archive retains the imported file and raw chunk/position records; the repository carries their identity and reconstruction instructions, not a modified processor.
