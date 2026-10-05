"""Random Forest da Base 3.

A grade, o walk-forward e a escolha por MAE da validação estão em
`protocolo_final.py`. Execute, na raiz do projeto:

    python analyses/grupo3/02_modelos/run_protocolo_final.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from protocolo_final import RF_GRID, run_random_forest  # noqa: E402

__all__ = ["RF_GRID", "run_random_forest"]


def fit_random_forest(*args, **kwargs):
    raise RuntimeError(
        "O ajuste hora a hora foi substituído pelo protocolo final. "
        "Execute python analyses/grupo3/02_modelos/run_protocolo_final.py"
    )


def forecast_random_forest(*args, **kwargs):
    raise RuntimeError(
        "O ajuste hora a hora foi substituído pelo protocolo final. "
        "Execute python analyses/grupo3/02_modelos/run_protocolo_final.py"
    )
