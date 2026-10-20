"""Download the exact public Census inputs used by Blog 5. No key is required."""
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from datetime import datetime, timezone
import json, hashlib
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
VARIABLES = ['NAME','B25064_001E','B25064_001M','B25119_003E','B25119_003M'] + [f'B25070_{i:03d}E' for i in range(1,12)]
BASE = 'https://api.census.gov/data/2024/acs/acs5'
GEO = 'https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/State_County/MapServer/1/query'

def download(url):
    req = Request(url, headers={'User-Agent':'Blog5EducationalAnalysis/1.0'})
    with urlopen(req, timeout=90) as response:
        data = response.read()
    value = json.loads(data)
    if isinstance(value, dict) and 'error' in value:
        raise ValueError(value['error'])
    return value

def main():
    RAW.mkdir(parents=True, exist_ok=True)
    queries = {
        'acs_counties.json': BASE+'?'+urlencode({'get':','.join(VARIABLES),'for':'county:*','in':'state:42'}),
        'acs_state.json': BASE+'?'+urlencode({'get':','.join(VARIABLES),'for':'state:42'}),
        'pa_counties_5070.json': GEO+'?'+urlencode({'where':"STATE='42'",'outFields':'GEOID,NAME,STATE,COUNTY','returnGeometry':'true','outSR':'5070','geometryPrecision':'0','maxAllowableOffset':'250','f':'json'})
    }
    sources = {}
    for filename, url in queries.items():
        value = download(url)
        if filename=='acs_counties.json':
            assert len(value)==68, f'Expected 67 counties: {len(value)-1}'
        elif filename=='acs_state.json':
            assert len(value)==2, 'Expected one statewide record'
        else:
            assert len(value.get('features',[]))==67, 'Expected 67 county geometries'
            assert not value.get('exceededTransferLimit'), 'Incomplete boundary query'
            sr=value.get('spatialReference',{})
            assert sr.get('wkid')==5070 or sr.get('latestWkid')==5070, sr
        payload=json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()
        (RAW/filename).write_bytes(payload)
        sources[filename]={'url':url,'sha256':hashlib.sha256(payload).hexdigest(),'bytes':len(payload)}
        print(filename, len(payload), 'bytes; validated')
    (RAW/'provenance.json').write_text(json.dumps({'retrieved_utc':datetime.now(timezone.utc).isoformat(),'acs_period':'2020-2024','money_units':'2024 inflation-adjusted dollars','boundary_service':'Census TIGERweb current county layer','projection':'EPSG:5070, NAD83 / Conus Albers','geometry_simplification':'250 metres; presentation only','sources':sources},indent=2)+'\n')

if __name__=='__main__':
    main()
