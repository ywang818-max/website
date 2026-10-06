"""Reproduce Blog 4: python code/analyze.py [--download]."""
from pathlib import Path
import argparse, json, urllib.request
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
ROOT=Path(__file__).resolve().parents[1]
SERIES={'wage':'CES0500000003','cpi':'CPIAUCSL','rent':'CUSR0000SEHA'}
START='2019-01-01'; END='2026-08-01'
args=argparse.ArgumentParser(); args.add_argument('--download',action='store_true'); opt=args.parse_args()
raw=ROOT/'data/raw'; processed=ROOT/'data/processed'; figures=ROOT/'results/figures'
for p in [raw,processed,figures]: p.mkdir(parents=True,exist_ok=True)
frames=[]
for name,series in SERIES.items():
    file=raw/(series+'.csv')
    if opt.download or not file.exists():
        url=f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd={START}&coed={END}'
        with urllib.request.urlopen(url,timeout=60) as response: file.write_bytes(response.read())
    df=pd.read_csv(file,parse_dates=['observation_date']).set_index('observation_date')
    df.columns=[name]; frames.append(df.apply(pd.to_numeric,errors='coerce'))
data=pd.concat(frames,axis=1).loc[START:END]
assert len(data)==92 and data.index[-1]==pd.Timestamp(END), 'Unexpected time window'
assert len(data.dropna())==91, 'Unexpected complete observation count'
base=data.loc['2019'].mean(); index=100*data/base
index['real_wage']=100*index.wage/index.cpi
index['rent_purchasing_power']=100*index.wage/index.rent
index.to_csv(processed/'indices.csv',index_label='date'); data.to_csv(processed/'monthly_levels.csv',index_label='date')
metrics={'baseline_2019_mean':base.to_dict(),'last_month':str(data.index[-1].date()),'last_indices':index.iloc[-1].to_dict(),'real_trough_since_2021':{'date':str(index.loc['2021':].real_wage.idxmin().date()),'index':float(index.loc['2021':].real_wage.min())},'retrieved':'2026-10-06','complete_observations':len(data.dropna()),'missing_months':[str(t.date()) for t in data.index[data.isna().any(axis=1)]]}
(ROOT/'results/metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.spines.bottom':False,'axes.labelcolor':'#465265','text.color':'#182335','xtick.color':'#465265','ytick.color':'#465265','svg.fonttype':'none'})
COLORS={'wage':'#155ab6','cpi':'#bd4d17','rent':'#7949a6','real_wage':'#155ab6'}
def chart(names,title,subtitle,filename,ylim):
    fig,ax=plt.subplots(figsize=(10,5.4)); fig.subplots_adjust(left=.09,right=.94,bottom=.21,top=.76)
    fig.text(.09,.94,title,fontsize=19,weight='bold',va='top');fig.text(.09,.85,subtitle,fontsize=11,color='#465265')
    ax.axhline(100,color='#8792a0',lw=1,ls=(0,(3,3)),zorder=1)
    labels={'wage':'Average hourly earnings','cpi':'Consumer prices','rent':'Rent of primary residence','real_wage':'Inflation-adjusted hourly earnings'}
    for n in names:
        ax.plot(index.index,index[n],lw=2.6,color=COLORS[n],label=labels[n],zorder=3)
        ax.scatter(index.index[-1],index[n].iloc[-1],s=24,color=COLORS[n],zorder=4)
    ax.set_ylim(*ylim);ax.set_xlim(data.index[0],pd.Timestamp('2026-12-01'));ax.grid(axis='y',color='#e5e9ef',lw=.8);ax.set_axisbelow(True)
    ax.xaxis.set_major_locator(mdates.YearLocator());ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'));ax.tick_params(length=0,pad=8);ax.set_ylabel('Index (2019 average = 100)',labelpad=12)
    ax.legend(loc='upper left',frameon=False,fontsize=10)
    if filename=='figure2':
        t=index.loc['2021':].real_wage.idxmin();v=index.loc[t,'real_wage']
        ax.annotate(f'Jun 2022: {v:.2f}',xy=(t,v),xytext=(pd.Timestamp('2021-01-01'),98.3),fontsize=10,arrowprops={'arrowstyle':'-','color':'#465265'})
        ax.annotate(f'Aug 2026: {index.real_wage.iloc[-1]:.2f}',xy=(index.index[-1],index.real_wage.iloc[-1]),xytext=(pd.Timestamp('2024-09-01'),105.8),fontsize=10,arrowprops={'arrowstyle':'-','color':'#465265'})
    end=' | '.join(f'{labels[n]}: {index[n].iloc[-1]:.2f}' for n in names)
    fig.text(.09,.10,'Aug 2026 — '+end,fontsize=10,color='#465265')
    fig.text(.09,.04,'Source: BLS via FRED. Monthly, seasonally adjusted. Oct 2025 CPI/rent unavailable; gaps not interpolated.',fontsize=9,color='#465265')
    for extension in ['svg','png']:fig.savefig(figures/(filename+'.'+extension),dpi=180,facecolor='white')
    plt.close(fig)
chart(['wage','cpi'],'Paychecks grew faster than the overall price level','Cumulative change measured from the same pre-pandemic baseline','figure1',(95,140))
chart(['real_wage'],'Purchasing power recovered, but the gain is modest','Nominal hourly earnings divided by consumer prices, rebased to 2019','figure2',(98,108.5))
chart(['wage','rent'],'Rent narrowly outpaced average hourly earnings','The same wage series compared with the rent component of the CPI','figure3',(95,140))
print(json.dumps(metrics,indent=2))
