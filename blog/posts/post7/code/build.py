"""Build Blog 7 from the archived Census response, offline, using Python's standard library."""
from pathlib import Path
import csv, hashlib, json, math, shutil

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/acs_reporter.json'
OUT = ROOT / 'results'
OUT.mkdir(parents=True, exist_ok=True)
EXPECTED = '8516df11de9c2bf8880dfa17c6298b9a5ccfbf7ece7caa88fbe01cfd57fca017'
assert hashlib.sha256(RAW.read_bytes()).hexdigest() == EXPECTED, 'Archived response changed'
source = json.loads(RAW.read_text())
assert source['release']['id'] == 'acs2024_5yr'

def extract(geoid, tables):
    estimates = tables['B25070']['estimate']
    counts = [estimates[f'B25070{i:03d}'] for i in range(1, 12)]
    assert all(v is not None and v >= 0 for v in counts)
    assert sum(counts[1:]) == counts[0], 'Burden categories must sum to total'
    denom = counts[0] - counts[10]
    numerator = sum(counts[6:10])
    r = dict(fips=geoid[-5:] if geoid.startswith('050') else '42',
        county=source['geography'][geoid]['name'].replace(' County, PA', ''),
        monthly_gross_rent=tables['B25064']['estimate']['B25064001'],
        rent_moe=tables['B25064']['error']['B25064001'],
        annual_renter_income=tables['B25119']['estimate']['B25119003'],
        income_moe=tables['B25119']['error']['B25119003'],
        cash_rent_households=counts[0], computable_households=denom,
        not_computed=counts[10], burdened_households=numerator,
        burden_pct=100*numerator/denom, severe_burden_pct=100*counts[9]/denom)
    assert denom > 0 and 0 <= r['burden_pct'] <= 100
    assert all(r[k] is not None and r[k] > 0 for k in ('monthly_gross_rent','annual_renter_income'))
    assert r['rent_moe'] is not None and r['rent_moe'] >= 0
    return r

rows = sorted([extract(g,t) for g,t in source['data'].items() if g.startswith('050')], key=lambda r:r['fips'])
state = extract('04000US42', source['data']['04000US42'])
assert len(rows) == len({r['fips'] for r in rows}) == 67
for k in ('cash_rent_households','computable_households','not_computed','burdened_households'):
    assert sum(r[k] for r in rows) == state[k], k

def scenario(budget, minimum=0):
    subset = [r for r in rows if r['monthly_gross_rent'] <= budget and r['computable_households'] >= minimum]
    d = sum(r['computable_households'] for r in subset)
    return dict(budget=budget, minimum=minimum, counties=len(subset), computable_households=d,
        pooled_burden_pct=100*sum(r['burdened_households'] for r in subset)/d if d else None,
        county_names=[r['county'] for r in subset])

metrics = dict(counties=67, period='2020–2024 ACS five-year estimates', dollars='2024 dollars',
    state=state, scenarios=[scenario(b,m) for b,m in [(600,0),(1000,0),(1200,0),(1800,0),(1000,20000)]],
    examples=[r for r in rows if r['county'] in ['Erie','Centre','Philadelphia','Chester','Cameron']])
with (OUT/'county_analysis.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
(OUT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
payload=json.dumps(dict(rows=rows,state=state),separators=(',',':')).replace('</','<\\/')
page=(ROOT/'code/explorer-template.html').read_text().replace('__DATA__',payload)
(OUT/'explorer.html').write_text(page)
shutil.copyfile(ROOT/'code/explorer.js',OUT/'explorer.js')
(OUT/'validation.json').write_text(json.dumps(dict(source_sha256=EXPECTED,unique_counties=67,
    categories_reconcile=True,county_counts_reconcile_to_state=True,
    filter_rule='median rent <= budget AND computable households >= minimum; inclusive boundaries',
    pooled_rate='sum(burdened households)/sum(computable households), not mean county rates',
    chart_runtime='Plotly.js basic 3.1.0; local vendored asset',
    plotly_sha256=hashlib.sha256((ROOT/'vendor/plotly-basic-3.1.0.min.js').read_bytes()).hexdigest()),indent=2)+'\n')
print(json.dumps(metrics,indent=2))
# A static listing thumbnail; the article's substantive visual is the Plotly explorer.
points=''.join(f'<circle cx="{55+(r["monthly_gross_rent"]-500)/1450*485:.2f}" cy="{265-(r["burden_pct"]-20)/45*205:.2f}" r="3.5" fill="#155ab6" opacity=".75"/>' for r in rows)
preview=f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="340" viewBox="0 0 600 340"><rect width="600" height="340" fill="#f7fafc"/><text x="30" y="30" font-family="sans-serif" font-size="19" font-weight="bold" fill="#213547">What does your rent budget leave out?</text><text x="30" y="51" font-family="sans-serif" font-size="12" fill="#53616f">67 Pennsylvania counties · 2020–2024 ACS · interactive Plotly explorer</text><path d="M55 60V265H550" fill="none" stroke="#9eafbf"/>{points}<text x="55" y="289" font-family="sans-serif" font-size="12" fill="#53616f">Median monthly gross rent →</text><text x="30" y="318" font-family="sans-serif" font-size="12" fill="#53616f">Adjust a ceiling • inspect counties • compare rent uncertainty</text></svg>'''
(OUT/'preview.svg').write_text(preview)
shutil.copyfile(ROOT/'code/preview-narrow.html', OUT/'preview-narrow.html')
