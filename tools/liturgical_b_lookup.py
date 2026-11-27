"""Resolve indexed pages for Year B, not an authoritative Ordo."""
import json
from pathlib import Path
from liturgical_calendar import calendar_day

INDEX=Path(__file__).resolve().parent.parent/'data'/'liturgical_b_index.json'

TITLE_IDS={
    'Natale del Signore':'christmas-day',
    'Maria Santissima Madre di Dio':'mary-mother-of-god',
    'Epifania del Signore':'epiphany-day',
    'Battesimo del Signore':'baptism',
    'Domenica delle Palme':'palms',
    'Giovedì Santo':'holy-thursday',
    'Venerdì Santo':'good-friday',
    'Pasqua di Risurrezione':'easter-day',
    'Ascensione del Signore':'ascension',
    'Pentecoste':'pentecost-day',
    'Santissima Trinità':'trinity',
    'Santissimo Corpo e Sangue di Cristo':'corpus-christi',
    'Sacratissimo Cuore di Gesù':'sacred-heart',
    'Cristo Re dell’Universo':'christ-king',
    'Presentazione del Signore':'02-02',
    'Natività di San Giovanni Battista':'06-24-day',
    'Santi Pietro e Paolo':'06-29-day',
    'Trasfigurazione del Signore':'08-06',
    'Assunzione della Beata Vergine Maria':'08-15-day',
    'Esaltazione della Santa Croce':'09-14',
    'Tutti i Santi':'11-01',
    'Commemorazione di tutti i fedeli defunti':'11-02-1',
    'Dedicazione della Basilica Lateranense':'11-09',
    'Immacolata Concezione':'12-08'
}
SEASONS={'Avvento':'advent','Quaresima':'lent','Pasqua':'easter','Tempo Ordinario':'ordinary'}

def lookup_id(key):
    catalog=json.loads(INDEX.read_text(encoding='utf-8'))
    entry=next((e for e in catalog['entries'] if e['id']==key),None)
    return {'entry':entry,'documents':catalog['documents'],'requires_review':True,
            'numbering':catalog['numbering']} if entry else None

def lookup_date(value):
    info=calendar_day(value)
    if info['sunday_cycle']!='B':
        return None
    title=info['title']
    key=TITLE_IDS.get(title)
    if key is None and title.startswith('Domenica - ') and info['season'] in SEASONS and info['week']:
        key=SEASONS[info['season']]+'-'+str(info['week'])
    return lookup_id(key) if key else None

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--date')
    g.add_argument('--id')
    args=p.parse_args()
    print(json.dumps(lookup_date(args.date) if args.date else lookup_id(args.id),ensure_ascii=False,indent=2))
