from pathlib import Path
import json,re,html,subprocess,shutil,os
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/blog9-mpl')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np,pandas as pd
P=Path(__file__).resolve().parents[1];R=P/'results';s=json.loads((R/'summary.json').read_text());c=s['class']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','svg.hashsalt':'blog9','figure.facecolor':'white','axes.labelcolor':'#233447','text.color':'#233447'})
colors={'Original':'#cc6942','Revised':'#2359a0','Training mean':'#697780','Equal weight':'#617c45','SPY':'#8054a5'}
def save(fig,name):
 fig.savefig(R/(name+'.svg'),bbox_inches='tight',metadata={'Date':None});fig.savefig('/private/tmp/blog9-'+name+'.png',bbox_inches='tight',dpi=130);plt.close(fig)
cl=pd.read_csv(P/'data/class_results.csv');d=(cl.portfolio2-cl.portfolio1).sort_values().to_numpy();fig,ax=plt.subplots(figsize=(9,3.6));ax.scatter(d,np.arange(1,46),c=np.where(d>=0,'#2359a0','#cc6942'),s=30);ax.axvline(0,color='#697780',lw=1);ax.axvline(c['difference'],color='#2359a0',ls='--',label=f"Mean difference: ${c['difference']:,.0f}")
ax.set(xlabel='Indicator portfolio minus intuition portfolio (dollars)',ylabel='Class pair, ordered by difference',title='Indicators finished ahead in 30 of 45 classroom pairs');ax.legend(loc='lower right',frameon=False);ax.grid(axis='x',alpha=.13);fig.tight_layout();save(fig,'classroom')
m=pd.read_csv(R/'prediction_metrics.csv');fig,axes=plt.subplots(1,2,figsize=(9,3.5),sharey=True)
for ax,key,title in zip(axes,['rmse','mae'],['Root mean squared error','Mean absolute error']):
 ax.barh(m.model,m[key]*100,color=[colors[x] for x in m.model]);ax.invert_yaxis();ax.set(xlim=(0,10.6),xlabel='Percentage points of holding-period return',title=title);ax.grid(axis='x',alpha=.13)
 for i,v in enumerate(m[key]*100):ax.text(v+.12,i,f'{v:.2f}',va='center',fontsize=10)
fig.suptitle('A simpler model reduces error, but barely beats a constant forecast',fontsize=13);fig.tight_layout();save(fig,'prediction')
w=pd.read_csv(R/'portfolio_windows.csv',parse_dates=['entry','exit']);fig,ax=plt.subplots(figsize=(9,4.4));styles={'Original':'--','Revised':'-','Equal weight':':','SPY':'-.'}
for name,g in w.groupby('strategy',sort=False):
 g=g.sort_values('exit');ax.plot([g.entry.min(),*g.exit],[100,*list(100*g.net_wealth)],label=name,color=colors[name],ls=styles[name],marker='o',markersize=3,lw=2)
ax.set(ylabel='Value of initial $100',xlabel='Holding-window exit in 2025',title='Revised selections earned more in ten held-out windows');ax.legend(ncol=2,frameon=False,loc='upper left');ax.grid(alpha=.15);fig.tight_layout();save(fig,'investment')
# Numeric prose derives from saved results, never from hand-entered chart labels.
metric={x['model']:x for x in s['prediction']};perf={(x['strategy'],x['cost_bps_each_side']):x['cumulative_return'] for x in s['investment']}
article=f'''---
title: "Can a Simpler Stock Model Beat Its Classroom Version?"
subtitle: "Better forecasts and better investments are different tests."
author: "Yixuan Wang"
date: "2026-11-09"
categories: [Machine Learning, Stocks, Gradient Boosting]
image: results/investment.svg
---

If a stock model makes smaller forecasting errors, should we trust it with money? Our classroom stock game gives this question a useful starting point. I compare its results with a separate historical test: can a simpler version of the classroom gradient-boosting model improve both prediction and portfolio performance?

## What the classroom game showed

The professor’s spreadsheet contains **45 paired final portfolio values**. His R script labels Portfolio 1 as intuition-based and Portfolio 2 as indicator-based. Their averages were **${c['intuition_mean']:,.0f} and ${c['indicator_mean']:,.0f}**. Indicators finished ahead in **{c['indicator_wins']} pairs**, but the mean advantage of **${c['difference']:,.0f}** came with a paired 95% interval from **−${abs(c['ci95'][0]):,.0f} to ${c['ci95'][1]:,.0f}**. The two-sided paired-test p-value was **{c['p_two_sided']:.3f}**.

![Figure 1. Each dot is one classroom pair. The dashed line marks the mean difference; zero means equal final values.](results/classroom.svg)

That is suggestive, not decisive. These are outcomes from one shared market episode, not 45 independent market histories. The file does not identify holdings, dates, or which predictions came from XGBoost. It cannot establish that gradient boosting caused the difference. I therefore use it to describe the classroom experiment, then evaluate the model separately.

## Give the revised model a fair test

Gradient boosting builds small decision trees sequentially, with each new tree correcting earlier prediction errors. The classroom script uses 300 trees, depth five, a learning rate of 0.05, and price, volume, momentum, volatility, and market-return information.

I reproduce those main settings in Python. The retained universe contains **95 classroom stocks**, plus SPY as a market comparator. One requested ticker, BK, failed retrieval and was excluded before fitting. Yahoo adjusted prices cover 2022 through October 2025. This is a historical reconstruction, not the exact class-time model artifact.

Both models train on **2022–2023**. I remove observations whose future-return labels cross into the next period. **2024** chooses among four revised specifications; **2025** remains untouched until final evaluation. Both models keep the same training observations, without refitting on validation data.

The revision drops nominal price and volume levels, keeps six return-based signals, and expresses momentum in the forward direction. Validation selects **100 trees of depth two**, with stronger regularization. These joint changes attempt to reduce overfitting; this comparison cannot identify which change helped most.

## Smaller errors do not guarantee useful forecasts

The target is the adjusted-close return from the next trading day’s close to the close 20 trading days after the signal: **19 daily return intervals**. On **{s['test_rows']:,} held-out stock-date observations**, revised RMSE is **{metric['Revised']['rmse']*100:.2f} percentage points**, versus **{metric['Original']['rmse']*100:.2f}** for the original settings. Lower is better.

![Figure 2. Both errors use identical held-out observations. The simple benchmark predicts the training-period mean for every stock and date.](results/prediction.svg)

Yet a constant forecast scores **{metric['Training mean']['rmse']*100:.2f} points**. The revised model barely improves that benchmark and has slightly worse mean absolute error. Its direction accuracy is **{metric['Revised']['direction_accuracy']*100:.1f}%**, below the constant forecast’s **{metric['Training mean']['direction_accuracy']*100:.1f}%**. Large errors show how much return variation these price-based signals leave unexplained. Learning past patterns can mistake noise for a relationship that will persist. Overlapping targets and common market movements also mean these observations are not independent evidence of forecasting skill.

## Would the selections have made money?

Every 20 trading days, I select each model’s ten highest forecasts and weight them by positive predicted returns. Trading begins at the next close. All strategies use identical holding windows, with a cash gap between them. I charge **10 basis points per side**—0.1% to buy and again to sell—and fully liquidate each window.

![Figure 3. Wealth compounds across ten windows, January 3–October 21, 2025. All four lines include the same assumed trading costs. SPY here follows the matched-window schedule.](results/investment.svg)

The revised portfolio gains **{perf['Revised',10]*100:.1f}%**, against **{perf['Original',10]*100:.1f}%** for the original, **{perf['Equal weight',10]*100:.1f}%** for equal-weighting all stocks, and **{perf['SPY',10]*100:.1f}%** for matched-window SPY. Genuine buy-and-hold SPY over the same endpoints gains **{s['passive_spy']['10']*100:.1f}%** after one purchase and sale. At 25 basis points per side, the revised gain falls to **{perf['Revised',25]*100:.1f}%**.

These gains are economically large within this test, but ten windows and a retrospectively supplied stock universe cannot establish persistent skill. Survivorship bias, changing relationships, and unmodeled execution costs remain. The practical lesson is narrower: simplifying helped relative to the classroom settings here, while beating a trivial forecasting benchmark remained difficult. Portfolio gains deserve a separate test, not an automatic endorsement from lower prediction error.

## Sources and replication

Classroom sources: professor-supplied portfolio spreadsheet, results R script, and original XGBoost script. Market source: [Yahoo Finance](https://finance.yahoo.com/). Methods: [XGBoost parameters](https://xgboost.readthedocs.io/en/stable/parameter.html) and [time-ordered model validation](https://scikit-learn.org/stable/modules/cross_validation.html#time-series-split). [Code, frozen data, detailed assumptions, and saved results](https://github.com/ywang818-max/website/tree/main/blog/posts/post9).
'''
(P/'index.qmd').write_text(article)
bodyprose=article.split('---',2)[2].split('## Sources and replication')[0];words=len(re.findall(r"\b[\w’–.-]+\b",re.sub(r'!\[.*?\]\(.*?\)','',bodyprose)))
print('Main prose words:',words)
# Use the existing site shell and Pandoc for a self-contained committed Pages build.
pandoc=shutil.which('pandoc') or '/Applications/RStudio.app/Contents/Resources/app/quarto/bin/tools/aarch64/pandoc'
body=subprocess.check_output([pandoc,str(P/'index.qmd'),'-f','markdown','-t','html5'],text=True)
site=P.parents[2];dest=site/'docs/blog/posts/post9';dest.mkdir(parents=True,exist_ok=True)
shell=(site/'docs/blog/posts/post8/index.html').read_text();start=shell.index('<header id="title-block-header"');end=shell.index('</main>',start)
title='Can a Simpler Stock Model Beat Its Classroom Version?'
header=f'<header id="title-block-header" class="quarto-title-block default"><div class="quarto-title"><h1 class="title">{title}</h1><p class="subtitle lead">Better forecasts and better investments are different tests.</p><div class="quarto-categories"><div class="quarto-category">Machine Learning</div><div class="quarto-category">Stocks</div><div class="quarto-category">Gradient Boosting</div></div></div><div class="quarto-title-meta"><div><div class="quarto-title-meta-heading">Author</div><div class="quarto-title-meta-contents"><p>Yixuan Wang</p></div></div><div><div class="quarto-title-meta-heading">Published</div><div class="quarto-title-meta-contents"><p class="date">November 9, 2026</p></div></div></div></header>'
shell=shell[:start]+header+body+shell[end:];shell=re.sub(r'<title>.*?</title>',f'<title>{title} – Yixuan Wang</title>',shell);shell=shell.replace('2026-11-01','2026-11-09');shell=re.sub(r'<meta name="description"[^>]*>','<meta name="description" content="A classroom stock game leads to a held-out test of simpler gradient boosting.">',shell)
(dest/'index.html').write_text(shell); (dest/'results').mkdir(exist_ok=True)
for f in R.glob('*.svg'): shutil.copy2(f,dest/'results'/f.name)
# Prepend one existing-style listing card, preserving earlier posts.
listing=site/'docs/blog/index.html';ls=listing.read_text();start=ls.index('<div class="quarto-post image-right"');stop=ls.index('<div class="quarto-post image-right"',start+1)
card=ls[start:stop]
card=card.replace('post8','post9').replace('results/preview.svg','results/investment.svg').replace('Can a 95% Interval Miss a 30-Minute Average?',title).replace('A simulated waiting-time example connects bootstrap intervals, coverage, and p-values.','Better forecasts and better investments are different tests.').replace('Nov 1, 2026','Nov 9, 2026').replace('2026-11-01','2026-11-09').replace('Simulation','Machine Learning').replace('Bootstrap','Stocks').replace('Statistical Inference','Gradient Boosting').replace('Resample one dataset, repeat the experiment, and test a claim to see what statistical uncertainty means.','A classroom stock game leads to a held-out test of simpler gradient boosting.')
if 'posts/post9/index.html' not in ls:listing.write_text(ls[:start]+card+ls[start:])
# Keep listing sort indices and category encoding coherent after inserting a card.
import base64,datetime
ls=listing.read_text();ls=re.sub(r'(<div class="quarto-post image-right"[^>]*data-index=")\d+("[^>]*>)',lambda m:m.group(1)+str(next(counter))+m.group(2),ls) if False else ls
counter=iter(range(100));ls=re.sub(r'data-index="\d+"',lambda m:'data-index="'+str(next(counter))+'"',ls)
pos=ls.index('posts/post9/index.html'); begin=ls.rfind('<div class="quarto-post image-right"',0,pos); end=ls.index('>',begin)
tag=ls[begin:end];tag=re.sub(r'data-categories="[^"]*"','data-categories="'+base64.b64encode(b'Machine%20Learning%2CStocks%2CGradient%20Boosting').decode()+'"',tag);tag=re.sub(r'data-listing-date-sort="[^"]*"','data-listing-date-sort="1794200400000"',tag);tag=re.sub(r'data-listing-word-count-sort="[^"]*"',f'data-listing-word-count-sort="{words}"',tag)
ls=ls[:begin]+tag+ls[end:];listing.write_text(ls)
lp=site/'docs/listings.json';j=json.loads(lp.read_text());item='/blog/posts/post9/index.html'
if item not in j[0]['items']:j[0]['items'].insert(0,item)
lp.write_text(json.dumps(j,indent=2)+'\n')
search=site/'docs/search.json';j=json.loads(search.read_text());j=[x for x in j if not x.get('href','').startswith('blog/posts/post9/')];j.append({'href':'blog/posts/post9/index.html','title':title,'section':'','text':re.sub('<[^>]+>',' ',body)});search.write_text(json.dumps(j,ensure_ascii=False,indent=2))
