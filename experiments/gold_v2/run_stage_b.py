"""Checkpointed Stage B worker. Runs only while the Windows host is awake."""
from __future__ import annotations
import json, time, traceback
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
OUT = HERE / 'outputs' / 'models'; OUT.mkdir(parents=True, exist_ok=True)
STATE = OUT / 'stage_b_state.json'; LOG = OUT / 'stage_b.log'

def event(message):
    stamp = datetime.now(timezone.utc).isoformat(); LOG.open('a', encoding='utf-8').write(f'{stamp} {message}\n'); print(message, flush=True)

def save(state): STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')

def main():
    import subprocess, sys
    feature_file = HERE / 'data' / 'processed' / 'gold_v2_features.csv'
    if not feature_file.exists(): subprocess.run([sys.executable, str(HERE / 'run_stage_a.py')], check=True)
    d = pd.read_csv(feature_file); protocol = json.loads((HERE.parents[1] / 'analyses/grupo5/outputs/protocol.json').read_text(encoding='utf-8'))
    d['target_delta'] = d.TARGET - d.GOLD_PRICE; d['target_log_return'] = np.log(d.TARGET / d.GOLD_PRICE)
    a2 = protocol['candidate_features']; a8 = json.loads((HERE / 'config/feature_blocks.json').read_text(encoding='utf-8'))['A8_technical_all_core']
    plans = [('PLS_A2_LEVEL', 'pls', a2, 'TARGET'), ('PLS_A8_LEVEL', 'pls', a8, 'TARGET'), ('RF_A2_LEVEL_V1', 'rf', a2, 'TARGET'), ('RF_A8_LEVEL_V1', 'rf', a8, 'TARGET')]
    state = json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else {'status':'running','completed':[], 'started_at_utc':datetime.now(timezone.utc).isoformat(), 'scope':'Stage B core Track A; checkpointed'}
    for name, kind, features, target in plans:
        if name in state['completed']: continue
        event('START '+name); rows=[]
        for origin in protocol['origins']['test']:
            train = d.iloc[:origin].dropna(subset=features+[target]); row=d.iloc[origin]
            if row[features].isna().any(): continue
            if kind == 'pls':
                sc=StandardScaler(); x=sc.fit_transform(train[features]); model=PLSRegression(n_components=min(11,len(features),len(train)-1)); model.fit(x,train[target]); pred=float(np.asarray(model.predict(sc.transform(row[features].to_frame().T))).reshape(-1)[0])
            else:
                model=RandomForestRegressor(n_estimators=300,max_depth=20,min_samples_split=10,min_samples_leaf=5,max_features=1.0,random_state=42,n_jobs=-1); model.fit(train[features],train[target]); pred=float(model.predict(row[features].to_frame().T)[0])
            rows.append({'model_run':name,'origin_index':origin,'y_true':row.TARGET,'y_pred_price':pred,'abs_error_usd_oz':abs(row.TARGET-pred)})
            if len(rows)%25==0: pd.DataFrame(rows).to_csv(OUT/f'{name}_partial.csv',index=False); state['current']={'job':name,'origins_done':len(rows)}; save(state)
        frame=pd.DataFrame(rows); frame.to_csv(OUT/f'{name}_predictions.csv',index=False)
        summary={'model_run':name,'n_origins':len(frame),'mae_usd_oz':float(frame.abs_error_usd_oz.mean()),'completed_at_utc':datetime.now(timezone.utc).isoformat()}
        pd.DataFrame([summary]).to_csv(OUT/f'{name}_metrics.csv',index=False); state['completed'].append(name); state.pop('current',None); save(state); event('DONE '+json.dumps(summary))
    state['status']='core_track_a_completed'; state['completed_at_utc']=datetime.now(timezone.utc).isoformat(); save(state)

if __name__ == '__main__':
    try: main()
    except Exception:
        STATE.write_text(json.dumps({'status':'failed','traceback':traceback.format_exc(),'failed_at_utc':datetime.now(timezone.utc).isoformat()},ensure_ascii=False,indent=2),encoding='utf-8'); raise
