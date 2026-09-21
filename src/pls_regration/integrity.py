"""Checks that protect frozen inputs and their temporal axis."""
from __future__ import annotations
import hashlib
from pathlib import Path
import pandas as pd
from .config import DatasetContract

def _read_time_column(contract: DatasetContract, root: Path) -> pd.Series:
    path = root / contract.source
    if not path.is_file():
        raise ValueError(f"{contract.identifier}: frozen source is missing: {contract.source}")
    if path.suffix.lower() == ".xlsx":
        frame = pd.read_excel(path, usecols=[contract.time_column])
    elif contract.time_parser == "composite_ymdh":
        frame = pd.read_csv(path, usecols=["year", "month", "day", "hour"])
    else:
        frame = pd.read_csv(path, usecols=[contract.time_column])
    if contract.time_parser == "unix_ms":
        return pd.to_datetime(frame[contract.time_column], unit="ms", utc=True, errors="coerce")
    if contract.time_parser == "datetime_dayfirst":
        return pd.to_datetime(frame[contract.time_column], dayfirst=True, utc=True, errors="coerce")
    if contract.time_parser == "composite_ymdh":
        return pd.to_datetime(frame[["year", "month", "day", "hour"]], utc=True, errors="coerce")
    return pd.to_datetime(frame[contract.time_column], utc=True, errors="coerce")

def assert_frozen_source_integrity(contract: DatasetContract, root: Path) -> None:
    path = root / contract.source
    payload = path.read_bytes()
    # Git may normalize CSV line endings between Windows and Linux runners.
    # The frozen digest therefore uses LF for text inputs and raw bytes for XLSX.
    if path.suffix.lower() == ".csv":
        payload = payload.replace(b"\r\n", b"\n")
    digest = hashlib.sha256(payload).hexdigest()
    if digest != contract.checksum_sha256:
        raise ValueError(f"{contract.identifier}: checksum differs from frozen contract")
    timestamps = _read_time_column(contract, root)
    if timestamps.empty or timestamps.isna().any():
        raise ValueError(f"{contract.identifier}: temporal axis contains invalid timestamps")
    duplicates = int(timestamps.duplicated().sum())
    if duplicates != contract.expected_duplicate_timestamps:
        raise ValueError(f"{contract.identifier}: duplicate timestamp count differs from frozen contract")
