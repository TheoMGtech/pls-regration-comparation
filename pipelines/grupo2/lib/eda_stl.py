"""EDA e decomposição STL."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import STL

from pipelines.grupo2 import config


def seasonal_strength(stl_result) -> float:
    """Força da sazonalidade (método da aula / Wang et al.)."""
    resid = np.asarray(stl_result.resid)
    seasonal = np.asarray(stl_result.seasonal)
    var_resid = np.nanvar(resid)
    var_deseas = np.nanvar(resid + seasonal)
    if var_deseas <= 0:
        return 0.0
    return float(max(0.0, 1.0 - var_resid / var_deseas))


def run_eda_and_stl(df: pd.DataFrame, fig_dir: Path | None = None) -> dict:
    fig_dir = fig_dir or config.FIG_DIR
    fig_dir.mkdir(parents=True, exist_ok=True)

    series = df.set_index(config.DATETIME_COL)[config.TARGET].asfreq(config.FREQ)

    # Série alvo
    fig, ax = plt.subplots(figsize=(12, 4))
    series.plot(ax=ax, lw=0.6, color="#1f4e79")
    ax.set_title("Tráfego horário — Metro Interstate")
    ax.set_ylabel("Veículos/hora")
    fig.tight_layout()
    fig.savefig(fig_dir / "01_serie_alvo.png", dpi=120)
    plt.close(fig)

    # Exógenas
    fig, axes = plt.subplots(2, 2, figsize=(12, 7), sharex=True)
    plot_df = df.set_index(config.DATETIME_COL)
    plot_df["temp"].plot(ax=axes[0, 0], lw=0.5, title="Temperatura (K)")
    plot_df["rain_1h"].plot(ax=axes[0, 1], lw=0.5, title="Chuva 1h (mm)")
    plot_df["clouds_all"].plot(ax=axes[1, 0], lw=0.5, title="Nuvens (%)")
    plot_df["snow_1h"].plot(ax=axes[1, 1], lw=0.5, title="Neve 1h (mm)")
    fig.suptitle("Variáveis externas")
    fig.tight_layout()
    fig.savefig(fig_dir / "02_externas.png", dpi=120)
    plt.close(fig)

    # Perfil horário médio
    fig, ax = plt.subplots(figsize=(8, 4))
    df.assign(hour=pd.to_datetime(df[config.DATETIME_COL]).dt.hour).groupby("hour")[
        config.TARGET
    ].mean().plot(ax=ax, marker="o", color="#c45c26")
    ax.set_title("Perfil médio por hora do dia")
    ax.set_xlabel("Hora")
    ax.set_ylabel("Tráfego médio")
    fig.tight_layout()
    fig.savefig(fig_dir / "03_perfil_horario.png", dpi=120)
    plt.close(fig)

    # STL em amostra recente (1 ano) para interpretação visual estável
    stl_sample = series.iloc[-24 * 365 :]
    stl = STL(stl_sample, period=config.SEASONAL_PERIOD, robust=True).fit()
    strength = seasonal_strength(stl)

    fig = stl.plot()
    fig.set_size_inches(12, 8)
    fig.suptitle(f"STL (último ano) — força sazonal = {strength:.3f}", y=1.02)
    fig.tight_layout()
    fig.savefig(fig_dir / "04_stl.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

    # STL completo seria muito pesado; reporta também força em amostra de treino
    return {
        "stl_sample_start": str(stl_sample.index.min()),
        "stl_sample_end": str(stl_sample.index.max()),
        "seasonal_strength": strength,
        "seasonal_period": config.SEASONAL_PERIOD,
        "trend_start_mean": float(stl.trend.iloc[:24 * 7].mean()),
        "trend_end_mean": float(stl.trend.iloc[-24 * 7 :].mean()),
        "figures": [
            "01_serie_alvo.png",
            "02_externas.png",
            "03_perfil_horario.png",
            "04_stl.png",
        ],
    }
