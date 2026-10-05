"""Parâmetros fixos da Base 2 — Bruna Cardoso."""

from pathlib import Path

GROUP = "grupo2"
OWNER = "Bruna Carvalho Cardoso"
RANDOM_STATE = 67
TRAIN_RATIO = 0.80
HORIZON = 1  # 1 hora à frente
FREQ = "h"
SEASONAL_PERIOD = 24  # sazonalidade diária em série horária
WEEKLY_PERIOD = 168

# O split externo continua 80/20. Dentro dos 80% iniciais, os últimos
# 12,5% formam a validação (equivale a 70/10/20 do total).
INNER_TRAIN_RATIO = 0.875

# Origens sistemáticas. O passo 11 é coprimo de 24,
# portanto percorrem todas as horas do dia. A validação reforçada fica próxima
# das 296 origens usadas pelo protocolo de referência do Grupo 5.
TEST_ORIGIN_STEP = 11
VALIDATION_ORIGIN_STEP = 11
SARIMAX_VALIDATION_ORIGIN_STEP = VALIDATION_ORIGIN_STEP

# Caminhos — tudo vive em analyses/grupo2/
GROUP_DIR = Path(__file__).resolve().parent
ROOT = GROUP_DIR.parents[1]
RAW_PATH = ROOT / "bases" / GROUP / "Metro_Interstate_Traffic_Volume.csv"
OUTPUT_DIR = GROUP_DIR / "outputs"
DATA_DIR = OUTPUT_DIR / "data"
FIG_DIR = OUTPUT_DIR / "figures"
MODEL_DIR = OUTPUT_DIR / "models"
RESULT_DIR = OUTPUT_DIR / "results"
NOTEBOOKS_DIR = GROUP_DIR

# Caminhos relativos dos notebooks até outputs/
NOTEBOOK_OUTPUTS_REL = "../outputs"  # 01/03/04/05
NOTEBOOK_OUTPUTS_REL_MODELS = "../../outputs"  # 02_modelos/*

TARGET = "traffic_volume"
DATETIME_COL = "date_time"

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
    "y_lag_2",
    "y_lag_3",
    "y_lag_6",
    "y_lag_12",
    "y_lag_23",
    "y_lag_24",
    "y_lag_25",
    "y_lag_48",
    "y_lag_72",
    "y_lag_167",
    "y_lag_168",
    "y_lag_169",
    "y_lag_336",
    "y_roll_mean_6",
    "y_roll_std_6",
    "y_roll_mean_24",
    "y_roll_std_24",
    "y_roll_mean_168",
    "y_roll_std_168",
    "temp_lag_1",
    "rain_lag_1",
    "snow_lag_1",
    "clouds_lag_1",
    "observed_lag_1",
    "observed_lag_24",
    "observed_lag_168",
    "observed_lag_336",
]

PLS_FEATURE_SETS = {
    "full": FEATURE_COLS,
    "no_weather": [
        feature
        for feature in FEATURE_COLS
        if feature
        not in {"temp_lag_1", "rain_lag_1", "snow_lag_1", "clouds_lag_1"}
    ],
    "compact": [
        feature
        for feature in FEATURE_COLS
        if feature
        not in {
            "month_sin",
            "month_cos",
            "rain_lag_1",
            "snow_lag_1",
            "clouds_lag_1",
            "y_roll_mean_168",
            "y_roll_std_168",
        }
    ],
}

SARIMAX_EXOG = [
    "hour_sin",
    "hour_cos",
    "dow_sin",
    "dow_cos",
    "is_holiday",
    "is_weekend",
    "temp_lag_1",
    "rain_lag_1",
    "clouds_lag_1",
]

# Janela móvel por modelo. Em cada origem o modelo é reajustado e prevê
# exclusivamente a próxima hora. A janela móvel evita que a série horária
# torne cada ajuste inviável e permite adaptação a drift.
SARIMAX_MAX_TRAIN = 24 * 60
HW_MAX_TRAIN = 24 * 120
ML_MAX_TRAIN = 24 * 180

# Combinações dirigidas, à semelhança do protocolo do Theo.
RF_CANDIDATES = [
    # Exploração local em torno da melhor região encontrada na execução v2.
    {"n_estimators": 600, "max_depth": 24, "min_samples_split": 5, "min_samples_leaf": 1, "max_features": "sqrt"},
    {"n_estimators": 900, "max_depth": 24, "min_samples_split": 5, "min_samples_leaf": 1, "max_features": "sqrt"},
    {"n_estimators": 600, "max_depth": None, "min_samples_split": 5, "min_samples_leaf": 1, "max_features": "sqrt"},
    {"n_estimators": 600, "max_depth": 20, "min_samples_split": 2, "min_samples_leaf": 1, "max_features": "sqrt"},
    {"n_estimators": 600, "max_depth": 24, "min_samples_split": 2, "min_samples_leaf": 2, "max_features": "sqrt"},
    {"n_estimators": 900, "max_depth": None, "min_samples_split": 2, "min_samples_leaf": 1, "max_features": "sqrt"},
    {"n_estimators": 600, "max_depth": 24, "min_samples_split": 5, "min_samples_leaf": 1, "max_features": 0.3},
    {"n_estimators": 300, "max_depth": 20, "min_samples_split": 2, "min_samples_leaf": 2, "max_features": 1.0},
    {"n_estimators": 500, "max_depth": 24, "min_samples_split": 2, "min_samples_leaf": 1, "max_features": 0.7},
    {"n_estimators": 300, "max_depth": None, "min_samples_split": 2, "min_samples_leaf": 1, "max_features": 1.0},
    {"n_estimators": 500, "max_depth": 20, "min_samples_split": 5, "min_samples_leaf": 2, "max_features": 1.0},
    {"n_estimators": 300, "max_depth": 16, "min_samples_split": 5, "min_samples_leaf": 3, "max_features": 0.7},
]

PLS_COMPONENTS_GRID = list(range(1, 33))

# 72 estruturas: 18 ordens regulares x 4 ordens sazonais; triagem por BIC,
# seguida de walk-forward nos melhores candidatos.
SARIMAX_REGULAR_ORDERS = [
    (p, d, q)
    for p in (0, 1, 2)
    for d in (0, 1)
    for q in (0, 1, 2)
]
SARIMAX_SEASONAL_ORDERS = [
    (0, 0, 0, SEASONAL_PERIOD),
    (1, 0, 0, SEASONAL_PERIOD),
    (0, 0, 1, SEASONAL_PERIOD),
    (0, 1, 1, SEASONAL_PERIOD),
]
SARIMAX_SCREEN_TOP_N = 5

HW_CANDIDATES = [
    {
        "trend": trend,
        "seasonal": seasonal,
        "damped_trend": damped,
        "seasonal_periods": period,
        "max_train_rows": window,
    }
    for window in (24 * 60, 24 * 120, 24 * 180)
    for period in (SEASONAL_PERIOD, WEEKLY_PERIOD)
    for trend in (None, "add")
    for seasonal in ("add",)
    for damped in (False, True)
    if not (trend is None and damped)
]
