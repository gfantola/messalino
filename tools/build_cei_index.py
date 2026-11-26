import datetime,json,pathlib,urllib.request
from zoneinfo import ZoneInfo
from probe_cei_structure import analyze
today=datetime.datetime.now(ZoneInfo('Europe/Rome')).date()
for offset in range(-1,15):
    date=today+datetime.timedelta(days=offset)
    key=date.isoformat()
    url='https://www.chiesacattolica.it/liturgia-del-giorno/?data-liturgia='+date.strftime('%Y%m%d')
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Messalino reference index/1.0'}),timeout=25) as response:
            html=response.read(3000000).decode(response.headers.get_content_charset() or 'utf-8',errors='replace')
        sections=analyze(html)
        refs={k:v['references'] for k,v in sections.items() if v.get('isolated') and v.get('references')}
        if not all(refs.get(k) for k in ('prima','salmo','vangelo')): raise ValueError('Incomplete references')
        data={'date':key,'source':url,'references':refs,'sections':sorted(k for k,v in sections.items() if v.get('isolated'))}
        path=pathlib.Path('data/cei')/(key+'.json')
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(key,refs)
    except Exception as e:
        print(key,'ERROR',type(e).__name__,str(e))
