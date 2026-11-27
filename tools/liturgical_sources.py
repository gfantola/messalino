"""Source catalog and preliminary volume suggestions, without copyrighted texts."""
from datetime import date
import json
from pathlib import Path
from liturgical_calendar import calendar_day

CATALOG_URL = 'https://liturgia.it/content/libri_liturgici_ita/index.htm'
MISSAL_URL = 'https://liturgico.chiesacattolica.it/messale-romanoterza-edizione-italiana/'
VOLUMES = {
    'A':'Lezionario domenicale e festivo - A',
    'B':'Lezionario domenicale e festivo - B',
    'C':'Lezionario domenicale e festivo - C',
    'I':'Lezionario feriale - anno dispari',
    'II':'Lezionario feriale - anno pari',
    'strong':'Lezionario feriale - tempi forti',
    'saints':'Lezionario per le celebrazioni dei santi',
    'votive':'Lezionario per le messe votive',
    'ritual':'Lezionario per le messe rituali',
}

def sources_for(value):
    day=date.fromisoformat(value) if isinstance(value,str) else value
    info=calendar_day(day)
    normal=info['sunday_cycle'] if day.weekday()==6 else (
        ('II' if day.year%2==0 else 'I') if info['season']=='Tempo Ordinario' else 'strong')
    candidates=[normal]
    if info.get('rank'):
        candidates=list(dict.fromkeys(['saints',info['sunday_cycle'],normal]))
    elif info['title'] in ('Natale del Signore','Epifania del Signore','Maria Santissima Madre di Dio'):
        candidates=[info['sunday_cycle'],'strong']
    page_index=None
    if (day.weekday()==6 and info['season']=='Avvento' and info['sunday_cycle']=='B'
            and not info.get('rank') and info['week'] in (1,2,3,4)):
        catalog=json.loads((Path(__file__).resolve().parent.parent/'data'/'liturgical_advent_b_index.json').read_text(encoding='utf-8'))
        page_index=next(e for e in catalog['entries'] if e['week']==info['week'])
        page_index={'locations':page_index,'documents':catalog['documents'],'scope':catalog['scope']}
    return {'calendar':info,'missal_url':MISSAL_URL,'catalog_url':CATALOG_URL,
            'lectionary_candidates':[{'id':k,'title':VOLUMES[k]} for k in candidates],
            'indexed_pages':page_index,'requires_review':True}

if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('date')
    print(json.dumps(sources_for(p.parse_args().date),ensure_ascii=False,indent=2))
