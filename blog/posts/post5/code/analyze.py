"""Offline, deterministic ACS county analysis and GIS figures. Run from any directory."""
from pathlib import Path
import csv, hashlib, json, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch
from matplotlib.colors import Normalize
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/'data/raw'
OUT = ROOT/'results'
FIG = OUT/'figures'
for p in [OUT, FIG]: p.mkdir(parents=True, exist_ok=True)
provenance = json.loads((RAW/'provenance.json').read_text())
for filename, spec in provenance['sources'].items():
    assert hashlib.sha256((RAW/filename).read_bytes()).hexdigest()==spec['sha256'], filename
acs = json.loads((RAW/'acs_reporter.json').read_text())
geo = json.loads((RAW/'pa_counties_5070.json').read_text())
assert acs['release']['id']=='acs2024_5yr'

def row(geoid, data):
    rent=data['B25064']['estimate']['B25064001']
    income=data['B25119']['estimate']['B25119003']
    counts=[data['B25070']['estimate'][f'B25070{i:03d}'] for i in range(1,12)]
    assert all(v is not None and v>=0 for v in counts)
    assert rent is not None and rent>0 and income is not None and income>0
    assert sum(counts[1:])==counts[0], geoid
    denominator=counts[0]-counts[10]
    assert denominator>0
    burden=sum(counts[6:10])/denominator*100
    assert 0<=burden<=100
    return dict(fips=geoid[-5:] if geoid.startswith('050') else '42',
        county=acs['geography'][geoid]['name'].replace(' County, PA',''),
        monthly_gross_rent=rent, rent_moe=data['B25064']['error']['B25064001'],
        annual_renter_income=income, income_moe=data['B25119']['error']['B25119003'],
        cash_rent_households=counts[0], computable_households=denominator,
        not_computed=counts[10], burdened_households=sum(counts[6:10]),
        burden_pct=burden, severe_burden_pct=counts[9]/denominator*100)

rows=[row(g,d) for g,d in acs['data'].items() if g.startswith('050')]
rows.sort(key=lambda r:r['fips'])
state=row('04000US42',acs['data']['04000US42'])
assert len(rows)==67 and len({r['fips'] for r in rows})==67
shapes={f['attributes']['GEOID']: f for f in geo['features']}
assert len(shapes)==67 and set(shapes)=={r['fips'] for r in rows}
assert all(r['fips'].startswith('42') for r in rows)
for key in ['cash_rent_households','not_computed','burdened_households']:
    assert sum(r[key] for r in rows)==state[key], key
with (OUT/'county_analysis.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
metrics={'state':state,'counties':67,
    'low_rent_high_burden':[r for r in rows if r['monthly_gross_rent']<state['monthly_gross_rent'] and r['burden_pct']>state['burden_pct']],
    'rent_min':min(rows,key=lambda r:r['monthly_gross_rent']),
    'rent_max':max(rows,key=lambda r:r['monthly_gross_rent'])}
(OUT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'svg.fonttype':'none','svg.hashsalt':'blog5','axes.titleweight':'bold'})

def county_path(feature):
    vertices=[]; codes=[]
    for ring in feature['geometry']['rings']:
        vertices.extend(ring); codes.extend([MPath.MOVETO]+[MPath.LINETO]*(len(ring)-2)+[MPath.CLOSEPOLY])
    return MPath(vertices,codes)

def map_figure(key,title,subtitle,cmap,filename,percent=False):
    fig,ax=plt.subplots(figsize=(11,6.6)); fig.subplots_adjust(left=.025,right=.975,bottom=.15,top=.79)
    norm=Normalize(min(r[key] for r in rows),max(r[key] for r in rows))
    palette=plt.get_cmap(cmap)
    for r in rows:
        ax.add_patch(PathPatch(county_path(shapes[r['fips']]),facecolor=palette(norm(r[key])),edgecolor='white',linewidth=.7))
    ax.autoscale_view(); ax.set_aspect('equal'); ax.axis('off')
    for name, offset in [('Erie',(0,10)),('Allegheny',(-10,-5)),('Centre',(0,0)),('Montgomery',(30,25)),('Philadelphia',(35,-12))]:
        r=next(r for r in rows if r['county']==name)
        points=[p for ring in shapes[r['fips']]['geometry']['rings'] for p in ring]
        x=(min(p[0] for p in points)+max(p[0] for p in points))/2
        y=(min(p[1] for p in points)+max(p[1] for p in points))/2
        ax.annotate(name,(x,y),xytext=offset,textcoords='offset points',ha='center',fontsize=8,color='#182638',bbox=dict(boxstyle='round,pad=.18',fc='white',alpha=.88,ec='none'),arrowprops=dict(arrowstyle='-',color='#182638',lw=.6) if name in ['Montgomery','Philadelphia'] else None)
    fig.text(.035,.945,title,fontsize=19,weight='bold',color='#213547')
    fig.text(.035,.895,subtitle,fontsize=11.5,color='#4b5563')
    cax=fig.add_axes([.25,.12,.5,.027]); cb=fig.colorbar(plt.cm.ScalarMappable(norm=norm,cmap=palette),cax=cax,orientation='horizontal')
    cb.ax.xaxis.set_major_formatter(FuncFormatter(lambda x,pos:f'{x:.0f}%' if percent else f'${x:,.0f}'))
    fig.text(.035,.025,'Source: U.S. Census Bureau, 2020–2024 ACS, via Census Reporter. County boundaries: Census TIGERweb.\nNAD83 / Conus Albers; county area does not represent the number of renters.',fontsize=8.5,color='#59636e')
    fig.savefig(FIG/(filename+'.svg'),metadata={'Date':None}); fig.savefig(FIG/(filename+'.png'),dpi=150); plt.close(fig)

map_figure('monthly_gross_rent','Where are Pennsylvania rents lower?','Median monthly gross rent, including utilities • 2020–2024 ACS • 2024 dollars','YlGnBu','figure1')
map_figure('burden_pct','Lower rent does not guarantee a lighter burden','Share of cash-rent households spending 30%+ of income on rent • excludes ratios not computed','YlOrRd','figure2',True)
fig,ax=plt.subplots(figsize=(10.5,6.5)); fig.subplots_adjust(left=.10,right=.96,bottom=.18,top=.80)
ax.scatter([r['monthly_gross_rent'] for r in rows],[r['burden_pct'] for r in rows],s=42,color='#317b8b',alpha=.72,edgecolors='white',linewidth=.5)
ax.axhline(state['burden_pct'],color='#9ca3af',ls='--',lw=1); ax.axvline(state['monthly_gross_rent'],color='#9ca3af',ls='--',lw=1)
for name,offset in [('Philadelphia',(8,7)),('Allegheny',(8,-14)),('Erie',(8,5)),('Centre',(8,5)),('Montgomery',(-70,8))]:
    r=next(r for r in rows if r['county']==name)
    ax.annotate(name,(r['monthly_gross_rent'],r['burden_pct']),xytext=offset,textcoords='offset points',fontsize=9)
ax.set_xlabel('Median monthly gross rent (2024 dollars)'); ax.set_ylabel('Rent-burdened households (%)')
ax.xaxis.set_major_formatter(FuncFormatter(lambda x,pos:f'${x:,.0f}')); ax.spines[['top','right']].set_visible(False)
fig.text(.07,.94,'A lower price can still come with a high burden',fontsize=19,weight='bold',color='#213547')
fig.text(.07,.89,'Each dot is one county. Dashed lines mark Pennsylvania’s directly estimated statewide figures.',fontsize=10.5)
fig.text(.07,.03,'Source: U.S. Census Bureau, 2020–2024 ACS, tables B25064 and B25070, via Census Reporter.\nBurden means spending 30%+ of household income on gross rent; ratios not computed are excluded.',fontsize=9,color='#59636e')
fig.savefig(FIG/'figure3.svg',metadata={'Date':None}); fig.savefig(FIG/'figure3.png',dpi=150); plt.close(fig)
(OUT/'validation.json').write_text(json.dumps({'source_hashes':'pass','unique_counties':67,'geometry_join':'67 of 67; one-to-one','category_totals':'pass','county_counts_reconcile_to_state':'pass','missing_or_nonpositive_medians':0,'offline':True},indent=2)+'\n')
print(json.dumps({'state':state,'low_rent_high_burden_count':len(metrics['low_rent_high_burden']),'examples':[r for r in rows if r['county'] in ['Philadelphia','Erie','Allegheny','Centre','Montgomery']]},indent=2))
