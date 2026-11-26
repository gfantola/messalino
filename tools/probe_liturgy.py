import re, json, urllib.request, datetime, unicodedata
from html.parser import HTMLParser
from zoneinfo import ZoneInfo
class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'): self.skip+=1
        if tag in ('p','br','div','h1','h2','h3','td','tr','b','strong'): self.parts.append('\n')
    def handle_endtag(self,tag):
        if tag in ('script','style'): self.skip=max(0,self.skip-1)
        if tag in ('p','div','h1','h2','h3','td','tr','b','strong'): self.parts.append('\n')
    def handle_data(self,data):
        if not self.skip: self.parts.append(data)
labels={'ingresso':r'antifona(?: d[’\x27]ingresso| di ingresso)?','colletta':'colletta','prima':'prima lettura','salmo':'salmo responsoriale','seconda':'seconda lettura','acclamazione':'(?:acclamazione|canto) al vangelo','vangelo':'vangelo','offerte':'(?:orazione )?sulle offerte','antcom':'antifona alla comunione','dopo':'(?:orazione )?dopo la comunione'}
def probe(url):
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'Messalino diagnostics/1.0'})
        with urllib.request.urlopen(req,timeout=25) as r:
            raw=r.read(3000000); html=raw.decode(r.headers.get_content_charset() or 'utf-8',errors='replace'); status=r.status
        p=Parser();p.feed(html)
        lines=[re.sub(r'\s+',' ',x).strip() for x in ''.join(p.parts).splitlines() if x.strip()]
        hits=[]
        for i,line in enumerate(lines):
            for key,pat in labels.items():
                if re.fullmatch(pat,line,re.I): hits.append((i,key));break
        sections={}
        for j,(i,key) in enumerate(hits):
            end=hits[j+1][0] if j+1<len(hits) else min(i+15,len(lines))
            if key not in sections: sections[key]={'heading_detected':True,'characters_estimate':len(' '.join(lines[i+1:end]))}
        return {'http':status,'bytes':len(raw),'sections':sections}
    except Exception as e: return {'error':type(e).__name__+': '+str(e)}
today=datetime.datetime.now(ZoneInfo('Europe/Rome')).date()
for date in [today,today+datetime.timedelta(days=1),today+datetime.timedelta(days=(6-today.weekday())%7)]:
    key=date.strftime('%Y%m%d')
    for name,url in [('CEI','https://www.chiesacattolica.it/liturgia-del-giorno/?data-liturgia='+key),('LaChiesa','https://www.lachiesa.it/calendario/'+key+'.html')]:
        print(json.dumps({'date':str(date),'source':name,**probe(url)},ensure_ascii=False))
