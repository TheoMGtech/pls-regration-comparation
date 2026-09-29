# Gold V2 experimental

This directory is an isolated experiment beside the frozen Group 5 V1. It never
edits `bases/grupo5/`, `analyses/grupo5/`, or `05_relatorio/`.

`python experiments/gold_v2/run_stage_a.py` recreates the Stage A provenance
records, conservative features, target diagnostics, and the deliberately small
validation-only ablation screen. It is not an authorization to run Stage B.

Downloaded raw files and the wide derived feature table are intentionally local
and ignored: `sources.json` records their download URLs, coverage, hashes and
bytes so they can be recreated without committing generated data.

The authoritative Stage A status and its approval gate are in
`config/protocol_v2.json` and `docs/V2_STATUS.md`.
