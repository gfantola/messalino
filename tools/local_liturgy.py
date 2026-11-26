"""Local personal-use server. No texts are committed or uploaded.
Run from the repository root: python3 tools/local_liturgy.py
Use only sources and texts you are entitled to reproduce.
"""
import datetime, json, pathlib, re, urllib.request, urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from zoneinfo import ZoneInfo
from probe_cei_structure import Parser, clean, key
ROOT=pathlib.Path(__file__).resolve().parent.parent
CACHE={}
def acquire(date):
    if date in CACHE:return CACHE[date]
    url='https://www.chiesacattolica.it/liturgia-del-giorno/?data-liturgia='+date.replace('-','')
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Messalino personal reader/1.0'}),timeout=25) as response:
        html=response.read(3000000).decode(response.headers.get_content_charset() or 'utf-8',errors='replace')
    parser=Parser();parser.feed(html)
    data={}
    for node in parser.root.walk():
        if 'cci-liturgia-giorno-dettagli-content' not in node.attrs.get('class','').split():continue
        lines=clean(node.lines())
        hits=[(i,key(line)) for i,line in enumerate(lines) if key(line)]
        if len(hits)!=1:continue
        i,k=hits[0]
        if k in data:continue
        text='\n'.join(lines[i+1:]).strip()
        if k in ('prima','seconda','vangelo'):
            text=re.sub(r'\s*Parola (?:di Dio|del Signore)\.?\s*$','',text,flags=re.I).strip()
        if text:data[k]=text
    if not all(data.get(k) for k in ('prima','salmo','vangelo')):raise ValueError('Sezioni principali non riconosciute')
    result={'date':date,'source':url,'data':data}
    CACHE[date]=result
    return result
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def do_GET(self):
        u=urllib.parse.urlsplit(self.path)
        if u.path!='/api/day':return super().do_GET()
        try:
            date=urllib.parse.parse_qs(u.query)['date'][0]
            if datetime.date.fromisoformat(date).isoformat()!=date:raise ValueError()
            result=acquire(date);status=200
        except Exception as e:
            result={'error':str(e)};status=502
        payload=json.dumps(result,ensure_ascii=False).encode()
        self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
if __name__=='__main__':
    print('Messalino locale: http://127.0.0.1:8765')
    ThreadingHTTPServer(('127.0.0.1',8765),Handler).serve_forever()
