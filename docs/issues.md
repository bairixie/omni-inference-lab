# Issues

This is the stable entry point for bottleneck reports: [GitHub Issues](https://github.com/bairixie/omni-inference-lab/issues).

The repository is published under the explicitly authorized `bairixie/omni-inference-lab` destination. Publishing the repository does not qualify internal observations as bottleneck findings. No investigation issue is created automatically.

Keep this entry stable rather than maintaining a results leaderboard in the README. Qualifying reports belong in GitHub Issues, with versioned small attachments in this repository.

## Evidence required

A report must identify a workload, frozen environment, target performance metric, reproducible observation, controlled output work and cache state, and evidence that a stage/resource/dependency limits that metric. It must distinguish confirmed limits from unresolved causes, host intervals from GPU execution, and overlapping work from exclusive time.

The report should include reproduction, experimental controls, readable results and figures, upstream overlap, a proposed single-variable optimization/validation plan, and acceptance criteria for end-to-end benefit and output quality. Put its small versioned attachments in `evidence/`. Update the same issue when new evidence addresses the same bottleneck.

Unconfirmed anomalies, baseline results, negative results, quality-assessment tasks and measurement gaps remain internal research records. They do not become issues solely because they are interesting. The internal eligibility review is retained in the original workspace's deliverables, outside this repository.
