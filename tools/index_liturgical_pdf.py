"""Index page locations in locally held liturgical PDFs; no body text exported.

Install: python -m pip install pymupdf
Usage: python tools/index_liturgical_pdf.py /path/to/lezionario.pdf --find "I DOMENICA DI AVVENTO"
Only run on documents you are entitled to process. Candidate pages require review.
"""
import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

def normalize(value):
    value=value.translate(str.maketrans({'π':'t','∏':'T','±':'N','ı':'1','Ω':'ff','≈':'fi'}))
    value=unicodedata.normalize('NFKD',value.casefold())
    return ' '.join(re.findall(r'[a-z0-9]+',''.join(c for c in value if not unicodedata.combining(c))))

def matches_heading(text, query):
    needle=normalize(query)
    if not needle:
        return False
    lines=[normalize(line) for line in text.splitlines() if normalize(line)]
    # Exact lines, including headings wrapped across up to three lines.
    return any(' '.join(lines[i:i+n])==needle
               for i in range(len(lines)) for n in (1,2,3))

def inspect_pdf(path, queries):
    import pymupdf
    path=Path(path)
    with path.open('rb') as stream:
        digest=hashlib.file_digest(stream,'sha256').hexdigest()
    with pymupdf.open(path) as doc:
        found={q:[] for q in queries}
        for level,title,page in doc.get_toc():
            for q in queries:
                if normalize(title)==normalize(q) and 1<=page<=len(doc):
                    found[q].append({'pdf_page':page,'method':'bookmark'})
        searchable=0
        for page in doc:
            body=page.get_text(sort=True)
            if body.strip(): searchable+=1
            header='\n'.join(body.splitlines()[:16])
            for q in queries:
                if matches_heading(header,q):
                    found[q].append({'pdf_page':page.number+1,'method':'heading'})
        return {'file':path.name,'sha256':digest,'page_count':len(doc),
                'pages_with_text':searchable,'bookmark_count':len(doc.get_toc()),
                'results':{q:{'candidates':sorted(set(hit['pdf_page'] for hit in hits)),
                              'evidence':hits,'verified':False} for q,hits in found.items()},
                'note':'Page numbers are physical PDF positions, not printed labels. Review manually.'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('pdf',type=Path)
    p.add_argument('--find',action='append',required=True)
    p.add_argument('--output',type=Path)
    args=p.parse_args()
    if args.output and args.output.resolve()==args.pdf.resolve():
        p.error('Output must not overwrite the PDF')
    result=json.dumps(inspect_pdf(args.pdf,args.find),ensure_ascii=False,indent=2)
    if args.output:
        args.output.write_text(result+'\n',encoding='utf-8')
    else:
        print(result)

if __name__=='__main__':
    main()
