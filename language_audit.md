# English language and scope audit

Audit date: 2026-11-17.

## Scope

The audit covers the entire target directory, including untracked files, hidden files, directory names, filenames, Markdown, Python, shell scripts, patches, JSON keys and string values, Mermaid, SVG text, license text, and both rendered PNG diagrams. Git internals are excluded. No CSV files are selected for this repository: baseline and unconfirmed-anomaly tables remain in the original workspace under the provenance manifest.

## Method

1. Recursively enumerate all files and directories independently of Git tracking state.
2. Parse readable UTF-8 text and decoded JSON strings; flag non-English script characters and unreviewed non-ASCII text. Mathematical notation, units and proper names are not language violations.
3. Manually review English prose, comments, docstrings, configuration explanations, source descriptions, patch context and diagram labels. An ASCII-only scan cannot itself prove that prose is English.
4. Inspect every rendered PNG alongside its English SVG text and Python drawing source. Check the editable Mermaid topology. These are clearly labeled architecture/placement diagrams, not synthetic traces.
5. Check local Markdown paths, Python/JSON/shell syntax, common secret patterns, account-specific absolute paths, file sizes and excluded runtime asset types.

The repeatable scanner is `scripts/audit_repository.py`. Its machine-readable inventory and hashes are kept outside the target directory in the R1 delivery record, avoiding a self-referential file inventory.

## Results

- All directory and file names use English/ASCII identifiers.
- All narrative text, code comments/docstrings, JSON field explanations, patch context, and figure labels are English.
- No Chinese document, translated raw model output, audio, full log, profiler trace, model, environment, or archive is copied into the repository.
- Source filenames ending in `_zh.md` appear only as ASCII provenance references to untouched originals. Their Chinese contents are not copied or translated into measurement records.
- Both PNGs were visually reviewed. Long labels were resized to remain within their nodes. SVG labels and Mermaid sources use English; no non-English text is hidden in a bitmap asset.
- No unexplained non-ASCII text, missing local Markdown targets, common access-token/private-key patterns, or hardcoded account paths remain in the audited files.
- No file exceeds 256 KiB. The largest files are the two architecture PNGs; they are small readable schematic assets with editable sources, not experimental traces. No LFS configuration is added.
- No issue draft is generated. The English internal eligibility review remains outside this repository in the original workspace's deliverables.

## README scope review

Passed. The README contains project purpose, research motivation, model components/task concepts, serving-system roles, memory/cache concepts, repository navigation and references. It contains no research-phase chronology, personal performance table, anomaly numbers, local tested/untested matrix, experiment launch commands, meeting script or result leaderboard. Its single Issues entry leads to the publication policy and the explicitly authorized GitHub destination.

## Limits and preservation

Automated character and secret scans are heuristic aids; the language conclusion also relies on manual review of the selected small file set. This audit does not certify inference correctness or output quality. Existing non-English originals, complete investigations and the unchanged evidence ZIP remain in the original run workspace. No raw measurement is altered to satisfy a language rule. The R1 preparation was local only. The user subsequently authorized pushing the repository to `bairixie/omni-inference-lab`; the publication links were updated in English and the full file scan was repeated. No GitHub issue or group message is created by that publication step.
