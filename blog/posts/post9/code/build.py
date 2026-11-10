"""Frozen classroom replication and validation-selected extension. No test-driven tuning."""
from pathlib import Path
import json,hashlib,platform,math
import numpy as np
import pandas as pd
from scipy import stats
import xgboost as xgb
P=Path(__file__).resolve().parents[1]; O=P/'results'; O.mkdir(exist_ok=True)
config=json.loads((P/'data/design.json').read_text())
# A compact public snapshot makes all analysis reproducible offline.
snapshot=P/'data/prices.csv.gz'
if not snapshot.exists():
 rows=[]
 for f in sorted((P/'data/raw').glob('*.json')):
  if f.name=='manifest.json':continue
  r=json.loads(f.read_text())['chart']['result'][0];q=r['indicators']['quote'][0]
  for i,ts in enumerate(r['timestamp']):
   rows.append({'symbol':f.stem,'date':pd.Timestamp(ts,unit='s',tz='UTC').strftime('%Y-%m-%d'),**{k:q[k][i] for k in ['open','high','low','close','volume']},'adjusted':r['indicators']['adjclose'][0]['adjclose'][i]})
 pd.DataFrame(rows).to_csv(snapshot,index=False,float_format='%.9g',compression={'method':'gzip','mtime':0})
a=pd.read_csv(snapshot,parse_dates=['date']); assert not a.duplicated(['symbol','date']).any()
assert not a.isna().any().any(); assert (a[['open','high','low','close','adjusted']]>0).all().all()
spy=a[a.symbol=='SPY'].sort_values('date').set_index('date'); calendar=spy.index
stocks=sorted(set(a.symbol)-{'SPY'})
assert all(a[a.symbol==s].set_index('date').index.equals(calendar) for s in stocks)
parts=[]
for s in stocks:
 d=a[a.symbol==s].sort_values('date').copy().set_index('date'); p=d.adjusted; r=p.pct_change()
 d['return']=r; d['spy_ret']=spy.adjusted.pct_change();d['excess_ret']=r-d.spy_ret
 for k,v in [('mom_1m',21),('mom_3m',63),('mom_6m',126),('ret_5d',5)]:d[k]=p.shift(v)/p.shift(1)-1
 d['vol_1m']=r.shift(1).rolling(22).std(ddof=1)
 # Signals for extension avoid nominal share-price levels and correct momentum direction.
 for k,v in [('trend_1m',21),('trend_3m',63),('trend_6m',126),('trend_5d',5)]:d[k]=p.shift(1)/p.shift(v)-1
 d['lag_excess']=d.excess_ret.shift(1)
 d['target']=p.shift(-20)/p.shift(-1)-1
 d['entry_date']=pd.Series(calendar,index=calendar).shift(-1);d['exit_date']=pd.Series(calendar,index=calendar).shift(-20)
 parts.append(d.reset_index())
df=pd.concat(parts,ignore_index=True).dropna().sort_values(['date','symbol']).reset_index(drop=True)
original=['open','high','low','close','volume','adjusted','return','spy_ret','mom_1m','mom_3m','mom_6m','vol_1m','ret_5d','excess_ret']
extension=['trend_1m','trend_3m','trend_6m','trend_5d','vol_1m','lag_excess']
train=df[(df.date<'2024-01-01')&(df.exit_date<'2024-01-01')]
val=df[(df.date>='2024-01-01')&(df.exit_date<'2025-01-01')]
test=df[(df.date>='2025-01-01')&(df.exit_date<='2025-10-31')]
assert train.exit_date.max()<val.date.min() and val.exit_date.max()<test.date.min()
def fit(features,depth,trees,lam=1):
 m=xgb.XGBRegressor(n_estimators=trees,max_depth=depth,learning_rate=.05,min_child_weight=10,gamma=0,reg_lambda=lam,subsample=1,colsample_bytree=1,objective='reg:squarederror',tree_method='hist',random_state=123,n_jobs=2,base_score=float(train.target.mean()))
 m.fit(train[features],train.target);return m
baseline=fit(original,5,300); selection=[]; fitted=[]
for c in config['candidates']:
 m=fit(extension,c['depth'],c['trees'],c['lambda']);v=m.predict(val[extension]);selection.append({**c,'validation_rmse':float(np.sqrt(np.mean((v-val.target)**2)))});fitted.append(m)
sel=pd.DataFrame(selection); ix=int(sel.validation_rmse.argmin()); improved=fitted[ix]
sel.to_csv(O/'validation_selection.csv',index=False)
# No 2024 refit: both fitted on the identical purged 2022–23 labels.
pred=test[['date','symbol','entry_date','exit_date','target']].copy()
pred['Original']=baseline.predict(test[original]).astype(float);pred['Revised']=improved.predict(test[extension]).astype(float);pred['Training mean']=float(train.target.mean())
pred.to_csv(O/'test_predictions.csv.gz',index=False,compression={'method':'gzip','mtime':0})
metrics=[]
for name in ['Original','Revised','Training mean']:
 y=pred.target.to_numpy(); yhat=pred[name].to_numpy();metrics.append({'model':name,'rmse':float(np.sqrt(np.mean((y-yhat)**2))),'mae':float(np.mean(abs(y-yhat))),'direction_accuracy':float(np.mean((y>0)==(yhat>0)))})
pd.DataFrame(metrics).to_csv(O/'prediction_metrics.csv',index=False)
# Nonoverlapping blocks, exact same next-close entry and +20 close exit for all arms.
dates=sorted(test.date.unique()); signals=dates[::20]; trades=[]; holdings=[]
for date in signals:
 g=pred[pred.date==date].sort_values('symbol');sp=float(spy.loc[g.exit_date.iloc[0],'adjusted']/spy.loc[g.entry_date.iloc[0],'adjusted']-1)
 for name in ['Original','Revised']:
  top=g.sort_values([name,'symbol'],ascending=[False,True]).head(10); pos=top[name].clip(lower=0).to_numpy();w=pos/pos.sum() if pos.sum()>0 else np.ones(len(top))/len(top)
  gross=float(w@top.target.to_numpy())
  trades.append({'signal':date,'entry':top.entry_date.iloc[0],'exit':top.exit_date.iloc[0],'strategy':name,'gross':gross,'net':(1-.001)**2*(1+gross)-1,'cost_bps_each_side':10})
  for (_,r),weight in zip(top.iterrows(),w):holdings.append({'signal':date,'strategy':name,'symbol':r.symbol,'weight':weight,'target':r.target,'prediction':r[name]})
 for name,v in [('Equal weight',float(g.target.mean())),('SPY',sp)]:trades.append({'signal':date,'entry':g.entry_date.iloc[0],'exit':g.exit_date.iloc[0],'strategy':name,'gross':v,'net':(1-.001)**2*(1+v)-1,'cost_bps_each_side':10})
tr=pd.DataFrame(trades); pd.DataFrame(holdings).to_csv(O/'holdings.csv',index=False)
wealth=[]; performances=[]
for name,g in tr.groupby('strategy',sort=False):
 g=g.sort_values('signal').copy();g['gross_wealth']=(1+g.gross).cumprod();g['net_wealth']=(1+g.net).cumprod();wealth.append(g)
 for cost in [0,10,25]:
  ret=(1-cost/10000)**2*(1+g.gross)-1
  performances.append({'strategy':name,'cost_bps_each_side':cost,'cumulative_return':float(np.prod(1+ret)-1),'periods':len(g),'mean_block_return':float(ret.mean()),'worst_block':float(ret.min())})
pd.concat(wealth).to_csv(O/'portfolio_windows.csv',index=False);pd.DataFrame(performances).to_csv(O/'investment_metrics.csv',index=False)
# A genuine buy-and-hold SPY comparator, unlike the matched-window strategy.
passive_gross=float(spy.loc[tr.exit.max(),'adjusted']/spy.loc[tr.entry.min(),'adjusted']-1)
summary_passive={str(cost):(1-cost/10000)**2*(1+passive_gross)-1 for cost in [0,10,25]}
c=pd.read_csv(P/'data/class_results.csv'); d=c.portfolio2-c.portfolio1;tt=stats.ttest_1samp(d,0);ci=stats.t.interval(.95,len(d)-1,loc=d.mean(),scale=stats.sem(d))
class_stats={'pairs':len(c),'intuition_mean':float(c.portfolio1.mean()),'indicator_mean':float(c.portfolio2.mean()),'difference':float(d.mean()),'ci95':list(map(float,ci)),'p_two_sided':float(tt.pvalue),'indicator_wins':int((d>0).sum())}
summary={'class':class_stats,'stocks':len(stocks),'excluded':['BK: Yahoo endpoint returned HTTP 400; excluded before model fitting'],'calendar_start':str(calendar.min().date()),'calendar_end':str(calendar.max().date()),'train_rows':len(train),'val_rows':len(val),'test_rows':len(test),'train_signal_end':str(train.date.max().date()),'train_label_end':str(train.exit_date.max().date()),'val_label_end':str(val.exit_date.max().date()),'test_signal_start':str(test.date.min().date()),'test_signal_end':str(test.date.max().date()),'first_entry':str(tr.entry.min().date()),'last_exit':str(tr.exit.max().date()),'passive_spy':summary_passive,'blocks':len(signals),'selected':selection[ix],'prediction':metrics,'investment':performances,'versions':{'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'xgboost':xgb.__version__},'snapshot_sha256':hashlib.sha256(snapshot.read_bytes()).hexdigest()}
(O/'summary.json').write_text(json.dumps(summary,indent=2));baseline.save_model(O/'original.ubj');improved.save_model(O/'revised.ubj')
print(json.dumps(summary,indent=2))
