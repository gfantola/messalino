import datetime, json, re, urllib.request
from zoneinfo import ZoneInfo
from html.parser import HTMLParser
LABELS = {'ingresso':r'antifona(?: d[’\x27]ingresso| di ingresso)?','colletta':'colletta','prima':'prima lettura','salmo':'salmo responsoriale','seconda':'seconda lettura','acclamazione':'(?:acclamazione|canto) al vangelo','vangelo':'vangelo','offerte':'(?:orazione )?sulle offerte','antcom':'antifona alla comunione','dopo':'(?:orazione )?dopo la comunione'}
REF=re.compile(r'\b(?:Ap|Dn|Is|Ger|Ez|Rm|Rom|Mt|Mc|Lc|Gv|Sal|At|Eb|Gen|Es|Dt|Nm|Gb|Pr|Sap|Sir|Qo|Os|Am|Mi|Zc|Ml|Gl|Sof|Na|Ab|Ag|Bar|Lam|Gs|Gdc|Rt|Est|Tb|Gdt|Fil|Gal|Ef|Col|Tt|Fm|Gc|Gd|[12]\s*(?:Cor|Ts|Tm|Pt|Gv|Sam|Re|Cr|Mac))\s+\d+(?:[,:]\s*\d+[a-z]?)?(?:\s*[-–.;,]\s*\d+[a-z]?)*',re.I)
class Node:
    def __init__(self, tag='', attrs=(), parent=None):
        self.tag=tag; self.attrs=dict(attrs); self.parent=parent; self.children=[]
    def walk(self):
        yield self
        for n in self.children:
            if isinstance(n,Node): yield from n.walk()
    def lines(self):
        if self.tag in ('script','style','noscript','nav','footer','header'): return ''
        block=self.tag in ('div','p','h1','h2','h3','h4','section','article','li','br','td','tr','strong','b')
        return ('\n' if block else '')+''.join(n.lines() if isinstance(n,Node) else n for n in self.children)+('\n' if block else '')
class Parser(HTMLParser):
    def __init__(self):
        super().__init__(); self.root=Node(); self.current=self.root
    def handle_starttag(self,tag,attrs):
        n=Node(tag,attrs,self.current);self.current.children.append(n)
        if tag not in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'): self.current=n
    def handle_startendtag(self,tag,attrs):
        self.current.children.append(Node(tag,attrs,self.current))
    def handle_endtag(self,tag):
        n=self.current
        while n.parent:
            if n.tag==tag: self.current=n.parent;return
            n=n.parent
    def handle_data(self,data): self.current.children.append(data)
def clean(s): return [re.sub(r'\s+',' ',x).strip() for x in s.splitlines() if x.strip()]
def key(s):
    return next((k for k,p in LABELS.items() if re.fullmatch(p,s,re.I)),None)
def analyze(html):
    p=Parser();p.feed(html)
    nodes=list(p.root.walk())
    headings=[]
    for n in nodes:
        if n.tag not in ('h1','h2','h3','h4','h5','div','p','strong','b','span'):continue
        lines=clean(n.lines())
        if len(lines)==1 and key(lines[0]):
            if any(isinstance(c,Node) and key(' '.join(clean(c.lines()))) for c in n.children):continue
            headings.append((n,key(lines[0])))
    out={}
    for n,k in headings:
        if k in out:continue
        scope=n.parent
        candidate=None
        while scope and scope.tag not in ('body','html',''):
            lines=clean(scope.lines())
            indices=[i for i,line in enumerate(lines) if key(line)]
            if len(indices)==1 and len(lines)>1 and len(' '.join(lines))<15000:
                candidate=scope
            if len(indices)>1:break
            scope=scope.parent
        if not candidate:
            out[k]={'isolated':False,'heading_tag':n.tag};continue
        lines=clean(candidate.lines())
        idx=next(i for i,line in enumerate(lines) if key(line)==k)
        body=lines[idx+1:]
        joined=' '.join(body)
        refs=[]
        if k in ('prima','seconda','salmo','vangelo','acclamazione'):
            for line in body[:5]:
                for m in REF.finditer(line):
                    if m.group() not in refs:refs.append(m.group())
        out[k]={'isolated':True,'container_tag':candidate.tag,'container_class':re.sub(r'[^a-zA-Z0-9 _-]','',candidate.attrs.get('class',''))[:150],'lines':len(body),'characters':len(joined),'references':refs,'intro_detected':bool(re.search(r'\b(?:dal libro|dalla lettera|dagli atti|dal vangelo|dalla prima|dalla seconda)\b',joined,re.I)),'closing_detected':bool(re.search(r'parola (?:di Dio|del Signore)',joined,re.I)),'refrain_marker':bool(re.search(r'(?:^|\s)(?:R\.|Rit\.)\s',joined,re.I))}
    return out
def main():
    today=datetime.datetime.now(ZoneInfo('Europe/Rome')).date()
    days=sorted({today,today+datetime.timedelta(days=1),today+datetime.timedelta(days=(6-today.weekday())%7)})
    for date in days:
        url='https://www.chiesacattolica.it/liturgia-del-giorno/?data-liturgia='+date.strftime('%Y%m%d')
        expected=set(LABELS)-({'seconda'} if date.weekday()!=6 else set())
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'Messalino diagnostics/2.0'})
            with urllib.request.urlopen(req,timeout=25) as r:
                raw=r.read(3000000);html=raw.decode(r.headers.get_content_charset() or 'utf-8',errors='replace')
            sections=analyze(html)
            print(json.dumps({'date':str(date),'source':url,'sections':sections,'missing':sorted(expected-set(sections)),'not_isolated':[k for k,v in sections.items() if not v['isolated']]},ensure_ascii=False))
        except Exception as e: print(json.dumps({'date':str(date),'error':type(e).__name__+': '+str(e)}))
if __name__=='__main__':main()
