# Repository preparation validation

Validation date: 2026-11-17. This is an offline repository check, not a new inference result.

| Check | Result and scope |
|---|---|
| Preserved table arithmetic | Passed: pooled request medians, throughput windows, average in-flight counts, stage medians, call-weighted decode batches, paired time differences, category counts and boundary output identity |
| Patch baseline | Two patches apply to the exact pinned commit; all eight resulting package files match measured hashes |
| Patch rollback | Reverse application returns all eight baseline hashes |
| Observer extraction | Byte-identical to the archived request-local observer |
| Source resolution | Search-path resolution points to the isolated package and selected helper; processor and modified-source hashes match |
| Package identity | SGLang 0.5.22, Transformers 5.19.0; PyTorch distribution metadata 2.14.1 and literal build version 2.14.1+cu130 agree with their respective recorded meanings |
| Audio reconstruction | Three local source recordings and all eleven crops match their original byte SHA-256 values; no source files are changed |
| Python and shell syntax | Python AST parsing and Bash syntax check passed without importing inference engines |
| Document and data references | Local Markdown links resolve; configuration/manifests parse; external evidence paths and hashes are retained |
| Figures | Two schematic PNGs inspected visually; SVG XML/text inspected; editable Mermaid and a shared SVG/PNG drawing script retained |
| Original evidence bundle | ZIP is readable and unchanged: SHA-256 `ab06d3978a2b80911433480bf6129b9bbbe47544b239551b0775424f550597ee` |
| Language and repository scope | See the separate language audit; no performance attachment is promoted without issue eligibility |

The full command/exit records and internal issue eligibility review are retained in the original workspace's deliverables. No new GPU inference, live service deployment, portable full-matrix run, formal ASR assessment, or performance optimization was validated in R1. The processor/dependency check reads metadata and source files; it does not claim a freshly running service imported them.

Unconfirmed encoder-host causes and cross-startup KV-size differences remain internal research questions. No bottleneck issue draft is created. The repository preserves a reproducible setup and the means to verify existing evidence without presenting these questions as confirmed performance limits.
