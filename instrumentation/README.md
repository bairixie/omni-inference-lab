# Archived observation module

`p1_observe.py` retains its historical import name so the extracted hooks produce the same observation behavior. It is copied byte-for-byte from the final request-local observer, not rewritten during repository preparation.

Records are keyed by run ID and request ID. Batch IDs include process identity and sequence number. Each batch stores its actual request membership and forward mode. Request, batch and process fields have different ownership. Python host clocks and allocator counters are sampled; there is no per-stage global CUDA synchronization or hot-path file writing added by this module.

The dictionaries are exported between cohorts by the archived client. The module does not stream an unbounded production telemetry service, enforce a memory budget for its own records, or measure exact kernel duration. Its process-level peak counters are cumulative. First-text observation decodes token pieces on the host and has overhead. All comparisons must use the same observation configuration.

This module imports PyTorch when a service loads it. Offline table and patch verifiers do not import it. Raw observed text or failure messages may be non-English; those runtime artifacts belong in the original run area, not in this English-only repository.
