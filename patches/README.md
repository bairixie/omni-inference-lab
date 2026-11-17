# Patch baseline and rollback

Upstream repository: https://github.com/sgl-project/sglang-omni

Exact baseline: `30da209c2330eaf50b1838fc82a2975c1ddc78f4`.

1. `0001-minicpmo-retraction-restore.patch` is the archived minimal two-file correctness backport of upstream #3701. It restores multimodal inputs after retraction and constructs the corresponding request class. SGLang remains 0.5.22. This is not the full upstream PR or a performance optimization.
2. `0002-request-batch-observation.patch` is a consolidated diff from that corrected baseline to the measured package. It adds the archived measurement hooks. Load `instrumentation/p1_observe.py` on `PYTHONPATH`; its legacy module name is part of the hook interface.

The [manifest](manifest.json) records all eight affected package files, base/corrected/measured hashes and apply order. The observer and two small runtime adapters are extracted separately. No upstream source tree is vendored.

Run the offline patch verifier from the experiment guide. It reads baseline blobs from an existing checkout, applies the patches only inside a temporary directory, and compares every resulting file with its archived measured hash. It does not alter that checkout, import a model, or allocate GPU memory.

For a future isolated reconstruction, apply the patches in order to a fresh copy of the exact baseline. To remove observation, reverse patch 2 in that copy and remove the observer import path. To remove the correctness backport, reverse patch 1 only after patch 2. Keep the original run artifacts and source copies unchanged. Reversing patches changes the experiment version; do not combine results across versions.

The historical correctness regression covered restored embedding rows and a forced-retraction smoke request. R1 rechecks patch application and source identity offline; it does not repeat GPU regression or claim the full upstream test suite passes.
