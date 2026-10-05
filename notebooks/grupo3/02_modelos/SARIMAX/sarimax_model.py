"""SARIMAX da Base 3.

A grade, o AIC/BIC e o walk-forward estão em `protocolo_final.py`.
Execute, na raiz do projeto:

    python analyses/grupo3/02_modelos/run_protocolo_final.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from protocolo_final import SARIMAX_CANDIDATES, run_sarimax  # noqa: E402

__all__ = ["SARIMAX_CANDIDATES", "run_sarimax"]


def fit_sarimax(*args, **kwargs):
    raise RuntimeError(
        "O ajuste hora a hora foi substituído pelo protocolo final. "
        "Execute python analyses/grupo3/02_modelos/run_protocolo_final.py"
    )


def forecast_sarimax(*args, **kwargs):
    raise RuntimeError(
        "O ajuste hora a hora foi substituído pelo protocolo final. "
        "Execute python analyses/grupo3/02_modelos/run_protocolo_final.py"
    )
