"""Source catalog and preliminary volume suggestions, without copyrighted texts."""
from datetime import date
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
    return {'calendar':info,'missal_url':MISSAL_URL,'catalog_url':CATALOG_URL,
            'lectionary_candidates':[{'id':k,'title':VOLUMES[k]} for k in candidates],
            'verified_page':None,'requires_review':True}

if __name__=='__main__':
    import argparse,json
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('date')
    print(json.dumps(sources_for(p.parse_args().date),ensure_ascii=False,indent=2))
