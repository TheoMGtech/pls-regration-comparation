"""Implementação específica da PLS Regression com escalonamento interno."""
from __future__ import annotations

import numpy as np
from sklearn.cross_decomposition import PLSRegression

DEFAULT_GRID = {"n_components": [2, 4, 8, 16, 32]}


def fit_pls(X, y, *, n_components=8, max_iter=500, tol=1e-06):
    X_values = np.asarray(X, dtype=float)
    y_values = np.asarray(y, dtype=float)
    if not np.isfinite(X_values).all() or not np.isfinite(y_values).all():
        raise ValueError("PLS não aceita NaN nos dados de treino.")
    if n_components < 1 or n_components > min(X_values.shape):
        raise ValueError("n_components deve estar entre 1 e min(n_amostras, n_features).")
    model = PLSRegression(
        n_components=n_components,
        scale=True,
        max_iter=max_iter,
        tol=tol,
    )
    return model.fit(X_values, y_values)


def forecast_pls(X_train, y_train, X_future, *, n_components=8, **config):
    fitted = fit_pls(X_train, y_train, n_components=n_components, **config)
    return np.asarray(fitted.predict(np.asarray(X_future, dtype=float))).reshape(-1)
