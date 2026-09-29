"""Parâmetros fixos da Base 2 — Bruna Cardoso."""

from pathlib import Path

GROUP = "grupo2"
OWNER = "Bruna Carvalho Cardoso"
RANDOM_STATE = 67
TRAIN_RATIO = 0.80
HORIZON = 1  # 1 hora à frente
FREQ = "h"
SEASONAL_PERIOD = 24  # sazonalidade diária em série horária

# Caminhos
ROOT = Path(__file__).resolve().parents[2]
PIPELINE_DIR = Path(__file__).resolve().parent
NOTEBOOKS_DIR = ROOT / "analyses" / GROUP
RAW_PATH = ROOT / "bases" / GROUP / "Metro_Interstate_Traffic_Volume.csv"
OUTPUT_DIR = PIPELINE_DIR / "outputs"
DATA_DIR = OUTPUT_DIR / "data"
FIG_DIR = OUTPUT_DIR / "figures"
MODEL_DIR = OUTPUT_DIR / "models"
RESULT_DIR = OUTPUT_DIR / "results"

# Caminhos relativos dos notebooks até pipelines/grupo2/outputs
NOTEBOOK_OUTPUTS_REL = "../../../pipelines/grupo2/outputs"  # 01/03/04/05
NOTEBOOK_OUTPUTS_REL_MODELS = "../../../../pipelines/grupo2/outputs"  # 02_modelos/*

TARGET = "traffic_volume"
DATETIME_COL = "date_time"

# Features tabulares compartilhadas (RF + PLS)
FEATURE_COLS = [
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
    "month_sin",
    "month_cos",
    "is_weekend",
    "is_holiday",
    "y_lag_1",
    "y_lag_24",
    "y_lag_168",
    "y_roll_mean_24",
    "y_roll_std_24",
    "y_roll_mean_168",
    "temp_lag_1",
    "rain_lag_1",
    "snow_lag_1",
    "clouds_lag_1",
]

# Exógenas para SARIMAX (já defasadas / calendário)
SARIMAX_EXOG = [
    "is_holiday",
    "is_weekend",
    "temp_lag_1",
    "rain_lag_1",
    "clouds_lag_1",
]

# Walk-forward: refit periódico para viabilidade em série horária longa
REFIT_EVERY = 336  # 2 semanas
SARIMAX_MAX_TRAIN = 24 * 30  # janela máxima de treino (~30 dias)
HW_MAX_TRAIN = 24 * 45
ML_MAX_TRAIN = 24 * 120  # RF/PLS: últimos ~120 dias (expandido via walk-forward)

# Busca de hiperparâmetros (somente no bloco de treino)
RF_PARAM_GRID = {
    "n_estimators": [100, 200],
    "max_depth": [12, 24],
    "min_samples_split": [2, 5],
    "min_samples_leaf": [1, 2],
    "max_features": ["sqrt"],
}

PLS_COMPONENTS_GRID = list(range(2, 11))

SARIMAX_ORDER_GRID = [
    ((1, 0, 1), (0, 1, 1, SEASONAL_PERIOD)),
    ((1, 0, 0), (0, 1, 1, SEASONAL_PERIOD)),
    ((2, 0, 1), (0, 1, 1, SEASONAL_PERIOD)),
    ((1, 1, 1), (0, 1, 1, SEASONAL_PERIOD)),
]

HW_TREND_GRID = ["add", None]
HW_SEASONAL_GRID = ["add"]
HW_DAMPED_GRID = [False, True]
