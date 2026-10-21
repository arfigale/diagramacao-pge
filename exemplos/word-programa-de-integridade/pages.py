import json,re,sys,subprocess,pdfplumber
d=json.load(open('conteudo.json'))
pdf=pdfplumber.open(sys.argv[1] if len(sys.argv)>1 else 'Programa-de-Integridade-PGE-MS.pdf')
txt=[(p.extract_text() or '') for p in pdf.pages]
def plain(r): return ''.join(' ' if x.get('br') else x['t'] for x in r)
out={}
last=3  # índice 0-based da página do sumário
for s in d['sumario']:
    t=plain(s['runs']); num=s['num']
    pat=re.compile(r'^\s*'+(re.escape(num)+r'\s+' if num else '')+re.escape(t[:40]),re.M)
    for i in range(last,len(txt)):
        if pat.search(txt[i]):
            out[t+'|'+num]='%02d'%(i+1-2); last=i; break
    else: print('NÃO ACHEI',num,t)
json.dump(out,open('pages.json','w'),ensure_ascii=False); print(len(out))
