import json,re,sys
from bs4 import BeautifulSoup, NavigableString, Tag
s=BeautifulSoup(open(sys.argv[1] if len(sys.argv)>1 else '../documento.html',encoding='utf-8').read(),'html.parser')
body=s.body
def norm(t): return re.sub(r'[ \t\r\n]+',' ',t.replace(' ',' '))
def runs(el,b=False,i=False,href=None):
    out=_r(el,b,i,href)
    return trim(out)
def _r(el,b=False,i=False,href=None):
    out=[]
    for c in el.children:
        if isinstance(c,NavigableString):
            t=norm(str(c))
            if t: out.append({'t':t,'b':b,'i':i,'href':href})
        elif isinstance(c,Tag):
            if c.name=='br': out.append({'br':True})
            elif c.name in('strong','b'): out+=_r(c,True,i,href)
            elif c.name in('em','i'): out+=_r(c,b,True,href)
            elif c.name=='a': out+=_r(c,b,i,c.get('href'))
            elif c.name in('ol','ul'): continue
            else: out+=_r(c,b,i,href)
    return out
def trim(out):
    # trim
    while out and out[0].get('t') is not None and not out[0]['t'].strip(): out.pop(0)
    while out and out[-1].get('t') is not None and not out[-1]['t'].strip(): out.pop()
    if out and 't' in out[0]: out[0]['t']=out[0]['t'].lstrip()
    if out and 't' in out[-1]: out[-1]['t']=out[-1]['t'].rstrip()
    return out
def lst(el): return [runs(li) for li in el.find_all('li',recursive=False)]
def cell(td):
    d={'runs':runs(td)}
    return d
blocks=[]
started=False
for el in body.find_all(recursive=False):
    cl=el.get('class',[]); n=el.name
    if n=='div' and 'sumario' in cl: started=True; continue
    if not started: continue
    if 'contracapa' in cl: break
    if n=='h2':
        num=el.select_one('.num'); tit=el.select_one('.titulo')
        blocks.append({'k':'h2','num':num.get_text() if num else '','runs':runs(tit),'pb':'quebra-antes' in cl})
    elif n=='h3':
        num=el.select_one('.num'); 
        if num: num.extract()
        blocks.append({'k':'h3','num':num.get_text() if num else '','runs':runs(el)})
    elif n=='p' and 'eixo' in cl:
        lab=el.select_one('.eixo-num'); t=lab.get_text(); lab.extract()
        blocks.append({'k':'eixo','label':t,'runs':runs(el)})
    elif n=='p' and 'grupo' in cl:
        blocks.append({'k':'grupo','runs':runs(el)})
    elif n=='p' and 'anexo-sobre' in cl:
        blocks.append({'k':'anexosobre','runs':runs(el)})
    elif n=='p':
        blocks.append({'k':'p','runs':runs(el)})
    elif n in('ul','ol'):
        blocks.append({'k':n,'items':lst(el)})
    elif n=='blockquote':
        blocks.append({'k':'quote','runs':runs(el.find('p'))})
    elif n=='table':
        cap=el.find('caption')
        head=[runs(th) for th in el.find('thead').find_all('th')]
        rows=[[runs(td) for td in tr.find_all('td')] for tr in el.find('tbody').find_all('tr')]
        blocks.append({'k':'table','cap':runs(cap) if cap else None,'head':head,'rows':rows,'pct':'maturidade' in cl})
    elif n=='div' and 'acao' in cl:
        rows=[]
        for d in el.select('dl.acao-campos > div'):
            dd=d.find('dd'); ol=dd.find(['ol','ul'])
            rows.append({'label':d.find('dt').get_text(),'runs':runs(dd),'items':lst(ol) if ol else None,'ol':ol is not None and ol.name=='ol'})
        blocks.append({'k':'acao','num':el.select_one('.acao-num').get_text(),'title':el.select_one('.acao-tit').get_text(),'rows':rows})
    elif n=='figure':
        cap=el.find('figcaption'); fo=el.select_one('.fig-fonte')
        kind='org' if 'org-img' in cl else ('cv' if 'cv' in cl else 'gov')
        blocks.append({'k':'figure','kind':kind,'cap':runs(cap),'fonte':fo.get_text() if fo else ''})
    elif n=='dl':
        blocks.append({'k':'ficha','items':[[dt.get_text(),runs(dt.find_next_sibling('dd'))] for dt in el.find_all('dt')]})
    elif n=='div' and 'assinatura' in cl:
        blocks.append({'k':'assinatura','nome':el.select_one('.nome').get_text(),'cargo':runs(el.select_one('.cargo'))})
    else:
        print('IGNORADO',n,cl)
# sumário
sum_=[]
for li in body.select('div.sumario li'):
    sum_.append({'sub':'sub' in li.get('class',[]),'num':li.select_one('.s-num').get_text(),'runs':runs(li.select_one('.s-tit span'))})
# expediente
exp=[]
for bl in body.select('section.expediente .ex-bloco'):
    items=[(p.get('class')[0],runs(p)) for p in bl.find_all('p')]
    exp.append(items)
cc={'unidade':runs(body.select_one('.cc-unidade'))}
json.dump({'blocks':blocks,'sumario':sum_,'exp':exp},open('conteudo.json','w',encoding='utf-8'),ensure_ascii=False)
from collections import Counter
print(Counter(b['k'] for b in blocks)); print(len(sum_),len(exp))
