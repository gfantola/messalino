"""Core Roman liturgical calendar for Italy (temporal cycle only).
Not a complete Ordo: saints, local celebrations and precedence require overlays.
Dates refer to daytime Mass, not vigil Mass.
"""
from datetime import date, timedelta

def sunday_on_or_after(d):
    return d + timedelta(days=(6-d.weekday())%7)

def advent(y):
    return sunday_on_or_after(date(y,11,27))

def easter(y):
    # Gregorian computus, Meeus/Jones/Butcher
    a=y%19; b,c=divmod(y,100); d,e=divmod(b,4)
    f=(b+8)//25; g=(b-f+1)//3
    h=(19*a+b-d-g+15)%30
    i,k=divmod(c,4); l=(32+2*e+2*i-h-k)%7
    m=(a+11*h+22*l)//451
    month,day=divmod(h+l-7*m+114,31)
    return date(y,month,day+1)

def calendar_day(day):
    if isinstance(day,str): day=date.fromisoformat(day)
    y=day.year; p=easter(y); a=advent(y)
    ly=y+int(day>=a)
    cycle=('C','A','B')[ly%3]
    baptism=sunday_on_or_after(date(y,1,7))
    ash=p-timedelta(days=46); pent=p+timedelta(days=49)
    fixed={date(y,1,1):('Maria Santissima Madre di Dio','bianco'),
           date(y,1,6):('Epifania del Signore','bianco'),
           date(y,12,25):('Natale del Signore','bianco')}
    movable={baptism:('Battesimo del Signore','bianco'),
             ash:('Mercoledì delle Ceneri','viola'),
             p-timedelta(days=7):('Domenica delle Palme','rosso'),
             p-timedelta(days=3):('Giovedì Santo','bianco'),
             p-timedelta(days=2):('Venerdì Santo','rosso'),
             p-timedelta(days=1):('Sabato Santo',None),
             p:('Pasqua di Risurrezione','bianco'),
             p+timedelta(days=42):('Ascensione del Signore','bianco'),
             pent:('Pentecoste','rosso'),
             pent+timedelta(days=7):('Santissima Trinità','bianco'),
             pent+timedelta(days=14):('Santissimo Corpo e Sangue di Cristo','bianco'),
             pent+timedelta(days=19):('Sacratissimo Cuore di Gesù','bianco'),
             a-timedelta(days=7):('Cristo Re dell’Universo','bianco')}
    # Major fixed celebrations; remaining sanctoral and local entries are not yet covered.
    solemnities={(3,19):('San Giuseppe','bianco'),(3,25):('Annunciazione del Signore','bianco'),
        (6,24):('Natività di San Giovanni Battista','bianco'),(6,29):('Santi Pietro e Paolo','rosso'),
        (8,15):('Assunzione della Beata Vergine Maria','bianco'),(11,1):('Tutti i Santi','bianco'),
        (12,8):('Immacolata Concezione','bianco')}
    lord_feasts={(2,2):('Presentazione del Signore','bianco'),(8,6):('Trasfigurazione del Signore','bianco'),
        (9,14):('Esaltazione della Santa Croce','rosso'),(11,9):('Dedicazione della Basilica Lateranense','bianco')}
    blocked=set(fixed)|set(movable)
    def privileged(d):
        return (p-timedelta(days=7)<=d<=p+timedelta(days=7)
            or d==ash or d in blocked
            or (d.weekday()==6 and (a<=d<date(y,12,25) or ash<=d<=pent)))
    assigned={}
    for (month,number),entry in solemnities.items():
        original=date(y,month,number); target=original
        if (month,number)==(3,19) and p-timedelta(days=7)<=target<p:
            target=p-timedelta(days=8)
        elif (month,number)==(3,25) and p-timedelta(days=7)<=target<=p+timedelta(days=7):
            target=p+timedelta(days=8)
        while privileged(target) or target in assigned:
            target+=timedelta(days=1)
        assigned[target]=(entry,original)
    week=None
    if day>=date(y,12,25) or day<=baptism:
        season='Natale'; color='bianco'
    elif day>=a:
        season='Avvento'; color='viola'; week=(day-a).days//7+1
    elif ash<=day<p-timedelta(days=3):
        season='Quaresima'; color='viola'
        week=max(0,(day-(ash+timedelta(days=4))).days//7+1)
    elif p-timedelta(days=3)<=day<p:
        season='Triduo pasquale'; color=None
    elif p<=day<=pent:
        season='Pasqua'; color='bianco'; week=(day-p).days//7+1
    else:
        season='Tempo Ordinario'; color='verde'
        if day<ash:
            week=(day-baptism).days//7+1
        else:
            week=34-((a-timedelta(days=7)-day).days+6)//7
    if season=='Tempo Ordinario' and day>pent:
        week=34-((a-timedelta(days=7))-(day-timedelta(days=(day.weekday()+1)%7))).days//7
    names=['Lunedì','Martedì','Mercoledì','Giovedì','Venerdì','Sabato','Domenica']
    title=names[day.weekday()]+' - '+season+(f' - settimana {week}' if week is not None else '')
    if day in movable: title,color=movable[day]
    if day in fixed: title,color=fixed[day]
    rank=None; transferred_from=None
    if day in assigned:
        (title,color),original=assigned[day]; rank='solennità'
        if original!=day: transferred_from=original.isoformat()
    elif (day.month,day.day) in lord_feasts and not privileged(day) and not (ash<=day<p and day.weekday()==6):
        title,color=lord_feasts[(day.month,day.day)]; rank='festa'
    elif day==date(y,11,2) and day not in fixed and day not in movable:
        title,color='Commemorazione di tutti i fedeli defunti','viola'; rank='commemorazione'
    return {'date':day.isoformat(),'liturgical_year':ly,'sunday_cycle':cycle,
            'weekday_cycle':'II' if ly%2==0 else 'I','season':season,'week':week,
            'title':title,'color':color,'rank':rank,'transferred_from':transferred_from,'complete':False,
            'scope':'Temporale romano e principali celebrazioni fisse; precedenze e santorale parziali'}

if __name__=='__main__':
    import argparse,json
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('date',help='YYYY-MM-DD')
    print(json.dumps(calendar_day(parser.parse_args().date),ensure_ascii=False,indent=2))
