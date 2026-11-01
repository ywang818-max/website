"""Seeded bootstrap coverage and Monte Carlo t-test tutorial. No empirical records or network calls."""
from pathlib import Path
import csv, hashlib, json, math, shutil
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'
OUT.mkdir(parents=True, exist_ok=True)
C = json.loads((ROOT/'data/config.json').read_text())
SEED, MU, SIGMA = C['seed'], C['population_mean'], C['population_sd']
LEVELS = C['confidence_levels']

def rng_for(n, purpose):
    return np.random.default_rng(np.random.SeedSequence([SEED, n, purpose]))

def interval(values, confidence):
    alpha = 1-confidence
    return np.quantile(values, [alpha/2, 1-alpha/2], method='linear')

def histogram(values, edges):
    counts, edges = np.histogram(values, bins=edges)
    assert counts.sum() == len(values), 'Histogram lost observations'
    widths = np.diff(edges)
    return dict(x=((edges[:-1]+edges[1:])/2).tolist(), width=widths.tolist(),
        density=(counts/(len(values)*widths)).tolist(), count=counts.tolist())

def write_csv(name, rows):
    with (OUT/name).open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)

base_sample = np.random.default_rng(SEED).normal(MU, SIGMA, max(C['sample_sizes']))
write_csv('simulated_sample.csv', [dict(observation=i+1,minutes=float(v)) for i,v in enumerate(base_sample)])
payload = dict(config=C, scenarios={})
coverage_rows, bootstrap_rows, summary_rows, null_rows = [], [], [], []
for n in C['sample_sizes']:
    x = base_sample[:n]
    sample_mean, sample_sd = float(x.mean()), float(x.std(ddof=1))
    se = sample_sd/math.sqrt(n)
    boot_rng = rng_for(n, 1)
    bootstrap = x[boot_rng.integers(0,n,size=(C['display_bootstrap_resamples'],n))].mean(axis=1)
    bootstrap_rows.extend(dict(n=n,replicate=i+1,mean=float(v)) for i,v in enumerate(bootstrap))
    boot_cis = {str(int(level*100)):interval(bootstrap,level).tolist() for level in LEVELS}
    boot_hist = histogram(bootstrap,np.linspace(float(bootstrap.min())-1e-9,float(bootstrap.max())+1e-9,36))

    # OUTER loop: entirely new independent samples from the known model.
    # INNER loop: resample each new sample, not the original displayed sample.
    coverage_rng = rng_for(n, 2)
    all_intervals = {str(int(level*100)):[] for level in LEVELS}
    for trial in range(C['coverage_repetitions']):
        sample = coverage_rng.normal(MU,SIGMA,n)
        means = sample[coverage_rng.integers(0,n,size=(C['coverage_bootstrap_resamples'],n))].mean(axis=1)
        for level in LEVELS:
            lo, hi = map(float,interval(means,level))
            covered = bool(lo <= MU <= hi)
            row=dict(n=n,confidence=level,trial=trial+1,low=lo,high=hi,covered=int(covered))
            coverage_rows.append(row)
            all_intervals[str(int(level*100))].append(row)
    coverage={}
    for level in LEVELS:
        key=str(int(level*100)); intervals=all_intervals[key]
        hits=sum(r['covered'] for r in intervals);rate=hits/len(intervals)
        coverage[key]=dict(covered=hits,repetitions=len(intervals),rate=rate,
            mcse=math.sqrt(rate*(1-rate)/len(intervals)),
            mean_width=float(np.mean([r['high']-r['low'] for r in intervals])),
            first_intervals=intervals[:C['display_intervals']])
        summary_rows.append(dict(n=n,confidence=level,covered=hits,repetitions=len(intervals),coverage=rate,
            monte_carlo_se=coverage[key]['mcse'],mean_width=coverage[key]['mean_width'],
            sample_mean=sample_mean,sample_sd=sample_sd,display_ci_low=boot_cis[key][0],display_ci_high=boot_cis[key][1]))

    # Normal-model one-sample t statistic. Centering the null at zero is valid
    # because the studentized location statistic is translation invariant.
    null_rng = rng_for(n,3)
    blocks=[]
    for start in range(0,C['null_repetitions'],5000):
        count=min(5000,C['null_repetitions']-start)
        samples=null_rng.normal(0,SIGMA,size=(count,n))
        s=samples.std(axis=1,ddof=1)
        assert np.all(s>0)
        blocks.append(samples.mean(axis=1)/(s/math.sqrt(n)))
    null_t=np.concatenate(blocks)
    tests={}
    for null_mean in C['null_means']:
        t_observed=(sample_mean-null_mean)/se
        extreme=int(np.count_nonzero(np.abs(null_t)>=abs(t_observed)))
        p=(extreme+1)/(len(null_t)+1)  # finite-simulation correction; never return p=0
        by_level={}
        for level in LEVELS:
            critical=float(np.quantile(np.abs(null_t),level,method='linear'))
            bound=math.ceil(max(float(np.max(np.abs(null_t))),abs(t_observed))+.25)
            # Add the actual observed/critical boundaries so density-bin tail areas
            # agree with the exact simulated tail count, not midpoint approximations.
            edges=np.unique(np.r_[np.linspace(-bound,bound,65),-abs(t_observed),abs(t_observed),-critical,critical])
            h=histogram(null_t,edges)
            tail=[bool(a>=abs(t_observed) or b<=-abs(t_observed)) for a,b in zip(edges[:-1],edges[1:])]
            assert sum(count for count,is_tail in zip(h['count'],tail) if is_tail)==extreme
            reject=bool(abs(t_observed)>critical)
            assert reject == (p < 1-level)
            by_level[str(int(level*100))]=dict(hist=h,tail=tail,critical=critical,bound=bound,reject=reject)
            null_rows.append(dict(n=n,confidence=level,null_mean=null_mean,t_observed=t_observed,
                extreme_count=extreme,null_repetitions=len(null_t),p_value=p,critical_abs=critical,reject=int(reject)))
        tests[str(int(null_mean))]=dict(null_mean=null_mean,t_observed=t_observed,extreme=extreme,p=p,by_level=by_level)
    payload['scenarios'][str(n)]=dict(n=n,sample_mean=sample_mean,sample_sd=sample_sd,se=se,
        bootstrap_hist=boot_hist,bootstrap_ci=boot_cis,coverage=coverage,tests=tests)

write_csv('bootstrap_means.csv',bootstrap_rows)
write_csv('coverage_intervals.csv',coverage_rows)
write_csv('coverage_summary.csv',summary_rows)
write_csv('null_test_summary.csv',null_rows)
(OUT/'payload.json').write_text(json.dumps(payload,separators=(',',':'))+'\n')
page=(ROOT/'code/lab-template.html').read_text().replace('__DATA__',json.dumps(payload,separators=(',',':')).replace('</','<\\/'))
(OUT/'lab.html').write_text(page)
shutil.copyfile(ROOT/'code/lab.js',OUT/'lab.js')
shutil.copyfile(ROOT/'code/preview-narrow.html',OUT/'preview-narrow.html')
default=payload['scenarios']['200']
metrics=dict(default_n=200,seed=SEED,sample_mean=default['sample_mean'],ci95=default['bootstrap_ci']['95'],
    covered95=default['coverage']['95']['covered'],coverage95=default['coverage']['95']['rate'],
    mcse95=default['coverage']['95']['mcse'],null30=default['tests']['30'],
    coverage_by_n={n:s['coverage']['95']['rate'] for n,s in payload['scenarios'].items()})
# Keep the compact narrative metrics separate from the full plotting payload.
metrics['null30']={k:v for k,v in metrics['null30'].items() if k!='by_level'}
(OUT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'data/config.json',ROOT/'code/build.py',ROOT/'code/lab.js',ROOT/'code/lab-template.html',ROOT/'code/article-template.qmd',ROOT/'code/preview-narrow.html',ROOT/'code/verify.py',ROOT/'vendor/plotly-basic-3.1.0.min.js']}
(OUT/'validation.json').write_text(json.dumps(dict(inputs_sha256=manifest,coverage_records=len(coverage_rows),
    expected_coverage_records=len(C['sample_sizes'])*len(LEVELS)*C['coverage_repetitions'],
    histogram_totals='all equal simulation count',null_tail_bins='exactly reconcile to extreme count',
    numpy_version=np.__version__,bit_generator='PCG64',quantile_method='linear',
    normal_model='Independent Normal(mean=30, sd=5) simulated minutes; no observed service data'),indent=2)+'\n')
# Small data-based thumbnail; the three substantive teaching panels are interactive.
ci=default['coverage']['95']['first_intervals'][:24]
lines=''.join(f'<line x1="{65+(r["low"]-28)*120:.1f}" x2="{65+(r["high"]-28)*120:.1f}" y1="{66+i*8}" y2="{66+i*8}" stroke="{"#155ab6" if r["covered"] else "#b67524"}" stroke-width="2"/>' for i,r in enumerate(ci))
(OUT/'preview.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="310"><rect width="600" height="310" fill="#f6f9fc"/><text x="25" y="30" font-size="21" font-family="sans-serif" font-weight="bold" fill="#213547">Can a 95% interval miss the true average?</text><line x1="305" x2="305" y1="50" y2="260" stroke="#263646" stroke-dasharray="5 4"/>{lines}<text x="25" y="290" font-family="sans-serif" font-size="13" fill="#53616f">Bootstrap → repeated coverage → simulated hypothesis test</text></svg>')
print(json.dumps(metrics,indent=2))
# Derive all numerical prose from the same saved simulation results.
article=(ROOT/'code/article-template.qmd').read_text()
replacements=dict(sample_mean=f'{metrics["sample_mean"]:.2f}',ci_low=f'{metrics["ci95"][0]:.2f}',
    ci_high=f'{metrics["ci95"][1]:.2f}',covered=f'{metrics["covered95"]:,}',
    coverage=f'{100*metrics["coverage95"]:.2f}',mcse=f'{100*metrics["mcse95"]:.2f}',
    small_coverage=f'{100*metrics["coverage_by_n"]["40"]:.2f}',
    t_obs=f'{metrics["null30"]["t_observed"]:.3f}',p_value=f'{metrics["null30"]["p"]:.3f}')
for key,value in replacements.items():article=article.replace('{{'+key+'}}',value)
assert '{{' not in article
(ROOT/'index.qmd').write_text(article)
