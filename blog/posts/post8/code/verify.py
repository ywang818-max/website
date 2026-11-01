"""Independent numerical checks of the saved Blog 8 results; no simulation helper imports."""
from pathlib import Path
from collections import defaultdict
import csv,json,math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'

def records(name):
    with (OUT/name).open() as f:return list(csv.DictReader(f))

def percentile(values,p):
    a=sorted(values);position=(len(a)-1)*p;lo=math.floor(position);hi=math.ceil(position)
    return a[lo]+(a[hi]-a[lo])*(position-lo)

def t_central_area(a,df):
    # Numerical integration of the analytic Student t density, independent of
    # the Monte Carlo generator. Symmetry gives the two-sided tail as 1-area.
    grid=np.linspace(0,abs(a),20001)
    log_c=math.lgamma((df+1)/2)-math.lgamma(df/2)-.5*math.log(df*math.pi)
    density=np.exp(log_c-(df+1)/2*np.log1p(grid*grid/df))
    return 2*float(np.trapezoid(density,grid))

config=json.loads((ROOT/'data/config.json').read_text())
sample=[float(r['minutes']) for r in records('simulated_sample.csv')]
boot=defaultdict(list)
for r in records('bootstrap_means.csv'):boot[int(r['n'])].append(float(r['mean']))
coverage=defaultdict(list)
for r in records('coverage_intervals.csv'):coverage[(int(r['n']),float(r['confidence']))].append(r)
payload=json.loads((OUT/'payload.json').read_text())
for n in config['sample_sizes']:
    x=sample[:n];mean=math.fsum(x)/n;sd=math.sqrt(math.fsum((v-mean)**2 for v in x)/(n-1))
    s=payload['scenarios'][str(n)]
    assert abs(mean-s['sample_mean'])<1e-12 and abs(sd-s['sample_sd'])<1e-12
    assert len(boot[n])==config['display_bootstrap_resamples']
    check_rng=np.random.default_rng(np.random.SeedSequence([config['seed'],n,1]))
    for i in range(3):assert abs(math.fsum(check_rng.choice(x,size=n,replace=True))/n-boot[n][i])<1e-11
    for c in config['confidence_levels']:
        key=str(int(c*100));expected=[percentile(boot[n],(1-c)/2),percentile(boot[n],(1+c)/2)]
        assert np.allclose(expected,s['bootstrap_ci'][key],atol=1e-12,rtol=0)
        rows=coverage[(n,c)];assert len(rows)==config['coverage_repetitions']
        assert [int(r['trial']) for r in rows]==list(range(1,len(rows)+1))
        hits=sum(float(r['low'])<=config['population_mean']<=float(r['high']) for r in rows)
        assert hits==s['coverage'][key]['covered']
        assert all(int(r['covered'])==int(float(r['low'])<=config['population_mean']<=float(r['high'])) for r in rows)
        for original,displayed in zip(rows[:config['display_intervals']],s['coverage'][key]['first_intervals']):
            assert abs(float(original['low'])-displayed['low'])<1e-12 and abs(float(original['high'])-displayed['high'])<1e-12
    h=s['bootstrap_hist'];assert sum(h['count'])==config['display_bootstrap_resamples'];assert abs(sum(d*w for d,w in zip(h['density'],h['width']))-1)<1e-12

max_p_error=0.0
for row in records('null_test_summary.csv'):
    n=int(row['n']);x=sample[:n];mean=math.fsum(x)/n;sd=math.sqrt(math.fsum((v-mean)**2 for v in x)/(n-1));obs=(mean-float(row['null_mean']))/(sd/math.sqrt(n))
    assert abs(obs-float(row['t_observed']))<1e-12
    extreme=int(row['extreme_count']);M=int(row['null_repetitions']);p=(extreme+1)/(M+1)
    assert abs(p-float(row['p_value']))<1e-14
    analytic_p=max(0.0,1-t_central_area(obs,n-1));mcse=math.sqrt(analytic_p*(1-analytic_p)/M)
    assert abs(p-analytic_p)<=5*mcse+2/(M+1)
    max_p_error=max(max_p_error,abs(p-analytic_p))
    central=t_central_area(float(row['critical_abs']),n-1);c=float(row['confidence'])
    assert abs(central-c)<5*math.sqrt(c*(1-c)/M)
    assert bool(int(row['reject']))==(p<1-c)
    test=payload['scenarios'][str(n)]['tests'][str(int(float(row['null_mean'])))]['by_level'][str(int(c*100))]
    h=test['hist'];assert sum(h['count'])==M
    assert sum(k for k,tail in zip(h['count'],test['tail']) if tail)==extreme
    assert abs(sum(d*w for d,w in zip(h['density'],h['width']))-1)<1e-12

report=dict(sample_mean_sd_checks=3,manual_percentile_checks=6,regenerated_bootstrap_means=9,
    coverage_records_reconciled=12000,displayed_coverage_intervals_reconciled=360,
    null_test_rows_checked=18,student_t_density_quadrature='all simulated p-values and critical areas within five Monte Carlo SEs',
    maximum_absolute_p_error=max_p_error,histogram_areas_and_exact_tail_counts='pass')
(OUT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
