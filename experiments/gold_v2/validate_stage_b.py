"""Cheap, independent health check for the long-running Gold V2 worker."""
from __future__ import annotations
import hashlib, json, subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(1 << 20), b''): h.update(part)
    return h.hexdigest()

reference = HERE / 'v1_reference_checksums.csv'
bad = []
for line in reference.read_text(encoding='utf-8').splitlines()[1:]:
    _, rel, expected, _ = line.split(',', 3)
    if digest(ROOT / rel) != expected: bad.append(rel)
state_path = HERE / 'outputs' / 'models' / 'stage_b_extended_state.json'
if not state_path.exists():
    state_path = HERE / 'outputs' / 'models' / 'stage_b_state.json'
state = json.loads(state_path.read_text(encoding='utf-8')) if state_path.exists() else {'status': 'not_started'}
result = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'v1_byte_identical': not bad, 'v1_mismatch_paths': bad, 'worker_state': state}
(HERE / 'outputs' / 'models' / 'stage_b_health.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
if bad: raise SystemExit('V1 integrity failure: ' + ', '.join(bad))
print(json.dumps(result, ensure_ascii=False))
