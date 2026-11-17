# Third-party notices

## SGLang Omni

Source: https://github.com/sgl-project/sglang-omni

Baseline commit: `30da209c2330eaf50b1838fc82a2975c1ddc78f4`.

The patch context and the #3701 correctness change derive from SGLang Omni, licensed under Apache License 2.0. The license text is preserved at [licenses/sglang-omni-LICENSE.txt](licenses/sglang-omni-LICENSE.txt). Existing SPDX declarations and attribution in patch context are preserved. The measurement patch and helper are local research modifications, identified separately in the patch manifest. No full upstream checkout is included. There is no root NOTICE file at the checked baseline. A component notice exists under `models/minicpm_o/components/token2wav/THIRD_PARTY_NOTICES.md`; no code from that component is copied here. Its source remains available at the pinned upstream commit.

## MiniCPM-o and runtime dependencies

MiniCPM-o 4.5: https://huggingface.co/openbmb/MiniCPM-o-4_5

SGLang, PyTorch, Transformers, NumPy, SciPy, SoundFile, and Pillow are referenced or used by the documented tools. Their packages, model weights, processors, and environments are not redistributed here. Consult their own licenses before redistribution. Dependency identities are recorded for reproducibility, not as a request to upgrade or reinstall them.

## Audio and reference material

The Open Speech Repository provides the cited recordings under the usage statement at https://www.voiptroubleshooter.com/open_speech/ : use with source attribution. The manifest retains that source statement rather than assigning a new SPDX license. Published Harvard sentence lists are referenced at https://www.cs.columbia.edu/~hgs/audio/harvard.html . Audio files and full reference/model transcripts are not redistributed. Provenance and sample hashes preserve reconstruction without changing the inputs.

## Repository-authored material

New explanatory documents and schematic diagrams were written for this repository. No blanket license for newly authored material is assigned by this preparation step. The upstream license does not automatically determine the license of every new file. Publication and a repository-wide license can be decided separately.
