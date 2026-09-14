"""Configuration contracts for frozen datasets and their external variables."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Availability = Literal["known_in_advance", "forecast_at_origin", "lag_only", "excluded"]
VALID_AVAILABILITY = frozenset({"known_in_advance", "forecast_at_origin", "lag_only", "excluded"})


@dataclass(frozen=True)
class ExternalVariable:
    name: str
    availability: Availability
    evidence: str


@dataclass(frozen=True)
class DatasetContract:
    identifier: str
    source: str
    target_column: str
    target_unit: str
    frequency: str
    forecast_horizon: int
    external_variables: tuple[ExternalVariable, ...]


def load_dataset_contracts(path: str | Path) -> tuple[DatasetContract, ...]:
    """Load the versioned configuration without accepting undefined availability."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    datasets = payload.get("datasets")
    if not isinstance(datasets, list) or len(datasets) > 5:
        raise ValueError("datasets must be a list containing at most five datasets")

    contracts: list[DatasetContract] = []
    for item in datasets:
        variables = tuple(
            ExternalVariable(
                name=variable["name"],
                availability=variable["availability"],
                evidence=variable["evidence"],
            )
            for variable in item["external_variables"]
        )
        if len(variables) < 2:
            raise ValueError(f"{item['id']} must declare at least two external variables")
        if any(variable.availability not in VALID_AVAILABILITY for variable in variables):
            raise ValueError(f"{item['id']} has an undefined temporal availability")
        if item["forecast_horizon"] < 1:
            raise ValueError(f"{item['id']} forecast_horizon must be positive")
        contracts.append(
            DatasetContract(
                identifier=item["id"],
                source=item["source"],
                target_column=item["target"]["column"],
                target_unit=item["target"]["unit"],
                frequency=item["frequency"],
                forecast_horizon=item["forecast_horizon"],
                external_variables=variables,
            )
        )
    return tuple(contracts)

