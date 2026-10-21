import zipfile,re,shutil,sys
src='bruto.docx'; dst='Programa-de-Integridade-PGE-MS.docx'
zin=zipfile.ZipFile(src)
zout=zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED)
for it in zin.infolist():
    d=zin.read(it.filename)
    if it.filename=='word/fontTable.xml':
        t=d.decode('utf-8'); t=re.sub(r'w:fontKey="(\{[^}]*\})"',lambda m:'w:fontKey="%s"'%m.group(1).upper(),t); d=t.encode('utf-8')
    elif it.filename=='word/_rels/fontTable.xml.rels':
        pass
    elif it.filename=='word/styles.xml':
        t=d.decode('utf-8')
        for sid,lv in (('Heading1',0),('Heading2',1)):
            m=re.search(r'(<w:style [^>]*w:styleId="%s".*?)(</w:pPr>)'%sid,t,re.S)
            t=t[:m.end(1)]+'<w:outlineLvl w:val="%d"/>'%lv+t[m.end(1):]
        def reord(m):
            inner=m.group(1)
            parts={k:re.search(r'<w:%s [^>]*/>'%k,inner).group(0) for k in ('top','left','bottom','right') if re.search(r'<w:%s [^>]*/>'%k,inner)}
            return '<w:pBdr>'+''.join(parts[k] for k in ('top','left','bottom','right') if k in parts)+'</w:pBdr>'
        t=re.sub(r'<w:pBdr>(.*?)</w:pBdr>',reord,t,flags=re.S)
        d=t.encode('utf-8')
    elif it.filename=='word/document.xml':
        t=d.decode('utf-8')
        ps=list(re.finditer(r'<w:p>(?:(?!</w:p>).)*?</w:p>',t,re.S))
        toc=[m for m in ps if re.search(r'<w:pStyle w:val="TOC[12]"/>',m.group(0))]
        first,last=toc[0],toc[-1]
        begin='<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> TOC \\o "1-2" \\h \\z \\u </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>'
        end='<w:r><w:fldChar w:fldCharType="end"/></w:r>'
        # insere depois do </w:pPr> do primeiro, antes de </w:p> do último
        f=first.group(0); f2=f.replace('</w:pPr>','</w:pPr>'+begin,1)
        l=last.group(0); l2=l[:-len('</w:p>')]+end+'</w:p>'
        t=t[:last.start()]+l2+t[last.end():]
        t=t[:first.start()]+f2+t[first.end():]
        d=t.encode('utf-8')
    zout.writestr(it,d)
zout.close()
print('ok')
