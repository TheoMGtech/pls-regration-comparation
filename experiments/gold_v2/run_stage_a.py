"""Reproducible, lightweight Stage A for the isolated Gold V2 experiment.

This program intentionally does not tune models or evaluate the frozen V1 test
set.  It records source provenance, creates causal features, and runs a small
PLS ablation on the pre-existing validation origins only.
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RAW = HERE / "data" / "raw"
PROCESSED = HERE / "data" / "processed"
META = HERE / "data" / "metadata"
OUT = HERE / "outputs"
DOCS = HERE / "docs"
CONFIG = HERE / "config"
V1_BASE = ROOT / "bases" / "grupo5" / "gold_daily_modeling.csv"
V1_OUT = ROOT / "analyses" / "grupo5" / "outputs"

FRED = {
    "DTWEXB": {"variable": "usd_broad_index", "institution": "Federal Reserve Board / FRED", "unit": "index", "track": "A"},
    "VIXCLS": {"variable": "vix", "institution": "Cboe / FRED", "unit": "index", "track": "A"},
    "NASDAQCOM": {"variable": "nasdaq_composite", "institution": "Nasdaq / FRED", "unit": "index", "track": "A"},
    "DGS2": {"variable": "treasury_2y", "institution": "U.S. Treasury / FRED", "unit": "percent", "track": "A"},
    "DCOILWTICO": {"variable": "wti", "institution": "EIA / FRED", "unit": "USD per barrel", "track": "A"},
    "DFII10": {"variable": "real_10y", "institution": "U.S. Treasury / FRED", "unit": "percent", "track": "B"},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def make_dirs() -> None:
    for path in (RAW, PROCESSED, META, OUT / "diagnostics", OUT / "ablation", OUT / "models", OUT / "comparisons", OUT / "figures", DOCS, CONFIG):
        path.mkdir(parents=True, exist_ok=True)


def snapshot_v1() -> pd.DataFrame:
    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    prefixes = ("analyses/grupo5/", "bases/grupo5/", "bases/grupo5-tratamento/")
    rows = []
    for rel in tracked:
        if not rel.startswith(prefixes):
            continue
        path = ROOT / rel
        if path.is_file():
            rows.append({"arquivo": path.name, "caminho": rel.replace("\\", "/"), "sha256": sha256(path), "tamanho": path.stat().st_size})
    frame = pd.DataFrame(rows).sort_values("caminho")
    frame.to_csv(HERE / "v1_reference_checksums.csv", index=False, encoding="utf-8")
    return frame


def download_fred(series_id: str) -> tuple[Path, dict]:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    target = RAW / f"{series_id}.csv"
    # curl is used here because it is available in the project Windows host and
    # provides bounded connection/read timeouts for an external download.
    subprocess.run(["curl.exe", "-L", "--fail", "--silent", "--show-error", "--connect-timeout", "15", "--max-time", "60", "-o", str(target), url], check=True)
    raw = pd.read_csv(target)
    raw.columns = [str(c).strip() for c in raw.columns]
    date_col = "observation_date" if "observation_date" in raw.columns else raw.columns[0]
    value_col = series_id if series_id in raw.columns else raw.columns[-1]
    parsed = pd.to_datetime(raw[date_col], errors="coerce")
    values = pd.to_numeric(raw[value_col], errors="coerce")
    clean = pd.DataFrame({"event_date": parsed, "value": values}).dropna().sort_values("event_date")
    clean.to_csv(PROCESSED / f"{series_id}_clean.csv", index=False)
    meta = {**FRED[series_id], "series_id": series_id, "official_url": f"https://fred.stlouisfed.org/series/{series_id}", "download_url": url,
            "frequency": "daily", "first_date": clean.event_date.min().date().isoformat(), "last_date": clean.event_date.max().date().isoformat(),
            "downloaded_at_utc": datetime.now(timezone.utc).isoformat(), "timezone_or_time": "daily observation; closing/publication time not assumed",
            "availability_rule": "available_date is conservatively the next calendar day after event_date; backward as-of only", "required_lag": "minimum 1 calendar day",
            "license_notes": "FRED redistributes the named institutional series; consult the official series page for current terms.", "raw_sha256": sha256(target), "raw_bytes": target.stat().st_size,
            "status": "downloaded"}
    return target, meta


def fetch_sources() -> list[dict]:
    entries = []
    for series_id in FRED:
        try:
            _, entry = download_fred(series_id)
        except Exception as exc:  # provenance must include failures too
            entry = {**FRED[series_id], "series_id": series_id, "official_url": f"https://fred.stlouisfed.org/series/{series_id}",
                     "download_url": f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}", "status": "failed", "error": f"{type(exc).__name__}: {exc}"}
        entries.append(entry)
    gold_hash = sha256(V1_BASE)
    entries.insert(0, {"variable": "gold_target_reference", "series_id": "V1_GOLD_PRICE", "institution": "V1 frozen dataset", "official_url": None,
                       "download_url": None, "frequency": "next market observation", "unit": "USD per troy ounce", "first_date": "1968-04-29", "last_date": "2014-12-30",
                       "downloaded_at_utc": None, "timezone_or_time": "London PM fixing as documented by V1", "availability_rule": "existing V1 contract; not redownloaded", "required_lag": "not applicable",
                       "license_notes": "No redistribution or replacement in V2.", "raw_sha256": gold_hash, "raw_bytes": V1_BASE.stat().st_size, "status": "referenced_not_copied"})
    (CONFIG / "sources.json").write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    return entries


def external_asof(gold: pd.DataFrame, series_id: str) -> pd.Series:
    path = PROCESSED / f"{series_id}_clean.csv"
    if not path.exists():
        return pd.Series(np.nan, index=gold.index, dtype=float)
    ext = pd.read_csv(path, parse_dates=["event_date"]).sort_values("event_date")
    # When the timestamp is unknown, a daily close is only admitted from the following calendar day.
    ext["available_date"] = ext["event_date"] + pd.Timedelta(days=1)
    left = gold[["DATE"]].rename(columns={"DATE": "forecast_origin"}).sort_values("forecast_origin")
    joined = pd.merge_asof(left, ext[["available_date", "event_date", "value"]].sort_values("available_date"), left_on="forecast_origin", right_on="available_date", direction="backward")
    return pd.Series(joined["value"].to_numpy(), index=gold.sort_values("DATE").index).reindex(gold.index)


def make_features() -> pd.DataFrame:
    gold = pd.read_csv(V1_BASE, parse_dates=["DATE"]).sort_values("DATE").reset_index(drop=True)
    for sid in FRED:
        gold[sid] = external_asof(gold, sid)
    p = gold["GOLD_PRICE"]
    gold["GOLD_DELTA"] = gold["TARGET"] - p
    gold["GOLD_RETURN"] = gold["TARGET"] / p - 1
    gold["GOLD_LOG_RETURN"] = np.log(gold["TARGET"] / p)
    historical_return = np.log(p / p.shift(1))
    gold["gold_log_return"] = historical_return
    for lag in (1, 2, 3, 5, 10, 20): gold[f"gold_ret_lag{lag}"] = historical_return.shift(lag)
    for window in (5, 10, 20, 60): gold[f"gold_momentum_{window}"] = p / p.shift(window) - 1
    for window in (5, 20, 60): gold[f"gold_rv_{window}"] = historical_return.rolling(window).std()
    for window in (5, 20): gold[f"distance_ma{window}"] = p / p.rolling(window).mean() - 1
    for sid, prefix in (("DTWEXB", "usd"), ("VIXCLS", "vix"), ("NASDAQCOM", "equity"), ("DGS2", "dgs2"), ("DCOILWTICO", "wti"), ("DFII10", "real10y")):
        x = gold[sid]
        if sid in ("DTWEXB", "VIXCLS", "NASDAQCOM", "DCOILWTICO"):
            r = np.log(x / x.shift(1)); gold[f"{prefix}_log_return"] = r
            gold[f"{prefix}_return_lag1"] = r.shift(1); gold[f"{prefix}_return_lag2"] = r.shift(2); gold[f"{prefix}_momentum_5"] = x / x.shift(5) - 1
        if sid == "VIXCLS":
            gold["vix_log"] = np.log(x); gold["vix_dlog"] = np.log(x / x.shift(1)); gold["vix_lag1"] = x.shift(1); gold["vix_lag2"] = x.shift(2)
            gold["vix_percentile_252"] = x.rolling(252).rank(pct=True); gold["high_vix"] = (gold["vix_percentile_252"] >= .8).astype(float)
        if sid == "NASDAQCOM":
            gold["equity_return"] = np.log(x / x.shift(1)); gold["equity_return_lag1"] = gold["equity_return"].shift(1); gold["equity_return_lag2"] = gold["equity_return"].shift(2)
            gold["equity_momentum_5"] = x / x.shift(5) - 1; gold["equity_drawdown"] = x / x.rolling(252).max() - 1; gold["negative_equity_return"] = (gold["equity_return"] < 0).astype(float)
        if sid == "DGS2":
            gold["dgs2_change_bp"] = x.diff() * 100; gold["dgs2_lag1"] = x.shift(1); gold["dgs2_change_lag1"] = gold["dgs2_change_bp"].shift(1)
            gold["yield_curve_slope"] = gold["TREASURY_10Y"] - x
        if sid == "DCOILWTICO":
            gold["wti_log_return"] = np.log(x / x.shift(1)); gold["wti_return_lag1"] = gold["wti_log_return"].shift(1); gold["wti_return_lag2"] = gold["wti_log_return"].shift(2)
            gold["wti_momentum_5"] = x / x.shift(5) - 1; gold["wti_volatility_20"] = gold["wti_log_return"].rolling(20).std()
        if sid == "DFII10":
            gold["real10y"] = x; gold["real10y_change_bp"] = x.diff() * 100; gold["real10y_lag1"] = x.shift(1); gold["real10y_change_lag1"] = gold["real10y_change_bp"].shift(1)
    gold.to_csv(PROCESSED / "gold_v2_features.csv", index=False)
    availability = pd.DataFrame([{"series_id": sid, "event_date": None, "available_date_rule": "event_date + 1 calendar day", "merge": "merge_asof(direction=backward)", "same_day_allowed": False} for sid in FRED])
    availability.to_csv(META / "external_availability_rules.csv", index=False)
    coverage = []
    for sid in FRED:
        present = gold.loc[gold[sid].notna(), "DATE"]
        coverage.append({"series_id": sid, "non_null_rows_after_availability_lag": len(present), "first_available_for_origin": present.min().date().isoformat() if len(present) else None, "last_available_for_origin": present.max().date().isoformat() if len(present) else None})
    pd.DataFrame(coverage).to_csv(OUT / "diagnostics" / "external_coverage.csv", index=False)
    correlation_cols = ["GOLD_LOG_RETURN", "DTWEXB", "VIXCLS", "NASDAQCOM", "DGS2", "DCOILWTICO", "DFII10", "usd_log_return", "vix_dlog", "equity_return", "dgs2_change_bp", "wti_log_return", "real10y_change_bp"]
    gold[[c for c in correlation_cols if c in gold]].corr(numeric_only=True).loc[["GOLD_LOG_RETURN"]].T.rename(columns={"GOLD_LOG_RETURN": "correlation_with_gold_log_return"}).to_csv(OUT / "diagnostics" / "core_feature_correlations.csv")
    return gold


def official_test_indices() -> list[int]:
    protocol = json.loads((V1_OUT / "protocol.json").read_text(encoding="utf-8"))
    return protocol["origins"]["test"]


def write_diagnostics(gold: pd.DataFrame) -> None:
    test = gold.iloc[official_test_indices()].copy()
    def stats(frame: pd.DataFrame, label: str) -> dict:
        delta, ret = frame.GOLD_DELTA, frame.GOLD_RETURN
        return {"period": label, "n_origins": len(frame), "mean_delta": delta.mean(), "median_delta": delta.median(), "std_delta": delta.std(), "min_delta": delta.min(), "max_delta": delta.max(),
                "p10_delta": delta.quantile(.1), "p25_delta": delta.quantile(.25), "p75_delta": delta.quantile(.75), "p90_delta": delta.quantile(.9), "p95_delta": delta.quantile(.95),
                "mean_abs_daily_move": delta.abs().mean(), "median_abs_daily_move": delta.abs().median(), "mean_abs_return": ret.abs().mean(), "return_volatility": ret.std(), "return_skewness": ret.skew(), "return_kurtosis": ret.kurt()}
    pd.DataFrame([stats(gold, "full_v1_reference"), stats(test, "official_test_296")]).to_csv(OUT / "diagnostics" / "target_difficulty_summary.csv", index=False)
    metrics = pd.read_csv(V1_OUT / "metrics.csv")
    natural = test.GOLD_DELTA.abs().mean(); median_move = test.GOLD_DELTA.abs().median(); price_mean = test.GOLD_PRICE.mean(); price_median = test.GOLD_PRICE.median(); change_std = test.GOLD_DELTA.std()
    rows = []
    for row in metrics.itertuples():
        rows.append({"model": row.model, "mae_usd_oz": row.mae, "mean_abs_daily_move": natural, "mae_over_mean_abs_daily_move": row.mae / natural, "mae_over_mean_price": row.mae / price_mean, "mae_over_median_price": row.mae / price_median, "mae_over_std_change": row.mae / change_std, "mae_over_median_abs_move": row.mae / median_move})
    rows.append({"model": "Persistence_recalculated", "mae_usd_oz": natural, "mean_abs_daily_move": natural, "mae_over_mean_abs_daily_move": 1.0, "mae_over_mean_price": natural / price_mean, "mae_over_median_price": natural / price_median, "mae_over_std_change": natural / change_std, "mae_over_median_abs_move": natural / median_move})
    pd.DataFrame(rows).to_csv(OUT / "diagnostics" / "mae_context.csv", index=False)
    gold[["DATE", "GOLD_PRICE", "TARGET", "GOLD_DELTA", "GOLD_RETURN", "GOLD_LOG_RETURN"]].to_csv(OUT / "diagnostics" / "target_series.csv", index=False)


def run_light_ablation(gold: pd.DataFrame) -> None:
    protocol = json.loads((V1_OUT / "protocol.json").read_text(encoding="utf-8"))
    # The full 296-origin ablation belongs to Stage B. Stage A is a deliberately
    # small, evenly-spaced 12-origin feasibility screen; it is never presented
    # as a final model comparison.
    origins = protocol["origins"]["validation"][::25]
    technical = [c for c in gold if c.startswith(("gold_", "distance_"))]
    blocks = {"A1_gold_price": ["GOLD_PRICE"], "A2_v1_complete": protocol["candidate_features"], "A3_gold_technical_no_raw": technical,
              "A4_exogenous_only": ["DTWEXB", "VIXCLS", "NASDAQCOM", "DGS2", "DCOILWTICO", "TREASURY_10Y", "FED_FUNDS_RATE"],
              "A5_technical_usd": technical + ["DTWEXB", "usd_log_return", "usd_return_lag1", "usd_return_lag2", "usd_momentum_5"],
              "A6_technical_usd_rates": technical + ["DTWEXB", "dgs2_lag1", "dgs2_change_lag1", "yield_curve_slope", "TREASURY_10Y", "FED_FUNDS_RATE"],
              "A7_technical_usd_rates_risk": technical + ["DTWEXB", "dgs2_lag1", "dgs2_change_lag1", "yield_curve_slope", "VIXCLS", "vix_lag1", "vix_percentile_252"],
              "A8_technical_all_core": technical + ["DTWEXB", "usd_log_return", "VIXCLS", "vix_lag1", "NASDAQCOM", "equity_return_lag1", "DGS2", "dgs2_lag1", "yield_curve_slope", "DCOILWTICO", "wti_return_lag1"]}
    results = []
    for name, features in {"A0_persistence": [] , **blocks}.items():
        errors, hits, used = [], [], 0
        for origin in origins:
            row = gold.iloc[origin]; train = gold.iloc[:origin].dropna(subset=features + ["TARGET"]) if features else gold.iloc[:origin]
            if name == "A0_persistence": pred = row.GOLD_PRICE
            elif len(train) < 100 or row[features].isna().any(): continue
            else:
                scaler = StandardScaler(); x = scaler.fit_transform(train[features]); x0 = scaler.transform(row[features].to_frame().T)
                model = PLSRegression(n_components=min(2, len(features), len(train) - 1)); model.fit(x, train.TARGET); pred = float(np.asarray(model.predict(x0)).reshape(-1)[0])
            errors.append(abs(row.TARGET - pred)); hits.append(int(np.sign(pred - row.GOLD_PRICE) == np.sign(row.TARGET - row.GOLD_PRICE))); used += 1
        results.append({"experiment": name, "evaluation": "light_validation_screen_12_evenly_spaced_origins_not_final_test", "model": "persistence" if name == "A0_persistence" else "PLSRegression_fixed_2_components", "n_features": len(features), "n_origins": used, "mae_usd_oz": np.mean(errors), "directional_accuracy": np.mean(hits), "relative_to_persistence_pct": np.nan})
    frame = pd.DataFrame(results); baseline = frame.loc[frame.experiment == "A0_persistence", "mae_usd_oz"].iloc[0]; frame["difference_absolute_vs_persistence"] = frame.mae_usd_oz - baseline; frame["difference_percent_vs_persistence"] = 100 * frame.difference_absolute_vs_persistence / baseline
    frame.to_csv(OUT / "ablation" / "ablation_results.csv", index=False)
    (CONFIG / "feature_blocks.json").write_text(json.dumps(blocks, ensure_ascii=False, indent=2), encoding="utf-8")


def write_protocol(gold: pd.DataFrame, sources: list[dict]) -> None:
    record = {"version": "v2-stage-a", "status": "stage_a_complete_pending_human_approval", "heavy_stage_authorized": False, "base_reference": str(V1_BASE.relative_to(ROOT)).replace("\\", "/"), "base_reference_sha256": sha256(V1_BASE),
              "tracks": {"A": "1995-2014 core, subject to observed external coverage", "B": "DFII10 rich real yield, separate 2003-2014 comparable subset", "C": "EPU/GPR exploratory retrospective; not downloaded in Stage A"},
              "forecast_origin_rule": "external values use available_date=event_date+1 calendar day and merge_asof backward; no forward/backfill or nearest merge", "targets": {"LEVEL": "TARGET", "DELTA": "TARGET-GOLD_PRICE", "LOG_RETURN": "log(TARGET/GOLD_PRICE)"},
              "stage_a_models": "persistence plus fixed two-component PLS on validation origins only; no tuning, no test evaluation", "source_status": {x["series_id"]: x["status"] for x in sources}, "feature_rows": len(gold)}
    (CONFIG / "protocol_v2.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    make_dirs(); before = snapshot_v1(); sources = fetch_sources(); gold = make_features(); write_diagnostics(gold); run_light_ablation(gold); write_protocol(gold, sources)
    after = snapshot_v1(); equal = before.equals(after); assert equal, "V1 checksum snapshot changed during Stage A"
    (META / "v1_checksum_verification.json").write_text(json.dumps({"v1_files_checked": len(after), "byte_identical": equal, "checked_at_utc": datetime.now(timezone.utc).isoformat()}, indent=2), encoding="utf-8")
    print(json.dumps({"v1_files": len(after), "sources": {s["series_id"]: s["status"] for s in sources}, "feature_rows": len(gold)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
