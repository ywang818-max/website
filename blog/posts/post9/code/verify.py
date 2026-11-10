"""Independent checks from saved prices, predictions and holdings, not build helpers."""
from pathlib import Path
import pandas as pd,numpy as np,json,math
P=Path(__file__).resolve().parents[1];R=P/'results';s=json.loads((R/'summary.json').read_text())
p=pd.read_csv(P/'data/prices.csv.gz'); p=p.set_index(['symbol','date']);d=pd.read_csv(R/'test_predictions.csv.gz');h=pd.read_csv(R/'holdings.csv');w=pd.read_csv(R/'portfolio_windows.csv'); metrics=pd.read_csv(R/'prediction_metrics.csv'); invest=pd.read_csv(R/'investment_metrics.csv')
assert len(d)==s['test_rows'] and len(d)==95*d.date.nunique()
assert not d.duplicated(['symbol','date']).any(); assert d.date.min()>s['val_label_end']
for r in d.itertuples():
 y=p.loc[(r.symbol,r.exit_date),'adjusted']/p.loc[(r.symbol,r.entry_date),'adjusted']-1
 assert abs(y-r.target)<1e-12
for col in ['Original','Revised','Training mean']:
 row=metrics[metrics.model==col].iloc[0]
 rmse=math.sqrt(math.fsum((a-b)**2 for a,b in zip(d.target,d[col]))/len(d));assert abs(rmse-row.rmse)<1e-12
for r in w.itertuples():
 if r.strategy in ['Original','Revised']:
  hh=h[(h.signal==r.signal)&(h.strategy==r.strategy)]; assert len(hh)==10 and abs(hh.weight.sum()-1)<1e-12
  pp=d[d.date==r.signal].sort_values([r.strategy,'symbol'],ascending=[False,True]).head(10)
  assert set(hh.symbol)==set(pp.symbol)
  gross=math.fsum(x.weight*x.target for x in hh.itertuples())
 elif r.strategy=='Equal weight':gross=math.fsum(d[d.date==r.signal].target)/95
 else:gross=p.loc[('SPY',r.exit),'adjusted']/p.loc[('SPY',r.entry),'adjusted']-1
 assert abs(gross-r.gross)<1e-12
 assert abs((1-.001)**2*(1+gross)-1-r.net)<1e-12
for name,g in w.groupby('strategy'):
 assert len(g)==10
 assert all(g.entry.to_numpy()[1:]>g.exit.to_numpy()[:-1])
 for cost in [0,10,25]:
  final=math.prod((1-cost/10000)**2*(1+v) for v in g.gross)-1
  reported=invest[(invest.strategy==name)&(invest.cost_bps_each_side==cost)].cumulative_return.iloc[0]
  assert abs(final-reported)<1e-12
c=pd.read_csv(P/'data/class_results.csv');delta=[b-a for a,b in zip(c.portfolio1,c.portfolio2)];assert abs(math.fsum(delta)/45-s['class']['difference'])<1e-9
out={'status':'passed','checked_test_targets':len(d),'checked_portfolio_rows':len(w),'checked_cost_combinations':len(invest),'class_pairs':len(c),'scope':'Every saved target, portfolio return, weight sum, ranking selection, RMSE and cost-compounded final wealth; paired class statistics independently matched R.'}
(R/'verification.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
