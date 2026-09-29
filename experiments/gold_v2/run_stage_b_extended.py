"""Resumable Stage B: fixed-configuration PLS/RF target and ablation matrix.

No test result changes features or hyperparameters. Outputs are checkpoints only.
"""
from __future__ import annotations
import json, time, traceback
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]; OUT=HERE/'outputs'/'models'; OUT.mkdir(parents=True,exist_ok=True)
STATE=OUT/'stage_b_extended_state.json'; LOG=OUT/'stage_b_extended.log'; MATRIX=OUT/'consolidated_matrix.csv'
def stamp(): return datetime.now(timezone.utc).isoformat()
def log(x): LOG.open('a',encoding='utf-8').write(f'{stamp()} {x}\n')
def save(x): STATE.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def targets(row, name, pred):
    if name=='LEVEL': return pred, row.TARGET, pred, row.TARGET
    if name=='DELTA': return row.GOLD_PRICE+pred, row.TARGET-row.GOLD_PRICE, pred, row.TARGET
    return row.GOLD_PRICE*np.exp(pred), np.log(row.TARGET/row.GOLD_PRICE), pred, row.TARGET

def run_job(d, origins, model_name, target_name, feature_name, features):
    path=OUT/f'{model_name}_{target_name}_{feature_name}_predictions.csv'
    if path.exists(): return pd.read_csv(path)
    native={'LEVEL':'TARGET','DELTA':'target_delta','LOG_RETURN':'target_log_return'}[target_name]; rows=[]; started=time.perf_counter(); log(f'START {model_name} {target_name} {feature_name}')
    for n,origin in enumerate(origins,1):
        row=d.iloc[origin]; train=d.iloc[:origin].dropna(subset=features+[native])
        if row[features].isna().any(): continue
        if model_name=='PLS':
            scaler=StandardScaler(); x=scaler.fit_transform(train[features]); model=PLSRegression(n_components=min(11,len(features),len(train)-1)); model.fit(x,train[native]); pred=float(np.asarray(model.predict(scaler.transform(row[features].to_frame().T))).reshape(-1)[0])
        else:
            model=RandomForestRegressor(n_estimators=300,max_depth=20,min_samples_split=10,min_samples_leaf=5,max_features=1.0,random_state=42,n_jobs=-1); model.fit(train[features],train[native]); pred=float(model.predict(row[features].to_frame().T)[0])
        price,native_true,native_pred,true=targets(row,target_name,pred); rows.append({'origin_index':origin,'target_date':row.DATE,'y_true_price':true,'y_pred_price':price,'y_true_native':native_true,'y_pred_native':native_pred,'abs_error_usd':abs(true-price),'abs_error_native':abs(native_true-native_pred),'direction_correct':int(np.sign(price-row.GOLD_PRICE)==np.sign(true-row.GOLD_PRICE))})
        if n%25==0: pd.DataFrame(rows).to_csv(path.with_name(path.stem+'_partial.csv'),index=False)
    frame=pd.DataFrame(rows); frame.to_csv(path,index=False)
    metric={'model':model_name,'target':target_name,'feature_set':feature_name,'mae_usd':frame.abs_error_usd.mean(),'mae_native':frame.abs_error_native.mean(),'directional_accuracy':frame.direction_correct.mean(),'n_features':len(features),'n_origins':len(frame),'elapsed_seconds':time.perf_counter()-started,'directly_comparable_v1':target_name=='LEVEL' and feature_name in ('A1_gold_price','A2_v1_complete'),'methodological_status':'fixed_configuration_post_approval_no_test_retuning'}
    pd.DataFrame([metric]).to_csv(path.with_name(path.stem+'_metrics.csv'),index=False); log('DONE '+json.dumps(metric)); return frame

def main():
    f=HERE/'data'/'processed'/'gold_v2_features.csv'
    if not f.exists(): raise RuntimeError('Stage A processed data unavailable; run run_stage_a.py first.')
    d=pd.read_csv(f); d['target_delta']=d.TARGET-d.GOLD_PRICE; d['target_log_return']=np.log(d.TARGET/d.GOLD_PRICE)
    p=json.loads((ROOT/'analyses/grupo5/outputs/protocol.json').read_text(encoding='utf-8')); blocks=json.loads((HERE/'config/feature_blocks.json').read_text(encoding='utf-8'))
    technical=blocks['A3_gold_technical_no_raw']; full=list(dict.fromkeys(p['candidate_features']+technical+blocks['A8_technical_all_core']))
    groups={'FULL':full,'FULL_without_GOLD_PRICE':[x for x in full if x!='GOLD_PRICE'],'FULL_without_gold_lags':[x for x in full if not x.startswith(('gold_','distance_'))],'FULL_without_USD':[x for x in full if x not in ('DTWEXB','usd_log_return','usd_return_lag1','usd_return_lag2','usd_momentum_5')],'FULL_without_rates':[x for x in full if x not in ('DGS2','TREASURY_10Y','FED_FUNDS_RATE','dgs2_lag1','dgs2_change_lag1','yield_curve_slope')],'FULL_without_risk':[x for x in full if x not in ('VIXCLS','vix_lag1','vix_lag2','vix_percentile_252')],'FULL_without_commodities':[x for x in full if x not in ('DCOILWTICO','wti_log_return','wti_return_lag1','wti_return_lag2','wti_momentum_5','wti_volatility_20')]}
    sets={**blocks,**groups}; state=json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else {'status':'running','started_at_utc':stamp(),'completed':[]}; origins=p['origins']['test']
    # A0 is mathematically persistence / zero return; materialize it once per target.
    for t in ('LEVEL','DELTA','LOG_RETURN'):
        bp=OUT/f'Persistence_{t}_A0_persistence_metrics.csv'
        if not bp.exists():
            rows=[]
            for origin in origins:
                row=d.iloc[origin]; native={'LEVEL':row.GOLD_PRICE,'DELTA':0.0,'LOG_RETURN':0.0}[t]; price,ntrue,npred,true=targets(row,t,native)
                rows.append({'origin_index':origin,'target_date':row.DATE,'y_true_price':true,'y_pred_price':price,'y_true_native':ntrue,'y_pred_native':npred,'abs_error_usd':abs(true-price),'abs_error_native':abs(ntrue-npred),'direction_correct':int(np.sign(price-row.GOLD_PRICE)==np.sign(true-row.GOLD_PRICE))})
            frame=pd.DataFrame(rows); frame.to_csv(bp.with_name(bp.name.replace('_metrics','_predictions')),index=False)
            pd.DataFrame([{'model':'Persistence','target':t,'feature_set':'A0_persistence','mae_usd':frame.abs_error_usd.mean(),'mae_native':frame.abs_error_native.mean(),'directional_accuracy':frame.direction_correct.mean(),'n_features':0,'n_origins':len(frame),'elapsed_seconds':0.0,'directly_comparable_v1':t=='LEVEL','methodological_status':'fixed_persistence_baseline'}]).to_csv(bp,index=False)
    # PLS: complete matrix; RF: all targets, core comparison and block-drop ablations. No grid expansion.
    jobs=[('PLS',t,s,x) for t in ('LEVEL','DELTA','LOG_RETURN') for s,x in sets.items()]+[('RF',t,s,sets[s]) for t in ('LEVEL','DELTA','LOG_RETURN') for s in ('A1_gold_price','A2_v1_complete','A3_gold_technical_no_raw','A4_exogenous_only','A5_technical_usd','A6_technical_usd_rates','A7_technical_usd_rates_risk','A8_technical_all_core','FULL','FULL_without_GOLD_PRICE','FULL_without_gold_lags','FULL_without_USD','FULL_without_rates','FULL_without_risk','FULL_without_commodities')]
    for model,t,s,x in jobs:
        key=f'{model}_{t}_{s}'
        if key in state['completed']: continue
        state['current']=key; save(state); run_job(d,origins,model,t,s,x); state['completed'].append(key); state.pop('current',None); save(state)
    metrics=[]
    for q in OUT.glob('*_metrics.csv'):
        try: metrics.append(pd.read_csv(q))
        except Exception: pass
    if metrics: pd.concat(metrics,ignore_index=True).drop_duplicates(['model','target','feature_set'],keep='last').to_csv(MATRIX,index=False)
    state['status']='matrix_models_completed'; state['completed_at_utc']=stamp(); save(state)
if __name__=='__main__':
    try: main()
    except Exception:
        STATE.write_text(json.dumps({'status':'failed','traceback':traceback.format_exc(),'failed_at_utc':stamp()},ensure_ascii=False,indent=2),encoding='utf-8'); raise
