from pathlib import Path
import re,json,urllib.request,concurrent.futures,hashlib,datetime
P=Path(__file__).resolve().parents[1]; raw=P/'data/raw'
s=(P/'code/classroom_original.R').read_text(); universe=re.findall(r'"([A-Z]+)"',s.split('tickers <- c(')[1].split('prices <-')[0]); universe=list(dict.fromkeys(universe+['SPY']))
def get(t):
 url=f'https://query2.finance.yahoo.com/v8/finance/chart/{t}?period1=1640995200&period2=1761955200&interval=1d'
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
 try:
  b=urllib.request.urlopen(req,timeout=30).read(); j=json.loads(b); r=j['chart']['result'][0]; assert len(r['timestamp'])>900
  (raw/f'{t}.json').write_bytes(b)
  return {'symbol':t,'url':url,'sha256':hashlib.sha256(b).hexdigest(),'rows':len(r['timestamp'])}
 except Exception as e: return {'symbol':t,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex: results=list(ex.map(get,universe))
(raw/'manifest.json').write_text(json.dumps({'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'requested':len(universe),'files':results},indent=2))
print(json.dumps({'requested':len(universe),'success':sum('error' not in r for r in results),'errors':[r for r in results if 'error'in r]},indent=2))
