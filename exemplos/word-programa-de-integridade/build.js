const fs=require('fs');
const D=require('docx');
const {LineRuleType,Document,Packer,Paragraph,TextRun,ImageRun,Table,TableRow,TableCell,WidthType,ShadingType,BorderStyle,AlignmentType,TabStopType,LeaderType,Header,Footer,PageNumber,HeadingLevel,LevelFormat,ExternalHyperlink,VerticalAlign,SectionType,HorizontalPositionRelativeFrom,VerticalPositionRelativeFrom,TextWrappingType,NumberFormat,TableLayoutType,CharacterSet}=D;
const C=JSON.parse(fs.readFileSync('conteudo.json','utf8'));
const pages=fs.existsSync('pages.json')?JSON.parse(fs.readFileSync('pages.json','utf8')):{};
const BLUE='294964',ORANGE='F58634',GRAYT='5A6673',LINE='D2D3D5',ZEBRA='F3F5F7',FONT='Source Sans 3';
const TW=9072;
const DIMS=JSON.parse(fs.readFileSync('dims.json','utf8'));function dim(f){return DIMS[f]}
function img(f,wpx,type){const[w,h]=dim(f);return new ImageRun({type:type||(f.endsWith('jpg')?'jpg':'png'),data:fs.readFileSync(f),transformation:{width:wpx,height:Math.round(wpx*h/w)},altText:{title:f,description:f,name:f}});}
function mk(runs,o={}){const out=[];for(const r of runs||[]){
 if(r.br){out.push(new TextRun({break:1}));continue}
 const t=new TextRun({text:r.t,bold:(o.bold||r.b)||undefined,italics:(o.italics||r.i)||undefined,color:o.color,size:o.size,font:FONT,characterSpacing:o.cs});
 if(r.href){out.push(new ExternalHyperlink({link:r.href,children:[new TextRun({text:r.t,bold:(o.bold||r.b)||undefined,italics:(o.italics||r.i)||undefined,color:'1F5F8B',underline:{},size:o.size,font:FONT})]}))}
 else out.push(t);}return out;}
const plain=r=>(r||[]).map(x=>x.br?' ':x.t).join('');
const body=[];
let listInst=0;
function cellPars(runs,o={}){ // runs com br -> parágrafos
 return [new Paragraph({children:mk(runs,o),alignment:o.align||AlignmentType.LEFT,spacing:{after:o.after??30,line:o.line||276,lineRule:LineRuleType.EXACT},indent:{firstLine:0}})];}
function bord(c,sz=4){return{style:BorderStyle.SINGLE,size:sz,color:c}}
const NONE={style:BorderStyle.NONE,size:0,color:'FFFFFF'};
function widths(cols,rows,min=900){const w=cols.map((_,i)=>{let s=0,n=0;for(const r of rows){s+=plain(r[i]).length;n++}return Math.min(48,Math.max(9,s/Math.max(n,1)))});const sum=w.reduce((a,b)=>a+b,0);let ws=w.map(x=>Math.max(min,Math.round(x/sum*TW)));const d=TW-ws.reduce((a,b)=>a+b,0);ws[ws.indexOf(Math.max(...ws))]+=d;return ws;}
function table(b){
 const rows=b.rows.map((r,ri)=>r);
 const ws=b.pct?[2300,1500,1500,3772]:widths(b.head,[b.head,...b.rows]);
 const hcell=(r,i)=>new TableCell({width:{size:ws[i],type:WidthType.DXA},shading:{type:ShadingType.CLEAR,fill:BLUE,color:'auto'},verticalAlign:VerticalAlign.CENTER,margins:{top:90,bottom:90,left:110,right:110},borders:{top:NONE,left:NONE,right:NONE,bottom:NONE},children:cellPars(r,{bold:true,color:'FFFFFF',size:16,cs:20})});
 const trs=[new TableRow({tableHeader:true,cantSplit:true,children:b.head.map((r,i)=>hcell(r,i))})];
 b.rows.forEach((r,ri)=>{trs.push(new TableRow({cantSplit:true,children:r.map((c,i)=>{
  let pars;
  if(b.pct&&i===2){const v=parseInt(plain(c));const n=Math.round(v/10);pars=[new Paragraph({spacing:{after:0,line:240},indent:{firstLine:0},children:[new TextRun({text:v+'%',bold:true,color:BLUE,size:20,font:FONT}),new TextRun({break:1}),new TextRun({text:'█'.repeat(n),color:BLUE,size:14,font:FONT}),new TextRun({text:'█'.repeat(10-n),color:LINE,size:14,font:FONT})]})];}
  else pars=cellPars(c,{size:20});
  return new TableCell({width:{size:ws[i],type:WidthType.DXA},shading:ri%2?{type:ShadingType.CLEAR,fill:ZEBRA,color:'auto'}:undefined,margins:{top:90,bottom:90,left:110,right:110},verticalAlign:VerticalAlign.TOP,borders:{top:NONE,left:NONE,right:NONE,bottom:bord(LINE)},children:pars});})}))});
 const out=[];
 if(b.cap) out.push(new Paragraph({keepNext:true,spacing:{before:200,after:100},indent:{firstLine:0},alignment:AlignmentType.LEFT,children:mk(b.cap,{bold:true,color:BLUE,size:17,cs:20})}));
 out.push(new Table({width:{size:TW,type:WidthType.DXA},columnWidths:ws,layout:TableLayoutType.FIXED,rows:trs}));
 out.push(new Paragraph({spacing:{after:120},children:[]}));
 return out;}
function acao(b){
 const ws=[2200,TW-2200];
 const none={top:NONE,left:NONE,right:NONE,bottom:NONE};
 const trs=[new TableRow({cantSplit:true,children:[new TableCell({columnSpan:2,width:{size:TW,type:WidthType.DXA},shading:{type:ShadingType.CLEAR,fill:BLUE,color:'auto'},margins:{top:110,bottom:110,left:160,right:160},borders:none,children:[new Paragraph({keepNext:true,indent:{firstLine:0},spacing:{after:0},children:[new TextRun({text:b.num.toUpperCase()+'  ',bold:true,color:ORANGE,size:17,characterSpacing:20,font:FONT}),new TextRun({text:b.title,bold:true,color:'FFFFFF',size:22,font:FONT})]})]})]})];
 b.rows.forEach((r,ri)=>{
  let vp;
  if(r.items){const inst=++listInst;vp=r.items.map(it=>new Paragraph({numbering:{reference:r.ol?'dec':'bul',level:0,instance:r.ol?inst:undefined},spacing:{after:50,line:276,lineRule:LineRuleType.EXACT},indent:{left:360,hanging:300,firstLine:undefined},children:mk(it,{size:19})}));}
  else vp=cellPars(r.runs,{size:19});
  trs.push(new TableRow({cantSplit:false,children:[
   new TableCell({width:{size:ws[0],type:WidthType.DXA},shading:ri%2?{type:ShadingType.CLEAR,fill:ZEBRA,color:'auto'}:undefined,margins:{top:90,bottom:90,left:160,right:100},borders:{top:bord(LINE),left:NONE,right:NONE,bottom:NONE},children:[new Paragraph({indent:{firstLine:0},spacing:{after:0},alignment:AlignmentType.LEFT,children:[new TextRun({text:r.label,bold:true,color:BLUE,size:18,font:FONT})]})]}),
   new TableCell({width:{size:ws[1],type:WidthType.DXA},shading:ri%2?{type:ShadingType.CLEAR,fill:ZEBRA,color:'auto'}:undefined,margins:{top:90,bottom:90,left:100,right:160},borders:{top:bord(LINE),left:NONE,right:NONE,bottom:NONE},children:vp})]}));});
 return [new Table({width:{size:TW,type:WidthType.DXA},columnWidths:ws,layout:TableLayoutType.FIXED,rows:trs,borders:{top:NONE,bottom:bord(LINE),left:bord(LINE),right:bord(LINE),insideHorizontal:NONE,insideVertical:NONE}}),new Paragraph({spacing:{after:200},children:[]})];}
const figf={org:['fig1.jpg',604],cv:['fig2.png',604],gov:['fig3.png',604]};
for(const b of C.blocks){
 switch(b.k){
 case 'h2':body.push(new Paragraph({heading:HeadingLevel.HEADING_1,pageBreakBefore:b.pb,children:[...(b.num?[new TextRun({text:b.num+'  ',font:FONT})]:[]),...mk(b.runs)]}));break;
 case 'h3':body.push(new Paragraph({heading:HeadingLevel.HEADING_2,children:[...(b.num?[new TextRun({text:b.num+'  ',font:FONT})]:[]),...mk(b.runs)]}));break;
 case 'eixo':body.push(new Paragraph({keepNext:true,spacing:{before:320,after:110},indent:{firstLine:0},alignment:AlignmentType.LEFT,children:[new TextRun({text:b.label.toUpperCase()+'  ',bold:true,color:ORANGE,size:17,characterSpacing:20,font:FONT}),...mk(b.runs,{bold:true,color:BLUE,size:25})]}));break;
 case 'grupo':body.push(new Paragraph({keepNext:true,spacing:{before:200,after:100},indent:{firstLine:0},alignment:AlignmentType.LEFT,children:mk(b.runs,{bold:true,color:BLUE,size:24})}));break;
 case 'anexosobre':body.push(new Paragraph({spacing:{after:200},indent:{firstLine:0},alignment:AlignmentType.LEFT,children:mk(b.runs,{color:GRAYT,size:20})}));break;
 case 'p':body.push(new Paragraph({children:mk(b.runs)}));break;
 case 'ul':case 'ol':{const inst=++listInst;b.items.forEach(it=>body.push(new Paragraph({numbering:{reference:b.k==='ol'?'dec':'bul',level:0,instance:b.k==='ol'?inst:undefined},spacing:{after:80,line:360},alignment:AlignmentType.LEFT,children:mk(it)})));body.push(new Paragraph({spacing:{after:60},children:[]}));break;}
 case 'quote':body.push(new Paragraph({spacing:{before:120,after:200,line:340,lineRule:LineRuleType.EXACT},indent:{left:360,right:200,firstLine:0},shading:{type:ShadingType.CLEAR,fill:'EAF4F5',color:'auto'},border:{left:{style:BorderStyle.SINGLE,size:24,color:'51A8B1',space:10}},alignment:AlignmentType.LEFT,children:mk(b.runs,{italics:true,color:BLUE})}));break;
 case 'table':body.push(...table(b));break;
 case 'acao':body.push(...acao(b));break;
 case 'figure':{const[f,w]=figf[b.kind];
  body.push(new Paragraph({keepNext:true,spacing:{before:200,after:120},indent:{left:140,firstLine:0},alignment:AlignmentType.LEFT,border:{left:{style:BorderStyle.SINGLE,size:18,color:ORANGE,space:8}},children:mk(b.cap,{color:'000000',size:21,bold:true}).map(x=>x)}));
  body.push(new Paragraph({keepNext:true,spacing:{after:40,line:240,lineRule:LineRuleType.AUTO},indent:{firstLine:0},alignment:AlignmentType.CENTER,children:[img(f,w)]}));
  body.push(new Paragraph({spacing:{after:200},indent:{firstLine:0},alignment:AlignmentType.LEFT,children:[new TextRun({text:b.fonte,color:GRAYT,size:18,font:FONT})]}));break;}
 case 'ficha':{const ws=[2400,TW-2400];body.push(new Table({width:{size:TW,type:WidthType.DXA},columnWidths:ws,layout:TableLayoutType.FIXED,rows:b.items.map(([l,v],ri)=>new TableRow({cantSplit:true,children:[
   new TableCell({width:{size:ws[0],type:WidthType.DXA},margins:{top:80,bottom:80,left:110,right:110},borders:{top:NONE,left:NONE,right:NONE,bottom:bord(LINE)},children:cellPars([{t:l,b:true}],{color:BLUE,size:20})}),
   new TableCell({width:{size:ws[1],type:WidthType.DXA},margins:{top:80,bottom:80,left:110,right:110},borders:{top:NONE,left:NONE,right:NONE,bottom:bord(LINE)},children:cellPars(v,{size:20})})]}))}));body.push(new Paragraph({spacing:{after:160},children:[]}));break;}
 case 'assinatura':body.push(new Paragraph({spacing:{before:900,after:0},indent:{left:2200,right:2200,firstLine:0},alignment:AlignmentType.CENTER,border:{top:{style:BorderStyle.SINGLE,size:6,color:'000000',space:4}},children:[new TextRun({text:b.nome,bold:true,size:22,font:FONT})]}));body.push(new Paragraph({spacing:{after:0},indent:{firstLine:0},alignment:AlignmentType.CENTER,children:mk(b.cargo,{size:20})}));break;
 }}
// sumário
const sumP=[new Paragraph({spacing:{before:0,after:240},indent:{firstLine:0},alignment:AlignmentType.LEFT,border:{top:{style:BorderStyle.SINGLE,size:6,color:BLUE,space:8},bottom:{style:BorderStyle.SINGLE,size:6,color:BLUE,space:8}},children:[new TextRun({text:'Sumário',bold:true,color:BLUE,size:34,font:FONT})]})];
C.sumario.forEach((s,k)=>{const key=(s.num?s.num+' ':'')+plain(s.runs);const pg=pages[plain(s.runs)+'|'+s.num]||'00';
 sumP.push(new Paragraph({style:s.sub?'TOC2':'TOC1',children:[...(s.num?[new TextRun({text:s.num+(s.sub?'':'.'),font:FONT}),new TextRun({text:'\t',font:FONT})]:[]),...mk(s.runs),new TextRun({text:'\t'+pg,font:FONT})]}));});
// cabeçalho/rodapé
const hdr=new Header({children:[new Paragraph({tabStops:[{type:TabStopType.RIGHT,position:TW}],spacing:{after:0,line:240,lineRule:LineRuleType.AUTO},indent:{firstLine:0},border:{bottom:{style:BorderStyle.SINGLE,size:6,color:LINE,space:6}},children:[img('logo-azul.png',118),new TextRun({text:'\tPROGRAMA DE INTEGRIDADE',color:BLUE,size:15,characterSpacing:50,bold:true,font:FONT})]})]});
const ftr=new Footer({children:[new Paragraph({tabStops:[{type:TabStopType.RIGHT,position:TW}],spacing:{after:0,line:240,lineRule:LineRuleType.AUTO},indent:{firstLine:0},border:{top:{style:BorderStyle.SINGLE,size:6,color:LINE,space:6}},children:[new TextRun({text:'Comitê Setorial de Compliance Público – PGE/MS',color:BLUE,size:15,bold:true,font:FONT}),new TextRun({children:['\tPÁG. ',PageNumber.CURRENT,' DE ',PageNumber.TOTAL_PAGES_IN_SECTION],color:GRAYT,size:15,font:FONT})]})]});
const emptyH=()=>new Header({children:[new Paragraph({children:[]})]});const emptyF=()=>new Footer({children:[new Paragraph({children:[]})]});
const A4={width:11906,height:16838};
function fullPage(f){const[w,h]=dim(f);return new Paragraph({spacing:{after:0,line:240,lineRule:LineRuleType.AUTO},indent:{firstLine:0},children:[new ImageRun({type:'png',data:fs.readFileSync(f),transformation:{width:794,height:1123},altText:{title:'Página',description:'Página inteira',name:f},floating:{horizontalPosition:{relative:HorizontalPositionRelativeFrom.PAGE,offset:0},verticalPosition:{relative:VerticalPositionRelativeFrom.PAGE,offset:0},behindDocument:true,wrap:{type:TextWrappingType.NONE}}})]});}
// expediente
const exp=[new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:0,after:500,line:240,lineRule:LineRuleType.AUTO},indent:{firstLine:0},children:[img('logo-azul.png',250)]})];
C.exp.forEach(bl=>{bl.forEach(([cl,r])=>{
 if(cl==='ex-rot')exp.push(new Paragraph({keepNext:true,spacing:{before:300,after:100},indent:{firstLine:0},alignment:AlignmentType.LEFT,border:{top:{style:BorderStyle.SINGLE,size:6,color:BLUE,space:5},bottom:{style:BorderStyle.SINGLE,size:6,color:BLUE,space:5}},children:mk(r,{bold:true,color:BLUE,size:30})}));
 else if(cl==='ex-nome')exp.push(new Paragraph({keepNext:true,spacing:{before:60,after:0},indent:{firstLine:0},alignment:AlignmentType.LEFT,children:mk(r,{bold:true,size:21})}));
 else exp.push(new Paragraph({spacing:{after:0},indent:{firstLine:0},alignment:AlignmentType.LEFT,children:mk(r,{size:21})}));});});
const props=(m)=>({page:{size:A4,margin:m}});
const doc=new Document({
 creator:'Comitê Setorial de Compliance Público – PGE/MS',title:'Programa de Integridade – PGE/MS',
 features:{updateFields:false},
 fonts:[{name:FONT,data:fs.readFileSync(require('path').join(__dirname,'..','..','assets','design-system','fonts','SourceSans3-Regular.ttf')),characterSet:CharacterSet.ANSI}],
 styles:{default:{document:{run:{font:FONT,size:24,color:'000000'},paragraph:{alignment:AlignmentType.JUSTIFIED,spacing:{after:136,line:360,lineRule:LineRuleType.EXACT},indent:{firstLine:709}}},heading1:{run:{font:FONT,size:32,bold:true,color:BLUE},paragraph:{keepNext:true,alignment:AlignmentType.LEFT,spacing:{before:420,after:180,line:400,lineRule:LineRuleType.EXACT},indent:{left:200,firstLine:0},border:{left:{style:BorderStyle.SINGLE,size:36,color:ORANGE,space:10}}}},heading2:{run:{font:FONT,size:26,bold:true,color:BLUE},paragraph:{keepNext:true,alignment:AlignmentType.LEFT,spacing:{before:300,after:120,line:340,lineRule:LineRuleType.EXACT},indent:{firstLine:0}}}},
  paragraphStyles:[
   {id:'TOC1',name:'toc 1',basedOn:'Normal',next:'Normal',run:{font:FONT,size:22,bold:true},paragraph:{border:{top:{style:BorderStyle.NONE,size:0,color:'FFFFFF'},bottom:{style:BorderStyle.NONE,size:0,color:'FFFFFF'},left:{style:BorderStyle.NONE,size:0,color:'FFFFFF'},right:{style:BorderStyle.NONE,size:0,color:'FFFFFF'}},alignment:AlignmentType.LEFT,spacing:{before:90,after:30,line:300,lineRule:LineRuleType.EXACT},indent:{firstLine:0,left:0},tabStops:[{type:TabStopType.LEFT,position:340},{type:TabStopType.RIGHT,position:TW,leader:LeaderType.DOT}]}},
   {id:'TOC2',name:'toc 2',basedOn:'Normal',next:'Normal',run:{font:FONT,size:20},paragraph:{border:{top:{style:BorderStyle.NONE,size:0,color:'FFFFFF'},bottom:{style:BorderStyle.NONE,size:0,color:'FFFFFF'},left:{style:BorderStyle.NONE,size:0,color:'FFFFFF'},right:{style:BorderStyle.NONE,size:0,color:'FFFFFF'}},alignment:AlignmentType.LEFT,spacing:{before:20,after:20,line:300,lineRule:LineRuleType.EXACT},indent:{firstLine:0,left:240},tabStops:[{type:TabStopType.LEFT,position:700},{type:TabStopType.RIGHT,position:TW,leader:LeaderType.DOT}]}}]},
 numbering:{config:[{reference:'bul',levels:[{level:0,format:LevelFormat.BULLET,text:'•',alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:720,hanging:360}},run:{color:BLUE}}}]},{reference:'dec',levels:[{level:0,format:LevelFormat.DECIMAL,text:'%1.',alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:720,hanging:360}},run:{color:BLUE,bold:true}}}]}]},
 sections:[
  {properties:{...props({top:0,bottom:0,left:0,right:0}),type:SectionType.NEXT_PAGE},headers:{default:emptyH()},footers:{default:emptyF()},children:[fullPage('capa.png')]},
  {properties:{...props({top:1500,bottom:1077,left:1417,right:1417}),type:SectionType.NEXT_PAGE},headers:{default:emptyH()},footers:{default:emptyF()},children:exp},
  {properties:{page:{size:A4,margin:{top:2098,bottom:1077,left:1417,right:1417,header:560,footer:480},pageNumbers:{start:1,formatType:NumberFormat.DECIMAL}},type:SectionType.NEXT_PAGE},headers:{default:hdr},footers:{default:ftr},children:[...sumP,...body]},
  {properties:{...props({top:0,bottom:0,left:0,right:0}),type:SectionType.NEXT_PAGE},headers:{default:emptyH()},footers:{default:emptyF()},children:[fullPage('contracapa.png')]}
 ]});
Packer.toBuffer(doc).then(b=>{fs.writeFileSync('bruto.docx',b);console.log('ok',b.length)});
