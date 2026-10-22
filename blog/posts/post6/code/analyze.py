"""PSID fixed-width extract -> SQLite -> same-sample IGE comparisons.

Only aggregate results are written. Provide locally downloaded files via CLI;
microdata, local paths, databases, and individual matches are never exported.
"""
from pathlib import Path
import argparse,collections,csv,hashlib,json,re,sqlite3
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
INCOMES='V81 V529 V1514 V2226 V2852 V3256 V3676 V4154 V5029 V5626 V6173 V6766 V7412 V8065 V8689 V9375 V11022 V12371 V13623 V14670 V16144 V17533 V18875 V20175 V21481 V23322 ER4153 ER6993 ER9244 ER12079 ER16462 ER20456 ER24099 ER28037 ER41027 ER46935 ER52343 ER58152 ER65349 ER71426 ER77448 ER81775 ER85629'.split()
WAVES=list(range(1968,1998))+list(range(1999,2024,2))

def layout(path):
    source=path.read_text(errors='replace')
    block=source.split('infix',1)[1].split('using',1)[0]
    widths={v:(int(a)-1,int(b)) for v,a,b in re.findall(r'\b(ER\d+|V\d+)\s+(\d+)\s*-\s*(\d+)',block)}
    labels=dict(re.findall(r'label variable\s+(\w+)\s+"([^"]+)"',source))
    return widths,labels

def main(args):
    widths,labels=layout(args.statements)
    assert len(widths)==261, 'This adapter expects the documented 261-variable extract'
    def value(line,v):
        a,b=widths[v];s=line[a:b].strip();return (float(s) if '.' in s else int(s)) if s else None
    wave_specs=[]
    for wave,inc in zip(WAVES,INCOMES):
        age=next(v for v,l in labels.items() if 'AGE OF INDIVIDUAL' in l and l.strip().endswith(str(wave)[-2:]))
        fid='ER30001' if wave==1968 else next(v for v,l in labels.items() if l==f'{wave} INTERVIEW NUMBER')
        seq=None if wave==1968 else next(v for v,l in labels.items() if 'SEQUENCE NUMBER' in l and l.strip().endswith(str(wave)[-2:]))
        rel=next(v for v,l in labels.items() if ('RELATIONSHIP TO HEAD' in l or 'RELATION TO HEAD' in l or 'RELATION TO REFERENCE PERSON' in l) and l.strip().endswith(str(wave)[-2:]))
        wave_specs.append(dict(wave=wave,income_year=wave-1,income=inc,age=age,family_id=fid,sequence=seq,relationship=rel))
    cpi={int(r['year']):float(r['cpi']) for r in csv.DictReader((ROOT/'data/cpi_annual.csv').open())}
    db=sqlite3.connect(':memory:')
    db.executescript('''CREATE TABLE people(pid INTEGER PRIMARY KEY,sex INTEGER);
        CREATE TABLE membership(pid INTEGER,wave INTEGER,family_id INTEGER,age INTEGER,
        PRIMARY KEY(pid,wave),FOREIGN KEY(pid) REFERENCES people(pid));
        CREATE TABLE families(wave INTEGER,family_id INTEGER,income_real REAL,PRIMARY KEY(wave,family_id));
        CREATE TABLE links(child_pid INTEGER PRIMARY KEY,parent_pid INTEGER);
        PRAGMA foreign_keys=ON;''')
    audit=collections.Counter();family_values={};sex={};persons=[];batch=[]
    for line in args.data.open():
        assert len(line.rstrip('\n\r'))>=798
        pid=value(line,'ER30001')*1000+value(line,'ER30002')
        sx=value(line,'ER32000');sex[pid]=sx;persons.append((pid,sx))
        for w in wave_specs:
            age=value(line,w['age']);fid=value(line,w['family_id']);seq=value(line,w['sequence']) if w['sequence'] else 1
            inc=value(line,w['income']);audit['candidate_person_waves']+=1
            if not fid or not seq or not 1<=seq<=20 or not age or not 1<=age<=125:
                audit['nonresident_missing_age_or_family']+=1;continue
            rel=value(line,w['relationship'])
            if rel not in ([1,2,9] if w['wave']<=1982 else [10,20,22]):
                audit['not_current_head_or_spouse_partner']+=1;continue
            if inc is None or inc<=1:
                audit['nonpositive_or_bottomcoded_income']+=1;continue
            ceiling=(99999 if 1969<=w['wave']<=1979 else 999999 if w['wave'] in [1980,1984,1985] else 9999999 if w['wave']<=1995 else 9999998)
            if w['wave']!=1968 and inc>=ceiling:
                audit['topcode_boundary_excluded']+=1;continue
            key=(w['wave'],fid)
            if key in family_values:assert family_values[key]==inc, 'Within-family income disagreement'
            family_values[key]=inc
            batch.append((pid,w['wave'],fid,age,inc*cpi[2022]/cpi[w['income_year']]))
    db.executemany('INSERT INTO people VALUES (?,?)',persons)
    db.executemany('INSERT INTO membership VALUES (?,?,?,?)',[r[:4] for r in batch])
    family_rows={(r[1],r[2]):r[4] for r in batch}
    db.executemany('INSERT INTO families VALUES (?,?,?)',[(w,f,y) for (w,f),y in sorted(family_rows.items())])
    db.execute('''CREATE VIEW panel AS SELECT m.pid,m.wave,m.family_id,m.age,f.income_real
        FROM membership m JOIN families f ON f.wave=m.wave AND f.family_id=m.family_id''')
    assert db.execute('SELECT COUNT(*) FROM panel').fetchone()[0]==len(batch),'Family join changed row count'
    audit['people']=len(persons);audit['valid_person_waves']=len(batch)
    assert len(sex)==len(persons),'Duplicate permanent person ID'
    links={};types=collections.Counter()
    for line in args.fims.open():
        ptype=line[15:17].strip();types[ptype]+=1
        if ptype!='F':continue
        child=int(line[:4])*1000+int(line[4:7]);parent=int(line[8:12])*1000+int(line[12:15])
        if child not in sex or parent not in sex:audit['father_links_missing_extract_person']+=1;continue
        if child==parent:raise ValueError('Self-parent link')
        if sex[parent]!=1:
            audit['father_type_sex_inconsistency_excluded']+=1;continue
        if child in links:assert links[child]==parent,'Multiple biological fathers'
        links[child]=parent
    db.executemany('INSERT INTO links VALUES (?,?)',sorted(links.items()))
    audit['linked_child_father_pairs']=len(links);audit['fims_parent_types']=dict(types)
    db.executescript((ROOT/'sql/match.sql').read_text())
    columns=[d[0] for d in db.execute('SELECT * FROM matched').description]
    data=[dict(zip(columns,r)) for r in db.execute('SELECT * FROM matched ORDER BY child_pid')]
    assert len(data)>30,'Too few same-sample complete pairs'
    audit['same_sample_pairs']=len(data);audit['distinct_fathers']=len(set(r['parent_pid'] for r in data))
    results=[]
    specs=[('Single year: both prime age','parent_one','child_one'),('Multiple years: both prime age','parent_avg','child_avg'),('Early adult child, parent average','parent_avg','child_early'),('Prime-age child, parent average','parent_avg','child_one')]
    groups=np.array([r['parent_pid'] for r in data]);unique=np.unique(groups)
    for name,x,y in specs:
        X=np.column_stack([np.ones(len(data)),np.log([r[x] for r in data])]);Y=np.log([r[y] for r in data])
        bread=np.linalg.inv(X.T@X);beta=bread@X.T@Y;u=Y-X@beta
        assert np.allclose(beta,np.linalg.lstsq(X,Y,rcond=None)[0],atol=1e-10), 'Independent OLS check'
        meat=np.zeros((2,2))
        for g in unique:
            ix=groups==g;score=X[ix].T@u[ix];meat+=np.outer(score,score)
        cov=bread@meat@bread*(len(unique)/(len(unique)-1))*((len(data)-1)/(len(data)-2))
        se=float(np.sqrt(cov[1,1]));b=float(beta[1])
        results.append(dict(model=name,n=len(data),ige=b,se_cluster_father=se,ci_low=b-1.96*se,ci_high=b+1.96*se))
    audit['mean_observed_years_child']=float(np.mean([r['child_years'] for r in data]));audit['mean_observed_years_parent']=float(np.mean([r['parent_years'] for r in data]))
    audit['mean_single_age_child']=float(np.mean([r['child_age'] for r in data]));audit['mean_single_age_parent']=float(np.mean([r['parent_age'] for r in data]));audit['mean_early_age_child']=float(np.mean([r['age_early'] for r in data]))
    audit['input_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [args.data,args.statements,args.fims]}
    audit['income_units']='2022 dollars; CPI annual table rounded to one decimal'
    audit['estimator']='Unweighted descriptive OLS; 95% normal CIs clustered by father; same pairs in all models'
    out=ROOT/'results';figs=out/'figures';figs.mkdir(parents=True,exist_ok=True)
    (out/'audit.json').write_text(json.dumps(dict(audit),indent=2)+'\n')
    (out/'estimates.json').write_text(json.dumps(results,indent=2)+'\n')
    with (out/'estimates.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(results[0]));writer.writeheader();writer.writerows(results)
    (ROOT/'data/variable_map.json').write_text(json.dumps(wave_specs,indent=2)+'\n')
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','svg.hashsalt':'blog6','font.size':11})
    for filename,indices,title in [('figure1',[0,1],'Does averaging income change measured persistence?'),('figure2',[2,3],'Does the child’s age change the answer?')]:
        rows=[results[i] for i in indices];fig,ax=plt.subplots(figsize=(10,4.4));fig.subplots_adjust(left=.40,right=.95,top=.78,bottom=.20)
        for i,r in enumerate(rows):ax.errorbar(r['ige'],i,xerr=1.96*r['se_cluster_father'],fmt='o',color=['#268b8b','#cf7e35'][i],capsize=5,markersize=8);ax.text(r['ci_high']+.02,i,f"{r['ige']:.3f}",va='center',fontsize=11)
        ax.set_yticks(range(2),[r['model'].replace(': ','\n').replace(', ','\n') for r in rows]);ax.invert_yaxis();ax.set_xlim(min(0,min(r['ci_low'] for r in rows)-.1),max(r['ci_high'] for r in rows)+.15);ax.set_xlabel('Intergenerational elasticity (log–log slope)');ax.spines[['top','right','left']].set_visible(False);ax.grid(axis='x',alpha=.15)
        fig.text(.04,.92,title,fontsize=17,weight='bold');fig.text(.04,.84,f"Same {len(data):,} child–father pairs; family income in 2022 dollars",fontsize=11)
        fig.text(.04,.035,'Source: PSID extract J366555 and biological-parent FIMS map. Bars: 95% CIs clustered by father.\nUnweighted descriptive estimates; selected complete-case sample, not a causal or national mobility estimate.',fontsize=8.5,color='#59636e')
        fig.savefig(figs/(filename+'.svg'),metadata={'Date':None});fig.savefig(figs/(filename+'.png'),dpi=140);plt.close(fig)
    print(json.dumps({'audit':dict(audit),'estimates':results},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--data',type=Path,required=True);p.add_argument('--statements',type=Path,required=True);p.add_argument('--fims',type=Path,required=True);main(p.parse_args())
