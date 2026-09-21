"""Versioned contracts for the five frozen time-series datasets."""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Availability = Literal["known_in_advance", "forecast_at_origin", "lag_only", "excluded"]
VALID_AVAILABILITY = frozenset({"known_in_advance", "forecast_at_origin", "lag_only", "excluded"})
VALID_TIME_PARSERS = frozenset({"datetime", "datetime_dayfirst", "unix_ms", "composite_ymdh"})

@dataclass(frozen=True)
class ExternalVariable:
    name: str
    availability: Availability
    evidence: str

@dataclass(frozen=True)
class DatasetContract:
    identifier: str
    owner_area: str
    source: str
    checksum_sha256: str
    expected_duplicate_timestamps: int
    source_reference: str
    time_column: str
    time_parser: str
    target_column: str
    target_unit: str
    frequency: str
    forecast_horizon: int
    external_variables: tuple[ExternalVariable, ...]

def load_dataset_contracts(path: str | Path) -> tuple[DatasetContract, ...]:
    """Load five explicit contracts without accepting undefined availability."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    datasets = payload.get("datasets")
    if not isinstance(datasets, list) or len(datasets) != 5:
        raise ValueError("datasets must contain exactly five datasets")
    contracts: list[DatasetContract] = []
    seen_ids: set[str] = set()
    seen_areas: set[str] = set()
    for item in datasets:
        required = {"id", "owner_area", "source", "checksum_sha256", "expected_duplicate_timestamps", "source_reference", "time_column", "time_parser", "target", "frequency", "forecast_horizon", "external_variables"}
        missing = required.difference(item)
        if missing:
            raise ValueError(f"dataset contract is missing: {sorted(missing)}")
        variables = tuple(ExternalVariable(variable["name"], variable["availability"], variable["evidence"]) for variable in item["external_variables"])
        if len(variables) < 2:
            raise ValueError(f"{item['id']} must declare at least two external variables")
        if any(variable.availability not in VALID_AVAILABILITY for variable in variables):
            raise ValueError(f"{item['id']} has an undefined temporal availability")
        if item["time_parser"] not in VALID_TIME_PARSERS:
            raise ValueError(f"{item['id']} has an unsupported time parser")
        if item["forecast_horizon"] < 1:
            raise ValueError(f"{item['id']} forecast_horizon must be positive")
        if len(item["checksum_sha256"]) != 64 or any(char not in "0123456789abcdef" for char in item["checksum_sha256"]):
            raise ValueError(f"{item['id']} must declare a lowercase SHA-256 checksum")
        if item["id"] in seen_ids or item["owner_area"] in seen_areas:
            raise ValueError("dataset identifiers and owner areas must be unique")
        seen_ids.add(item["id"]); seen_areas.add(item["owner_area"])
        contracts.append(DatasetContract(item["id"], item["owner_area"], item["source"], item["checksum_sha256"], item["expected_duplicate_timestamps"], item["source_reference"], item["time_column"], item["time_parser"], item["target"]["column"], item["target"]["unit"], item["frequency"], item["forecast_horizon"], variables))
    return tuple(contracts)
