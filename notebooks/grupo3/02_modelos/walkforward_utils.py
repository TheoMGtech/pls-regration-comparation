"""Infraestrutura temporal compartilhada pelos quatro modelos da Base 3.

As funções deste módulo não escolhem hiperparâmetros e não conhecem detalhes do
algoritmo. Cada notebook fornece o adaptador model-specific fit_predict.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
import pandas as pd


def mae(y_true, y_pred) -> float:
    true = np.asarray(y_true, dtype=float)
    pred = np.asarray(y_pred, dtype=float)
    if true.shape != pred.shape:
        raise ValueError("y_true e y_pred precisam ter o mesmo formato.")
    return float(np.mean(np.abs(true - pred)))


def expanding_walk_forward(
    initial_history: pd.DataFrame,
    evaluation_frame: pd.DataFrame,
    fit_predict: Callable[[pd.DataFrame, pd.Series], float],
    *,
    model_name: str,
    split_name: str,
    stride: int = 1,
) -> pd.DataFrame:
    """Executa previsões one-step com janela expansiva e refit em cada origem.

    ``stride`` > 1 escolhe quais origens entram na avaliação. O histórico de cada
    origem inclui todas as horas anteriores, inclusive as que não foram pontuadas.
    """
    if stride < 1:
        raise ValueError("stride deve ser >= 1.")
    n_hist = len(initial_history)
    combined = pd.concat([initial_history, evaluation_frame], ignore_index=True)
    rows: list[dict[str, Any]] = []
    for pos in range(n_hist, len(combined), stride):
        history = combined.iloc[:pos]
        current = combined.iloc[pos]
        prediction = float(fit_predict(history, current))
        y_true = float(current["target_pm25_t_plus_1"])
        rows.append({
            "model": model_name,
            "split": split_name,
            "forecast_origin": current["timestamp"],
            "target_date": current["target_timestamp"],
            "horizon": 1,
            "y_true": y_true,
            "y_pred": prediction,
            "residual": y_true - prediction,
        })
    result = pd.DataFrame(rows)
    if result.empty:
        raise ValueError("A avaliação temporal não possui observações.")
    result["absolute_error"] = (result["y_true"] - result["y_pred"]).abs()
    return result
