"""Contrato temporal compartilhado para os quatro modelos da Base 3.

A matriz de features já contém apenas atributos disponíveis na origem.
Este módulo somente define cortes; não treina modelos nem seleciona hiperparâmetros.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

RANDOM_STATE = 42
HORIZON_HOURS = 1
FINAL_TEST_FRACTION = 0.20
INTERNAL_VALIDATION_FRACTION = 0.20


def repository_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "bases" / "grupo3").exists():
            return candidate
    raise FileNotFoundError("Raiz do repositório não encontrada.")


def build_temporal_protocol(features: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    required = {"timestamp", "target_timestamp", "target_pm25_t_plus_1"}
    missing = required.difference(features.columns)
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {sorted(missing)}")

    frame = features.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="raise")
    frame["target_timestamp"] = pd.to_datetime(frame["target_timestamp"], errors="raise")
    frame = frame.sort_values("timestamp", kind="stable").reset_index(drop=True)
    # target_pm25_observed = PM2.5 na origem t (para modelos univariados como Holt-Winters)
    frame["target_pm25_observed"] = frame["target_pm25_t_plus_1"].shift(1)
    if frame["timestamp"].duplicated().any() or not frame["timestamp"].is_monotonic_increasing:
        raise ValueError("Features precisam estar ordenadas e sem origens duplicadas.")
    if not frame["target_timestamp"].sub(frame["timestamp"]).eq(pd.Timedelta(hours=HORIZON_HOURS)).all():
        raise ValueError("O horizonte não é consistentemente de uma hora.")
    if frame["target_pm25_t_plus_1"].isna().any():
        raise ValueError("O protocolo não aceita alvos futuros ausentes.")

    n_rows = len(frame)
    final_test_start = int(n_rows * (1 - FINAL_TEST_FRACTION))
    development = frame.iloc[:final_test_start]
    internal_train_end = int(len(development) * (1 - INTERNAL_VALIDATION_FRACTION))

    labels = pd.Series("test_final", index=frame.index, dtype="string")
    labels.iloc[:internal_train_end] = "train_interno"
    labels.iloc[internal_train_end:final_test_start] = "validacao_interna"
    frame["split"] = labels.to_numpy()

    boundaries = {
        "train_interno": (0, internal_train_end),
        "validacao_interna": (internal_train_end, final_test_start),
        "test_final": (final_test_start, n_rows),
    }
    split_rows = []
    for split_name, (start, stop) in boundaries.items():
        subset = frame.iloc[start:stop]
        split_rows.append({
            "split": split_name,
            "start_row_inclusive": start,
            "end_row_exclusive": stop,
            "rows": len(subset),
            "origin_start": str(subset["timestamp"].min()),
            "origin_end": str(subset["timestamp"].max()),
            "target_start": str(subset["target_timestamp"].min()),
            "target_end": str(subset["target_timestamp"].max()),
        })
    split_table = pd.DataFrame(split_rows)

    protocol = {
        "dataset": "Base 3 — PRSA Aotizhongxin",
        "features_file": "analyses/grupo3/01_dados/outputs/features_base3.csv",
        "target": "target_pm25_t_plus_1",
        "origin_column": "timestamp",
        "target_timestamp_column": "target_timestamp",
        "horizon_hours": HORIZON_HOURS,
        "final_test_fraction": FINAL_TEST_FRACTION,
        "internal_validation_fraction_of_development": INTERNAL_VALIDATION_FRACTION,
        "split_strategy": "chronological; no shuffle",
        "training_window": "expanding",
        "random_state": RANDOM_STATE,
        "rows_total": n_rows,
        "rows_development": final_test_start,
        "rows_train_internal": internal_train_end,
        "rows_validation_internal": final_test_start - internal_train_end,
        "rows_test_final": n_rows - final_test_start,
        "hyperparameter_selection": "train_interno -> validacao_interna only",
        "test_usage": "only after hyperparameters are frozen",
        "walk_forward": {
            "initial_training_rows": internal_train_end,
            "refit": "at every forecast origin",
            "update": "append the observed target after each one-step forecast",
            "test_origins": "all origins in test_final",
        },
    }
    return frame, {"protocol": protocol, "split_table": split_table}


def main() -> None:
    root = repository_root()
    output_dir = root / "analyses" / "grupo3" / "02_modelos" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    features_path = root / "analyses" / "grupo3" / "01_dados" / "outputs" / "features_base3.csv"
    features = pd.read_csv(features_path, parse_dates=["timestamp", "target_timestamp"])
    labeled, result = build_temporal_protocol(features)
    labeled.to_csv(output_dir / "features_with_splits.csv", index=False)
    result["split_table"].to_csv(output_dir / "temporal_splits.csv", index=False)
    with (output_dir / "validation_protocol.json").open("w", encoding="utf-8") as file:
        json.dump(result["protocol"], file, ensure_ascii=False, indent=2)
    print(result["split_table"].to_string(index=False))
    print(f"Protocol saved to {output_dir}")


if __name__ == "__main__":
    main()
