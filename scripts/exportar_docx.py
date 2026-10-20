#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
exportar_docx.py, converte o documento.html final da PGE-MS em .docx editável.

    python scripts/dpge.py docx <documento.html> [--saida X.docx] [--modo sobrio|completo]

O build chama este módulo depois de gerar o PDF (desligue com --sem-docx). O .docx
sai em A4, com as mesmas margens do PDF, Source Sans 3, corpo preto de 12 pt,
entrelinha 1,5, texto justificado com recuo de 1,25 cm só no texto corrido,
títulos nos estilos Título 1, 2 e 3 do Word (painel de navegação), listas e
tabelas reais, caixas como tabelas de uma célula, cabeçalho com logo, rodapé
com paginação, capa, expediente, corpo e contracapa em seções próprias e
sumário como campo TOC do Word.

O que o Word não reproduz igual ao PDF é degradado para algo legível e listado
no fim da execução como aviso; nada é descartado em silêncio.

Biblioteca: python-docx (requirements.txt). O HTML é lido com BeautifulSoup,
a mesma biblioteca do converter.py.
"""

import argparse
import base64
import io
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup, Comment, NavigableString, Tag
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Mm, Pt, RGBColor
from docx.table import _Cell
from docx.text.run import Run

RAIZ = Path(__file__).resolve().parent.parent
DESIGN = RAIZ / "assets" / "design-system"
LOGO_AZUL = DESIGN / "logo-pge.png"
LOGO_BRANCO = DESIGN / "logo-pge-branco.png"

FAMILIA = "Source Sans 3"

# Margens do PDF (build.MARGENS): topo 37, pé 19, laterais 25 mm. Largura útil 160 mm.
MARGEM_CORPO = dict(top=37, bottom=19, left=25, right=25)
LARGURA_UTIL = 160.0

# Cores do tokens.css que o documento usa.
MARINHO = "294964"
MARINHO_ESCURO = "223141"
LARANJA = "F58634"
LARANJA_ESCURO = "C16C2F"
AGUA = "51A8B1"
CINZA_01 = "FAFAFA"
CINZA_02 = "F1F1F2"
CINZA_04 = "DCDDDF"
CINZA_05 = "D2D3D5"
CINZA_TEXTO = "5A6673"
DESTAQUE_FUNDO = "FFF9F2"
BRANCO = "FFFFFF"

TWIP_MM = 56.6929  # twips por milímetro


# ---------------------------------------------------------------------------
# Tema e avisos
# ---------------------------------------------------------------------------

@dataclass
class Tema:
    """Valores que o build pode alterar (--corpo, --entrelinha, --paleta...)."""
    corpo: float = 12.0
    entrelinha: float = 1.5
    espaco_paragrafo: float = 2.4  # mm
    texto: str = "000000"
    marinho: str = MARINHO
    acento: str = MARINHO
    acento_claro: str = "8FA9BC"
    acento_fundo: str = "F4F7FA"

    @property
    def k(self) -> float:
        return self.corpo / 12.0

    def pt(self, valor: float) -> float:
        return round(valor * self.k, 2)


def tema_da_paleta(nome: Optional[str], **extra) -> Tema:
    """Monta o Tema a partir de uma paleta do build.py."""
    tema = Tema(**{k: v for k, v in extra.items() if v is not None})
    if nome:
        from build import PALETAS  # import tardio: build importa este módulo
        p = PALETAS[nome]
        tema.acento = p["acento"].lstrip("#").upper()
        tema.acento_claro = p["acento_claro"].lstrip("#").upper()
        tema.acento_fundo = p["acento_fundo"].lstrip("#").upper()
    return tema


class Avisos:
    """Lista de degradações, sem repetição, na ordem em que apareceram."""

    def __init__(self):
        self._itens = {}

    def add(self, texto: str) -> None:
        self._itens[texto] = self._itens.get(texto, 0) + 1

    def linhas(self) -> list:
        return [t if n == 1 else f"{t} ({n} ocorrências)" for t, n in self._itens.items()]


# ---------------------------------------------------------------------------
# XML de baixo nível
# ---------------------------------------------------------------------------

ORDEM = {
    "tcPr": ["cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap",
             "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark"],
    "pPr": ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl",
            "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens",
            "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE",
            "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind",
            "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection",
            "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr",
            "sectPr", "pPrChange"],
    "rPr": ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike",
            "dstrike", "outline", "shadow", "emboss", "imprint", "noProof", "snapToGrid",
            "vanish", "webHidden", "color", "spacing", "w", "kern", "position", "sz", "szCs",
            "highlight", "u", "effect", "bdr", "shd", "fitText", "vertAlign", "rtl", "cs",
            "em", "lang", "eastAsianLayout", "specVanish", "oMath"],
    "tblPr": ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
              "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders",
              "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption", "tblDescription"],
}


def colocar(pr, novo) -> None:
    """Insere `novo` em `pr` na posição que o esquema do Word exige."""
    tipo = pr.tag.split("}")[1]
    ordem = ORDEM[tipo]
    nome = novo.tag.split("}")[1]
    for existente in pr.findall(novo.tag):
        pr.remove(existente)
    idx = ordem.index(nome) if nome in ordem else len(ordem)
    for filho in list(pr):
        n = filho.tag.split("}")[1]
        if n in ordem and ordem.index(n) > idx:
            filho.addprevious(novo)
            return
    pr.append(novo)


def _el(nome, **attrs):
    e = OxmlElement(nome)
    for k, v in attrs.items():
        e.set(qn("w:" + k), str(v))
    return e


def fundo(pr, cor: str) -> None:
    colocar(pr, _el("w:shd", val="clear", color="auto", fill=cor))


def _ppr(par):
    return par._p.get_or_add_pPr()


def borda_paragrafo(par, lado: str, cor: str, sz: int, espaco: int = 4) -> None:
    """Borda de parágrafo. `sz` em oitavos de ponto; `espaco` em pontos."""
    ppr = _ppr(par)
    bdr = ppr.find(qn("w:pBdr"))
    if bdr is None:
        bdr = _el("w:pBdr")
        colocar(ppr, bdr)
    for velho in bdr.findall(qn("w:" + lado)):
        bdr.remove(velho)
    novo = _el("w:" + lado, val="single", sz=sz, space=espaco, color=cor)
    ordem = ["top", "left", "bottom", "right", "between", "bar"]
    for filho in list(bdr):
        if ordem.index(filho.tag.split("}")[1]) > ordem.index(lado):
            filho.addprevious(novo)
            return
    bdr.append(novo)


def _bordas(pai_tag, pr, ordem, lados: dict) -> None:
    cont = pr.find(qn(pai_tag))
    if cont is None:
        cont = _el(pai_tag)
        colocar(pr, cont)
    for lado in ordem:
        if lado in lados:
            val = lados[lado]
            for velho in cont.findall(qn("w:" + lado)):
                cont.remove(velho)
            if val is None:
                cont.append(_el("w:" + lado, val="nil"))
            else:
                sz, cor = val
                cont.append(_el("w:" + lado, val="single", sz=sz, space=0, color=cor))


def bordas_celula(cell, **lados) -> None:
    """lados: top, left, bottom, right = (sz, cor) ou None (sem borda)."""
    tcpr = cell._tc.get_or_add_tcPr()
    # ordem do esquema: top, left, bottom, right
    _bordas("w:tcBorders", tcpr, ["top", "left", "bottom", "right"], lados)


def bordas_tabela(tabela, **lados) -> None:
    tblpr = tabela._tbl.tblPr
    _bordas("w:tblBorders", tblpr, ["top", "left", "bottom", "right", "insideH", "insideV"], lados)


def margens_celula(cell, topo=0.0, esq=0.0, base=0.0, dir=0.0) -> None:
    tcpr = cell._tc.get_or_add_tcPr()
    mar = _el("w:tcMar")
    for lado, mm in (("top", topo), ("left", esq), ("bottom", base), ("right", dir)):
        mar.append(_el("w:" + lado, w=int(mm * TWIP_MM), type="dxa"))
    colocar(tcpr, mar)


def margens_tabela(tabela, topo, esq, base, dir) -> None:
    tblpr = tabela._tbl.tblPr
    mar = _el("w:tblCellMar")
    for lado, mm in (("top", topo), ("left", esq), ("bottom", base), ("right", dir)):
        mar.append(_el("w:" + lado, w=int(mm * TWIP_MM), type="dxa"))
    colocar(tblpr, mar)


def fixar_tabela(tabela, larguras_mm: list) -> None:
    """Largura fixa por coluna, na tabela, na grade e em cada célula."""
    tblpr = tabela._tbl.tblPr
    colocar(tblpr, _el("w:tblLayout", type="fixed"))
    colocar(tblpr, _el("w:tblW", w=int(sum(larguras_mm) * TWIP_MM), type="dxa"))
    colocar(tblpr, _el("w:tblInd", w=0, type="dxa"))
    for i, largura in enumerate(larguras_mm):
        tabela.columns[i].width = Mm(largura)
    for tr in tabela._tbl.tr_lst:
        pos = 0
        for tc in tr.tc_lst:
            span = tc.grid_span
            tc.width = Mm(sum(larguras_mm[pos:pos + span]))
            pos += span


def linha_nao_parte(row) -> None:
    trpr = row._tr.get_or_add_trPr()
    trpr.append(_el("w:cantSplit"))


def linha_cabecalho(row) -> None:
    trpr = row._tr.get_or_add_trPr()
    trpr.append(_el("w:tblHeader"))


def campo(par, instrucao: str, cache: str, fmt: Optional[dict] = None) -> None:
    """Campo complexo do Word (PAGE, SECTIONPAGES...), com resultado em cache."""
    def run_com(*filhos):
        r = par.add_run()
        for f in filhos:
            r._r.append(f)
        _aplicar_fmt(r, fmt or {})
        return r
    run_com(_el("w:fldChar", fldCharType="begin"))
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = f" {instrucao} "
    run_com(instr)
    run_com(_el("w:fldChar", fldCharType="separate"))
    r = par.add_run(cache)
    _aplicar_fmt(r, fmt or {})
    run_com(_el("w:fldChar", fldCharType="end"))


def _aplicar_fmt(run, fmt: dict) -> None:
    f = run.font
    if fmt.get("b"):
        f.bold = True
    if fmt.get("i"):
        f.italic = True
    if fmt.get("u"):
        f.underline = True
    if fmt.get("tam"):
        f.size = Pt(fmt["tam"])
    if fmt.get("cor"):
        f.color.rgb = RGBColor.from_string(fmt["cor"])
    if fmt.get("caps"):
        f.all_caps = True
    if fmt.get("sup"):
        f.superscript = True
    if fmt.get("sub"):
        f.subscript = True
    rpr = run._r.get_or_add_rPr()
    if fmt.get("esp"):
        colocar(rpr, _el("w:spacing", val=int(fmt["esp"])))
    if fmt.get("fundo"):
        fundo(rpr, fmt["fundo"])


def tiny(par) -> None:
    """Parágrafo de 1 pt, usado onde o Word exige um parágrafo depois da tabela."""
    pf = par.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(1)
    pf.first_line_indent = 0
    ppr = _ppr(par)
    rpr = ppr.find(qn("w:rPr"))
    if rpr is None:
        rpr = _el("w:rPr")
        colocar(ppr, rpr)
    colocar(rpr, _el("w:sz", val=2))
    colocar(rpr, _el("w:szCs", val=2))


# ---------------------------------------------------------------------------
# Imagens
# ---------------------------------------------------------------------------

def carregar_imagem(src: str, base: Path, avisos: Avisos) -> Optional[bytes]:
    """Bytes de uma imagem do HTML (PNG, JPEG, GIF, BMP; SVG e WebP viram PNG)."""
    from PIL import Image
    if src.startswith("data:"):
        try:
            dados = base64.b64decode(src.split(",", 1)[1])
        except Exception:
            avisos.add("imagem embutida (data:) ilegível; não entrou no Word")
            return None
        nome = "imagem embutida"
    else:
        limpo = src.split("?")[0].split("#")[0]
        limpo = re.sub(r"^(?:\.\./)*(?:@ds|design-system)/", "", limpo) if re.match(
            r"^(?:\.\./)*(?:@ds|design-system)/", limpo) else limpo
        if re.match(r"^(?:\.\./)*(?:@ds|design-system)/", src.split("?")[0]):
            caminho = DESIGN / limpo
        else:
            caminho = (base / limpo).resolve()
        if not caminho.is_file():
            avisos.add(f"imagem não encontrada: {src}")
            return None
        dados = caminho.read_bytes()
        nome = caminho.name
        if caminho.suffix.lower() == ".svg":
            return svg_para_png(dados, avisos, nome)
    try:
        im = Image.open(io.BytesIO(dados))
        if im.format in ("PNG", "JPEG", "GIF", "BMP", "TIFF"):
            return dados
        saida = io.BytesIO()
        im.convert("RGBA").save(saida, "PNG")
        return saida.getvalue()
    except Exception:
        avisos.add(f"formato de imagem não suportado ({nome}); não entrou no Word")
        return None


def svg_para_png(dados: bytes, avisos: Avisos, nome: str = "svg", largura_px: int = 1654) -> Optional[bytes]:
    """Rasteriza um SVG com o PyMuPDF (já instalado para o build)."""
    try:
        import pymupdf as fitz
        doc = fitz.open(stream=dados, filetype="svg")
        pagina = doc[0]
        escala = largura_px / pagina.rect.width
        pix = pagina.get_pixmap(matrix=fitz.Matrix(escala, escala), alpha=True)
        png = pix.tobytes("png")
        doc.close()
        return png
    except Exception as e:
        avisos.add(f"SVG {nome} não pôde ser convertido em imagem ({e}); ficou de fora")
        return None


def dimensoes_mm(png: bytes) -> tuple:
    from PIL import Image
    im = Image.open(io.BytesIO(png))
    dpi = im.info.get("dpi", (96, 96))[0] or 96
    return im.width * 25.4 / dpi, im.height * 25.4 / dpi


def inserir_imagem(par, dados: bytes, largura_mm: Optional[float] = None,
                   altura_mm: Optional[float] = None, maximo_mm: float = LARGURA_UTIL,
                   alt: Optional[str] = None):
    """Imagem em linha, com texto alternativo. Devolve o objeto InlineShape."""
    nat_l, nat_a = dimensoes_mm(dados)
    if largura_mm is None and altura_mm is not None:
        largura_mm = nat_l * altura_mm / nat_a
    if largura_mm is None:
        largura_mm = min(nat_l, maximo_mm)
    largura_mm = min(largura_mm, maximo_mm)
    forma = par.add_run().add_picture(io.BytesIO(dados), width=Mm(largura_mm))
    doc_pr = forma._inline.docPr
    doc_pr.set("descr", alt or "")
    if alt:
        doc_pr.set("title", alt[:60])
    return forma


def fixar_ao_fundo(forma) -> None:
    """Converte a imagem em linha em imagem solta atrás do texto, ancorada na página."""
    inline = forma._inline
    cx, cy = inline.extent.cx, inline.extent.cy
    ns = ('xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
          'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"')
    ancora = parse_xml(
        f'<wp:anchor {ns} distT="0" distB="0" distL="0" distR="0" simplePos="0" '
        'relativeHeight="0" behindDoc="1" locked="1" layoutInCell="0" allowOverlap="1">'
        '<wp:simplePos x="0" y="0"/>'
        '<wp:positionH relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionH>'
        '<wp:positionV relativeFrom="page"><wp:posOffset>0</wp:posOffset></wp:positionV>'
        f'<wp:extent cx="{cx}" cy="{cy}"/>'
        '<wp:effectExtent l="0" t="0" r="0" b="0"/><wp:wrapNone/></wp:anchor>')
    ancora.append(inline.docPr)
    quadro = inline.find(qn("wp:cNvGraphicFramePr"))
    ancora.append(quadro if quadro is not None else parse_xml(f'<wp:cNvGraphicFramePr {ns}/>'))
    ancora.append(inline.graphic)
    inline.getparent().replace(inline, ancora)


# ---------------------------------------------------------------------------
# Texto corrido: runs a partir do HTML
# ---------------------------------------------------------------------------

RX_ESPACO = re.compile(r"[ \t\r\n\f]+")


class Texto:
    """Escreve num parágrafo juntando os espaços como o navegador faz."""

    def __init__(self, par, base: Optional[dict] = None):
        self.par = par
        self.base = dict(base or {})
        self.espaco = True  # início de linha: espaço inicial não conta
        self.ultimo = None

    def add(self, texto: str, **fmt) -> None:
        texto = RX_ESPACO.sub(" ", texto)
        if self.espaco:
            texto = texto.lstrip(" ")
        if not texto:
            return
        self.espaco = texto.endswith(" ")
        corr = dict(self.base)
        corr.update(fmt)
        run = self.par.add_run(texto)
        _aplicar_fmt(run, corr)
        self.ultimo = run

    def bruto(self, texto: str, **fmt) -> None:
        """Texto que não entra na regra de espaços (marcadores, símbolos)."""
        corr = dict(self.base)
        corr.update(fmt)
        run = self.par.add_run(texto)
        _aplicar_fmt(run, corr)
        self.ultimo = run
        self.espaco = False

    def quebra(self) -> None:
        self.par.add_run().add_break()
        self.espaco = True

    def fechar(self) -> None:
        if self.ultimo is not None and self.ultimo.text.endswith(" "):
            self.ultimo.text = self.ultimo.text.rstrip(" ")


def classes(el) -> list:
    if not isinstance(el, Tag):
        return []
    c = el.get("class") or []
    return c if isinstance(c, list) else str(c).split()


def tem(el, nome: str) -> bool:
    return nome in classes(el)


INLINE = {"span", "strong", "b", "em", "i", "u", "a", "br", "sup", "sub", "code", "small",
          "mark", "cite", "abbr", "img", "s", "del", "ins", "kbd", "q", "time", "svg"}


@dataclass
class Ctx:
    """Formatação herdada pelos parágrafos de uma caixa ou célula."""
    tam: Optional[float] = None
    linha: Optional[float] = None
    alinhar: Optional[str] = None  # left, justify, center, right
    cor: Optional[str] = None
    negrito: bool = False
    depois_mm: Optional[float] = None
    largura: float = LARGURA_UTIL  # largura disponível em mm
    prefixo: Optional[tuple] = None  # (texto, fmt) escrito no próximo parágrafo
    sem_recuo: bool = True

    def copia(self, **mud):
        d = dict(self.__dict__)
        d.update(mud)
        return Ctx(**d)


CTX_DOC = Ctx(sem_recuo=False)


# ---------------------------------------------------------------------------
# Conversor
# ---------------------------------------------------------------------------

class Conversor:
    def __init__(self, html_path: Path, modo: str, tema: Tema, avisos: Avisos):
        self.html_path = html_path
        self.base = html_path.parent
        self.modo = modo
        self.t = tema
        self.avisos = avisos
        texto = html_path.read_text(encoding="utf-8")
        self.sopa = BeautifulSoup(texto, "html.parser")
        self.doc = Document()
        self.frescas = set()       # células cujo primeiro parágrafo ainda está vazio
        self.secao_tipo = None
        self.n_secoes = 0
        self.primeiro_da_secao = True
        self.quebra_pendente = False
        self.espaco_apos_tabela = False
        self.num_abstratos = {}
        self.unidade = self.meta("vl-unidade")
        self.processo = self.meta("vl-processo")
        self.rotulo_rodape = self.meta("vl-rodape-rotulo", "Documento n.")
        self.peca = self.meta("vl-peca", "Documento institucional")
        self.orgao = self.meta("vl-orgao", "Procuradoria-Geral do Estado de Mato Grosso do Sul")
        titulo = self.meta("vl-titulo") or (self.sopa.title.get_text() if self.sopa.title else "")
        self.titulo = RX_ESPACO.sub(" ", titulo.replace("\xa0", " ")).strip() or self.html_path.stem
        self.preparar_estilos()
        self.preparar_numeracao()

    # --- leitura ----------------------------------------------------------

    def meta(self, nome: str, padrao: str = "") -> str:
        m = self.sopa.find("meta", attrs={"name": nome})
        return (m.get("content") or "").strip() if m else padrao

    def visivel(self, el: Tag) -> bool:
        c = classes(el)
        if "so-completo" in c and self.modo != "completo":
            return False
        if "so-sobrio" in c and self.modo == "completo":
            return False
        estilo = (el.get("style") or "").replace(" ", "").lower()
        if "display:none" in estilo or el.has_attr("hidden"):
            return False
        return True

    # --- estilos ----------------------------------------------------------

    def preparar_estilos(self) -> None:
        t = self.t
        est = self.doc.styles

        # docDefaults: fonte, idioma
        padrao = est.element.find(qn("w:docDefaults"))
        if padrao is not None:
            rpr = padrao.find(qn("w:rPrDefault")).find(qn("w:rPr"))
            self._rfonts(rpr)
            colocar(rpr, _el("w:lang", val="pt-BR", eastAsia="pt-BR", bidi="ar-SA"))

        def estilo(nome, base="Normal", tipo=WD_STYLE_TYPE.PARAGRAPH):
            try:
                s = est[nome]
            except KeyError:
                s = est.add_style(nome, tipo)
                if base and tipo == WD_STYLE_TYPE.PARAGRAPH:
                    s.base_style = est[base]
            return s

        def fonte(s, tam=None, b=None, i=None, cor=None, caps=None):
            self._rfonts(s.element.get_or_add_rPr())
            s.font.name = FAMILIA
            if tam:
                s.font.size = Pt(tam)
            if b is not None:
                s.font.bold = b
            if i is not None:
                s.font.italic = i
            if cor:
                s.font.color.rgb = RGBColor.from_string(cor)
            if caps:
                s.font.all_caps = True

        pt = t.pt
        normal = est["Normal"]
        fonte(normal, pt(12), b=False, cor=t.texto)
        pf = normal.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf.line_spacing = t.entrelinha
        pf.space_before = Pt(0)
        pf.space_after = Mm(t.espaco_paragrafo)
        pf.widow_control = True
        pf.first_line_indent = Mm(0)

        corpo = estilo("Body Text")
        fonte(corpo, pt(12), cor=t.texto)
        corpo.paragraph_format.first_line_indent = Mm(12.5)
        corpo.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        # Títulos: azul da marca, negrito, alinhados à esquerda
        h1 = est["Heading 1"]
        fonte(h1, pt(16), b=True, i=False, cor=t.marinho)
        f = h1.paragraph_format
        f.alignment = WD_ALIGN_PARAGRAPH.LEFT
        f.space_before = Mm(10)
        f.space_after = Mm(5)
        f.line_spacing = 1.25
        f.keep_with_next = True
        f.keep_together = True
        f.left_indent = Pt(17)
        f.first_line_indent = Mm(0)
        ppr = h1.element.get_or_add_pPr()
        bdr = _el("w:pBdr")
        bdr.append(_el("w:left", val="single", sz=40, space=12, color=LARANJA))
        colocar(ppr, bdr)

        h2 = est["Heading 2"]
        fonte(h2, pt(13), b=True, i=False, cor=t.marinho)
        f = h2.paragraph_format
        f.alignment = WD_ALIGN_PARAGRAPH.LEFT
        f.space_before = Mm(5)
        f.space_after = Mm(2.4)
        f.line_spacing = 1.25
        f.keep_with_next = True
        f.first_line_indent = Mm(0)

        h3 = est["Heading 3"]
        fonte(h3, pt(12), b=True, i=False, cor=t.marinho)
        f = h3.paragraph_format
        f.alignment = WD_ALIGN_PARAGRAPH.LEFT
        f.space_before = Mm(4)
        f.space_after = Mm(2)
        f.line_spacing = 1.25
        f.keep_with_next = True
        f.first_line_indent = Mm(0)

        titulo = est["Title"]
        fonte(titulo, pt(24), b=True, cor=t.marinho)
        f = titulo.paragraph_format
        f.alignment = WD_ALIGN_PARAGRAPH.LEFT
        f.space_before = Mm(0)
        f.space_after = Mm(3)
        f.line_spacing = 1.15
        # o estilo Title do modelo traz borda inferior; o design system não
        ppr = titulo.element.get_or_add_pPr()
        for b in ppr.findall(qn("w:pBdr")):
            ppr.remove(b)

        # Título do sumário: azul, entre dois filetes azuis (não entra no TOC)
        sumt = estilo("TOC Heading")
        fonte(sumt, pt(17), b=True, cor=t.marinho)
        f = sumt.paragraph_format
        f.alignment = WD_ALIGN_PARAGRAPH.LEFT
        f.space_before = Mm(0)
        f.space_after = Mm(6)
        f.line_spacing = 1.2
        f.keep_with_next = True
        f.first_line_indent = Mm(0)
        sumt.base_style = est["Normal"]
        f.left_indent = Mm(0)
        ppr = sumt.element.get_or_add_pPr()
        for b in ppr.findall(qn("w:outlineLvl")):
            ppr.remove(b)
        bdr = _el("w:pBdr")
        bdr.append(_el("w:top", val="single", sz=8, space=6, color=t.marinho))
        bdr.append(_el("w:bottom", val="single", sz=8, space=6, color=t.marinho))
        colocar(ppr, bdr)

        for nome, tam, negrito, recuo in (("toc 1", 11, True, 0), ("toc 2", 10, False, 4),
                                          ("toc 3", 10, False, 8)):
            s = estilo(nome)
            fonte(s, pt(tam), b=negrito, cor=t.texto)
            f = s.paragraph_format
            f.alignment = WD_ALIGN_PARAGRAPH.LEFT
            f.line_spacing = 1.35
            f.space_before = Mm(2 if nome == "toc 1" else 1)
            f.space_after = Mm(0)
            f.left_indent = Mm(recuo)
            f.first_line_indent = Mm(0)
            f.tab_stops.add_tab_stop(Mm(LARGURA_UTIL), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)

        legenda = est["Caption"]
        fonte(legenda, pt(10), b=True, i=False, cor=t.marinho)
        f = legenda.paragraph_format
        f.alignment = WD_ALIGN_PARAGRAPH.LEFT
        f.space_before = Mm(3)
        f.space_after = Mm(1.8)
        f.line_spacing = 1.2
        f.keep_with_next = True
        f.first_line_indent = Mm(0)

        lista = estilo("List Paragraph")
        fonte(lista, pt(12), cor=t.texto)
        f = lista.paragraph_format
        f.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        f.space_after = Mm(1.4)
        f.first_line_indent = Mm(0)
        for c in lista.element.get_or_add_pPr().findall(qn("w:contextualSpacing")):
            c.getparent().remove(c)

        for nome in ("Header", "Footer"):
            s = est[nome]
            fonte(s, pt(8), cor=MARINHO)
            f = s.paragraph_format
            f.alignment = WD_ALIGN_PARAGRAPH.LEFT
            f.line_spacing = 1.0
            f.space_after = Mm(0)
            f.first_line_indent = Mm(0)
            ppr = s.element.get_or_add_pPr()
            for tabs in ppr.findall(qn("w:tabs")):
                ppr.remove(tabs)

        # Hiperlink do Word
        try:
            est["Hyperlink"]
        except KeyError:
            h = est.add_style("Hyperlink", WD_STYLE_TYPE.CHARACTER)
            h.font.color.rgb = RGBColor.from_string(t.marinho)
            h.font.underline = True

    @staticmethod
    def _rfonts(rpr) -> None:
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = _el("w:rFonts")
            colocar(rpr, rf)
        for attr in list(rf.attrib):
            if "Theme" in attr:
                del rf.attrib[attr]
        for a in ("ascii", "hAnsi", "cs", "eastAsia"):
            rf.set(qn("w:" + a), FAMILIA)

    # --- listas -----------------------------------------------------------

    def preparar_numeracao(self) -> None:
        numeracao = self.doc.part.numbering_part.element
        existentes = [int(a.get(qn("w:abstractNumId"))) for a in numeracao.findall(qn("w:abstractNum"))]
        proximo = max(existentes + [0]) + 1
        self._proximo_num = max([int(n.get(qn("w:numId"))) for n in numeracao.findall(qn("w:num"))] + [0]) + 1

        def niveis(tipo):
            xml = []
            for i in range(3):
                esq = 6 + 6 * i
                if tipo == "bullet":
                    fmt, texto = "bullet", ["•", "–", "•"][i]
                else:
                    fmt = ["decimal", "lowerLetter", "lowerRoman"][i]
                    texto = ["%1.", "%2)", "%3."][i]
                xml.append(
                    f'<w:lvl w:ilvl="{i}"><w:start w:val="1"/><w:numFmt w:val="{fmt}"/>'
                    f'<w:lvlText w:val="{texto}"/><w:lvlJc w:val="left"/>'
                    f'<w:pPr><w:ind w:left="{int(esq * TWIP_MM)}" w:hanging="{int(5 * TWIP_MM)}"/></w:pPr>'
                    f'<w:rPr><w:rFonts w:ascii="{FAMILIA}" w:hAnsi="{FAMILIA}" w:cs="{FAMILIA}"/>'
                    f'<w:b w:val="{1 if (tipo != "bullet") else 0}"/>'
                    f'<w:color w:val="{self.t.acento}"/></w:rPr></w:lvl>')
            return "".join(xml)

        primeiro_num = numeracao.find(qn("w:num"))
        for tipo in ("bullet", "decimal"):
            abstrato = parse_xml(
                f'<w:abstractNum {nsdecls("w")} w:abstractNumId="{proximo}">'
                f'<w:multiLevelType w:val="hybridMultilevel"/>{niveis(tipo)}</w:abstractNum>')
            if primeiro_num is not None:
                primeiro_num.addprevious(abstrato)
            else:
                numeracao.append(abstrato)
            self.num_abstratos[tipo] = proximo
            proximo += 1

    def novo_num(self, ordenada: bool) -> int:
        numeracao = self.doc.part.numbering_part.element
        tipo = "decimal" if ordenada else "bullet"
        nid = self._proximo_num
        self._proximo_num += 1
        sobre = "".join(
            f'<w:lvlOverride w:ilvl="{i}"><w:startOverride w:val="1"/></w:lvlOverride>' for i in range(3))
        numeracao.append(parse_xml(
            f'<w:num {nsdecls("w")} w:numId="{nid}">'
            f'<w:abstractNumId w:val="{self.num_abstratos[tipo]}"/>{sobre}</w:num>'))
        return nid

    # --- seções -----------------------------------------------------------

    def entrar(self, tipo: str, margens: Optional[dict] = None) -> None:
        """Abre uma seção nova (página nova) quando o tipo muda."""
        if tipo == self.secao_tipo:
            return
        if self.n_secoes == 0:
            sec = self.doc.sections[0]
        else:
            sec = self.doc.add_section(WD_SECTION.NEW_PAGE)
            self._compactar_paragrafo_de_secao()
        self.n_secoes += 1
        self.secao_tipo = tipo
        self.primeiro_da_secao = True
        self.quebra_pendente = False
        self.espaco_apos_tabela = False
        sec.page_width, sec.page_height = Mm(210), Mm(297)
        m = margens or {"corpo": MARGEM_CORPO,
                        "expediente": dict(top=18, bottom=18, left=25, right=25),
                        "capa": dict(top=26, bottom=16, left=34, right=30),
                        "total": dict(top=0, bottom=0, left=0, right=0)}.get(
                            tipo if tipo in ("corpo", "expediente", "capa") else "total")
        sec.top_margin, sec.bottom_margin = Mm(m["top"]), Mm(m["bottom"])
        sec.left_margin, sec.right_margin = Mm(m["left"]), Mm(m["right"])
        sec.header_distance = Mm(9 if tipo == "corpo" else 0)
        sec.footer_distance = Mm(8 if tipo == "corpo" else 0)
        sectpr = sec._sectPr
        for p in sectpr.findall(qn("w:pgNumType")):
            sectpr.remove(p)
        if tipo == "corpo":
            # a paginação do rodapé começa no sumário, que é a página 1
            pg = _el("w:pgNumType", start=1)
            ref = sectpr.find(qn("w:cols"))
            if ref is not None:
                ref.addprevious(pg)
            else:
                sectpr.append(pg)
            self.montar_cabecalho_rodape(sec)
        elif tipo == "contracapa" or tipo.startswith("total"):
            for parte in (sec.header, sec.footer):
                parte.is_linked_to_previous = False
                tiny(parte.paragraphs[0])

    def _compactar_paragrafo_de_secao(self) -> None:
        """O parágrafo que carrega a quebra de seção vira uma linha de 1 pt."""
        corpo = self.doc.element.body
        for p in reversed(list(corpo.iter(qn("w:p")))):
            ppr = p.find(qn("w:pPr"))
            if ppr is not None and ppr.find(qn("w:sectPr")) is not None:
                from docx.text.paragraph import Paragraph
                tiny(Paragraph(p, self.doc._body))
                return

    def montar_cabecalho_rodape(self, sec) -> None:
        t = self.t
        sec.header.is_linked_to_previous = False
        sec.footer.is_linked_to_previous = False
        cab = sec.header.paragraphs[0]
        cab.paragraph_format.tab_stops.add_tab_stop(Mm(LARGURA_UTIL), WD_TAB_ALIGNMENT.RIGHT)
        cab.paragraph_format.space_after = Mm(0)
        inserir_imagem(cab, LOGO_AZUL.read_bytes(), altura_mm=11,
                       alt="PGE – Procuradoria-Geral do Estado de Mato Grosso do Sul")
        cab.add_run("\t")
        r = cab.add_run(self.peca)
        _aplicar_fmt(r, dict(b=True, tam=t.pt(8), cor=t.marinho, caps=True, esp=32))
        borda_paragrafo(cab, "bottom", CINZA_05, 4, 4)

        rod = sec.footer.paragraphs[0]
        rod.paragraph_format.tab_stops.add_tab_stop(Mm(LARGURA_UTIL), WD_TAB_ALIGNMENT.RIGHT)
        borda_paragrafo(rod, "top", CINZA_05, 4, 6)
        if self.processo:
            r = rod.add_run(self.rotulo_rodape.upper() + " ")
            _aplicar_fmt(r, dict(tam=t.pt(7), cor=CINZA_TEXTO, esp=16))
            r = rod.add_run(self.processo)
            _aplicar_fmt(r, dict(b=True, tam=t.pt(7), cor=t.marinho, esp=16))
        elif self.unidade:
            r = rod.add_run(self.unidade)
            _aplicar_fmt(r, dict(b=True, tam=t.pt(8), cor=t.marinho))
        rod.add_run("\t")
        peq = dict(tam=t.pt(7), cor=CINZA_TEXTO, esp=16)
        grande = dict(b=True, tam=t.pt(7), cor=t.marinho, esp=16)
        r = rod.add_run("PÁG. ")
        _aplicar_fmt(r, peq)
        campo(rod, "PAGE", "1", grande)
        r = rod.add_run(" DE ")
        _aplicar_fmt(r, peq)
        # SECTIONPAGES conta só as páginas do corpo, como o rodapé do PDF
        campo(rod, "SECTIONPAGES", "1", grande)

    # --- parágrafos -------------------------------------------------------

    def novo_par(self, alvo, estilo: Optional[str] = None, ctx: Optional[Ctx] = None):
        ctx = ctx or CTX_DOC
        if isinstance(alvo, _Cell):
            if alvo._tc in self.frescas:
                par = alvo.paragraphs[0]
                self.frescas.discard(alvo._tc)
            else:
                par = alvo.add_paragraph()
        else:
            par = alvo.add_paragraph()
            if self.quebra_pendente and not self.primeiro_da_secao:
                par.paragraph_format.page_break_before = True
            self.quebra_pendente = False
            self.primeiro_da_secao = False
            if self.espaco_apos_tabela:
                par.paragraph_format.space_before = Mm(3.5)
                self.espaco_apos_tabela = False
        if estilo:
            par.style = self.doc.styles[estilo]
        pf = par.paragraph_format
        if ctx.alinhar:
            pf.alignment = {"left": WD_ALIGN_PARAGRAPH.LEFT, "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
                            "center": WD_ALIGN_PARAGRAPH.CENTER, "right": WD_ALIGN_PARAGRAPH.RIGHT}[ctx.alinhar]
        if ctx.linha:
            pf.line_spacing = ctx.linha
        if ctx.depois_mm is not None:
            pf.space_after = Mm(ctx.depois_mm)
        return par

    def base_fmt(self, ctx: Ctx) -> dict:
        f = {}
        if ctx.tam:
            f["tam"] = ctx.tam
        if ctx.cor:
            f["cor"] = ctx.cor
        if ctx.negrito:
            f["b"] = True
        return f

    def paragrafo(self, el, alvo, ctx: Ctx, estilo: Optional[str] = None, pos=None, extra_fmt=None):
        """Escreve o conteúdo inline de `el` num parágrafo novo."""
        par = self.novo_par(alvo, estilo, ctx)
        base = self.base_fmt(ctx)
        if extra_fmt:
            base.update(extra_fmt)
        T = Texto(par, base)
        if ctx.prefixo:
            texto, fmt = ctx.prefixo
            T.bruto(texto, **fmt)
            T.bruto(" ")
            ctx.prefixo = None
        self.inline(el, T)
        T.fechar()
        if pos:
            pos(par)
        return par

    def inline(self, el, T: Texto, fmt: Optional[dict] = None) -> None:
        fmt = dict(fmt or {})
        for no in el.children:
            if isinstance(no, Comment):
                continue
            if isinstance(no, NavigableString):
                T.add(str(no), **fmt)
                continue
            if not isinstance(no, Tag) or not self.visivel(no):
                continue
            n = no.name
            c = classes(no)
            f = dict(fmt)
            if n == "br":
                T.quebra()
                continue
            if n in ("strong", "b"):
                f["b"] = True
            elif n in ("em", "i", "cite"):
                f["i"] = True
            elif n == "u":
                f["u"] = True
            elif n == "sup":
                f["sup"] = True
            elif n == "sub":
                f["sub"] = True
            elif n == "svg":
                self.avisos.add("desenho SVG dentro do texto não vai ao Word (ícone ou grafismo)")
                continue
            elif n == "img":
                self.imagem_inline(no, T)
                continue
            elif n == "a":
                self.hiperlink(no, T, f)
                continue
            if "nota-rodape" in c:
                self.avisos.add("nota de rodapé vira texto entre colchetes no ponto da chamada "
                                "(o Word exigiria o recurso de notas, que a biblioteca não grava)")
                T.add(" ")
                T.bruto("[nota: ", i=True, cor=CINZA_TEXTO)
                self.inline(no, T, dict(f, i=True, cor=CINZA_TEXTO))
                T.bruto("]", i=True, cor=CINZA_TEXTO)
                continue
            if "campo" in c:
                f["cor"] = LARANJA_ESCURO
            if "linha" in c and not no.get_text(strip=True):
                T.bruto("_" * 18, **f)
                continue
            if "caixa" in c and not no.get_text(strip=True):
                T.bruto("☐", **f)
                continue
            if "pct" in c:
                self.avisos.add("barra de percentual na tabela vira só o número")
                valor = no.select_one(".pct-valor")
                T.add(valor.get_text(strip=True) if valor else no.get_text(strip=True), **dict(f, b=True))
                continue
            self.inline(no, T, f)
            if "num" in c and n == "span":
                T.bruto(" ")

    def hiperlink(self, no, T: Texto, fmt: dict) -> None:
        href = no.get("href", "")
        if not href or href.startswith("#"):
            self.inline(no, T, fmt)
            return
        rid = T.par.part.relate_to(href, RT.HYPERLINK, is_external=True)
        h = _el("w:hyperlink", history=1)
        h.set(qn("r:id"), rid)
        T.par._p.append(h)
        texto = RX_ESPACO.sub(" ", no.get_text())
        r = _el("w:r")
        rpr = _el("w:rPr")
        rpr.append(_el("w:rStyle", val="Hyperlink"))
        r.append(rpr)
        tx = OxmlElement("w:t")
        tx.set(qn("xml:space"), "preserve")
        tx.text = texto.strip() if T.espaco else texto
        r.append(tx)
        h.append(r)
        T.espaco = texto.endswith(" ")
        T.ultimo = None

    def imagem_inline(self, no, T: Texto, maximo=None) -> None:
        dados = carregar_imagem(no.get("src", ""), self.base, self.avisos)
        if not dados:
            alt = no.get("alt")
            if alt:
                T.add(f"[imagem: {alt}]")
            return
        alt = no.get("alt")
        if alt is None:
            self.avisos.add(f"imagem sem texto alternativo ({no.get('src', '')[:40]}): "
                            "acrescente alt no HTML")
        inserir_imagem(T.par, dados, alt=alt, maximo_mm=maximo or LARGURA_UTIL)
        T.espaco = False

    # --- blocos -----------------------------------------------------------

    def grupos(self, el):
        """Divide os filhos em blocos e trechos inline contíguos."""
        trecho = []
        for no in el.children:
            if isinstance(no, Comment):
                continue
            eh_inline = isinstance(no, NavigableString) or (
                isinstance(no, Tag) and no.name in INLINE and not _tem_bloco(no))
            if isinstance(no, Tag) and not self.visivel(no):
                continue
            if eh_inline:
                trecho.append(no)
                continue
            if trecho:
                yield ("inline", trecho)
                trecho = []
            if isinstance(no, Tag):
                yield ("bloco", no)
        if trecho:
            yield ("inline", trecho)

    def trecho(self, nos, alvo, ctx: Ctx, corrido: bool) -> None:
        if not any((isinstance(n, Tag) and (n.name in ("img",) or n.get_text(strip=True)))
                   or (isinstance(n, NavigableString) and str(n).strip()) for n in nos):
            return
        falso = BeautifulSoup("<p></p>", "html.parser").p
        for n in nos:
            falso.append(n.extract() if hasattr(n, "extract") else n)
        estilo = "Body Text" if (corrido and not ctx.sem_recuo) else None
        self.paragrafo(falso, alvo, ctx, estilo)

    def blocos(self, el, alvo, ctx: Ctx, corrido: bool = False) -> None:
        for tipo, item in list(self.grupos(el)):
            if tipo == "inline":
                self.trecho(item, alvo, ctx, corrido)
            else:
                self.bloco(item, alvo, ctx, corrido)

    def corrido_em(self, el) -> bool:
        pai = el.parent
        if pai is None:
            return False
        if pai.name == "body":
            return True  # o body traz a classe do modo (modo-sobrio) e conta
        return pai.name in ("section", "article", "main") and not classes(pai)

    def bloco(self, el: Tag, alvo, ctx: Ctx, corrido: bool) -> None:
        n = el.name
        c = classes(el)
        if n in ("script", "style", "meta", "link", "title", "head", "noscript"):
            return
        if "quebra-antes" in c:
            self.quebra_pendente = True

        # --- seções do documento (só no nível do corpo)
        if n == "section" and "capa-manual" in c:
            return self.capa(el)
        if n == "section" and "expediente" in c:
            return self.expediente(el)
        if n == "section" and "contracapa" in c:
            return self.contracapa(el)

        if isinstance(alvo, type(self.doc)):
            self.entrar("corpo")

        if n in ("h1", "h2", "h3", "h4", "h5", "h6"):
            return self.titulo_(el, alvo, ctx)
        if n == "p":
            return self.p(el, alvo, ctx, corrido)
        if n in ("ul", "ol"):
            return self.lista(el, alvo, ctx)
        if n == "table":
            return self.tabela(el, alvo, ctx)
        if n == "dl":
            return self.dl(el, alvo, ctx)
        if n == "figure":
            return self.figura(el, alvo, ctx)
        if n == "img":
            par = self.novo_par(alvo, None, ctx.copia(alinhar="center"))
            T = Texto(par, {})
            self.imagem_inline(el, T, maximo=ctx.largura)
            return
        if n == "hr":
            par = self.novo_par(alvo, None, ctx)
            tiny(par)
            borda_paragrafo(par, "bottom", CINZA_05, 4, 1)
            return
        if n == "blockquote":
            c2 = ctx.copia(alinhar="justify")
            par = self.paragrafo(el, alvo, c2, None, extra_fmt={"i": True})
            par.paragraph_format.left_indent = Mm(25)
            return

        # --- componentes
        for classe, fn in (("sintese", self.c_sintese), ("atencao", self.c_atencao),
                           ("exemplo", self.c_exemplo), ("nota", self.c_nota),
                           ("requisitos", self.c_requisitos), ("confronto", self.c_confronto),
                           ("modelo", self.c_modelo), ("eixo", self.c_eixo), ("acao", self.c_acao),
                           ("numeros", self.c_numeros), ("timeline", self.c_timeline),
                           ("grafico", self.c_grafico), ("assinatura", self.c_assinatura),
                           ("aprovacao", self.c_aprovacao), ("doc-abertura", self.c_abertura),
                           ("sumario", self.c_sumario)):
            if classe in c:
                return fn(el, alvo, ctx)
        rotulos = {
            "sintese-rotulo": self.r_rotulo_caixa, "doc-eyebrow": self.r_eyebrow,
            "doc-periodo": self.r_periodo, "enderecamento": self.r_enderecamento,
            "m-nome": None,
        }
        for classe, fn in rotulos.items():
            if classe in c and fn:
                return fn(el, alvo, ctx)

        # contêineres neutros: segue para os filhos
        conhecidas = {"fecho", "fecho-modelo", "doc-corpo", "pagina", "conteudo", "quebra-antes",
                      "primeira", "pode-quebrar", "nao-quebrar", "juntar", "so-completo",
                      "so-sobrio", "modo-sobrio", "modo-completo", "ex-blocos", "ex-bloco",
                      "ex-ficha", "indice-modelos"}
        desconhecidas = [x for x in c if x not in conhecidas]
        if desconhecidas and n in ("div", "section", "article", "aside", "span"):
            self.avisos.add("componente sem equivalente no Word: ."
                            + ".".join(desconhecidas) + " (o texto foi mantido, sem o visual)")
        if n in ("div", "section", "article", "main", "aside", "header", "footer", "nav",
                 "form", "fieldset", "details", "summary", "figcaption", "address", "center", "body"):
            return self.blocos(el, alvo, ctx, corrido=corrido and not c)
        # qualquer outra tag de bloco vira parágrafo
        self.paragrafo(el, alvo, ctx)

    # títulos ---------------------------------------------------------------

    def titulo_(self, el, alvo, ctx: Ctx) -> None:
        c = classes(el)
        n = el.name
        if "sumario-titulo" in c:
            self.paragrafo(el, alvo, ctx.copia(alinhar="left"), "TOC Heading")
            return
        if "doc-titulo" in c:
            self.paragrafo(el, alvo, ctx, "Title")
            return
        nivel = {"h1": 1, "h2": 1, "h3": 2}.get(n, 3)
        par = self.paragrafo(el, alvo, ctx.copia(alinhar=None, linha=None, depois_mm=None),
                             f"Heading {nivel}")
        # cabeçalhos dentro de caixa não devem arrastar a barra laranja
        if not isinstance(alvo, type(self.doc)) and nivel == 1:
            ppr = _ppr(par)
            borda_paragrafo(par, "left", LARANJA, 40, 12)

    def p(self, el, alvo, ctx: Ctx, corrido: bool) -> None:
        c = classes(el)
        if not el.get_text(strip=True) and not el.find("img"):
            return
        if "grupo" in c:
            self.paragrafo(el, alvo, ctx.copia(alinhar="left"), None,
                           extra_fmt={"b": True, "cor": self.t.marinho},
                           pos=lambda p: setattr(p.paragraph_format, "keep_with_next", True))
            return
        if "item-letra" in c:
            par = self.paragrafo(el, alvo, ctx, None)
            par.paragraph_format.left_indent = Mm(6)
            return
        if "tab-nota" in c or "fig-fonte" in c:
            self.paragrafo(el, alvo, ctx.copia(alinhar="left", tam=self.t.pt(9.6), cor=CINZA_TEXTO,
                                               linha=1.2))
            return
        if "anexo-contexto" in c:
            self.paragrafo(el, alvo, ctx.copia(alinhar="left", tam=self.t.pt(9.6), cor=CINZA_TEXTO))
            return
        if "cc-nota" in c:
            return self.paragrafo(el, alvo, ctx)
        recuo = not ctx.sem_recuo and self.corrido_em(el) and not set(c) - {"primeira"}
        self.paragrafo(el, alvo, ctx, "Body Text" if recuo else None)

    # listas ----------------------------------------------------------------

    def lista(self, el, alvo, ctx: Ctx, nivel: int = 0, num_id: Optional[int] = None) -> None:
        ordenada = el.name == "ol"
        if num_id is None:
            num_id = self.novo_num(ordenada)
        nivel = min(nivel, 2)
        itens = [li for li in el.find_all("li", recursive=False) if self.visivel(li)]
        for i, li in enumerate(itens):
            ultimo = i == len(itens) - 1
            primeiro_par = True
            for tipo, item in list(self.grupos(li)):
                if tipo == "bloco" and item.name in ("ul", "ol"):
                    mesma = (item.name == "ol") == ordenada
                    self.lista(item, alvo, ctx, nivel + 1, num_id if mesma else None)
                    continue
                if tipo == "inline":
                    if not any((isinstance(x, Tag) and (x.get_text(strip=True) or x.name == "img"))
                               or (isinstance(x, NavigableString) and str(x).strip()) for x in item):
                        continue
                    falso = BeautifulSoup("<p></p>", "html.parser").p
                    for x in item:
                        falso.append(x.extract())
                    fonte_el = falso
                else:
                    fonte_el = item
                par = self.novo_par(alvo, "List Paragraph", ctx)
                T = Texto(par, self.base_fmt(ctx))
                self.inline(fonte_el, T)
                T.fechar()
                if primeiro_par:
                    ppr = _ppr(par)
                    num = _el("w:numPr")
                    num.append(_el("w:ilvl", val=nivel))
                    num.append(_el("w:numId", val=num_id))
                    colocar(ppr, num)
                    primeiro_par = False
                else:
                    par.paragraph_format.left_indent = Mm(6 + 6 * nivel)
                if ctx.tam:
                    pass
                if ultimo and nivel == 0:
                    par.paragraph_format.space_after = Mm(ctx.depois_mm if ctx.depois_mm is not None
                                                          else self.t.espaco_paragrafo)
                if ctx.depois_mm is not None and not (ultimo and nivel == 0):
                    par.paragraph_format.space_after = Mm(min(ctx.depois_mm, 1.4))

    # tabelas ---------------------------------------------------------------

    def criar_tabela(self, alvo, linhas: int, larguras: list):
        """Tabela vazia, de largura fixa, dentro do documento ou de uma célula."""
        if isinstance(alvo, _Cell):
            if alvo._tc in self.frescas:
                p = alvo.paragraphs[0]._p
                p.getparent().remove(p)
                self.frescas.discard(alvo._tc)
            t = alvo.add_table(linhas, len(larguras))
            # o python-docx deixa um parágrafo depois da tabela: reduz
            tiny(alvo.paragraphs[-1])
        else:
            filhos = [f for f in self.doc.element.body if f.tag != qn("w:sectPr")]
            if filhos and filhos[-1].tag == qn("w:tbl"):
                # duas tabelas coladas viram uma só no Word: separa com uma linha
                sep = self.doc.add_paragraph()
                tiny(sep)
                sep.paragraph_format.line_spacing = Pt(10)
            t = alvo.add_table(rows=linhas, cols=len(larguras))
            if self.quebra_pendente and not self.primeiro_da_secao:
                # a quebra pedida vale para a primeira célula
                t.cell(0, 0).paragraphs[0].paragraph_format.page_break_before = True
            self.quebra_pendente = False
            self.primeiro_da_secao = False
            self.espaco_apos_tabela = True
        t.autofit = False
        fixar_tabela(t, larguras)
        bordas_tabela(t, top=None, left=None, bottom=None, right=None, insideH=None, insideV=None)
        for row in t.rows:
            for cell in row.cells:
                self.frescas.add(cell._tc)
        return t

    def caixa(self, alvo, ctx: Ctx, fundo_cor=None, bordas=None, margens=(2.2, 3, 2.2, 3),
              pode_quebrar=False):
        """Caixa = tabela de uma célula, com fundo e borda do PDF."""
        t = self.criar_tabela(alvo, 1, [ctx.largura])
        cell = t.cell(0, 0)
        if fundo_cor:
            fundo(cell._tc.get_or_add_tcPr(), fundo_cor)
        if bordas:
            bordas_celula(cell, **bordas)
        margens_celula(cell, *[m for m in margens])
        if not pode_quebrar:
            linha_nao_parte(t.rows[0])
        return t, cell

    def pesos(self, linhas: list, ncols: int) -> list:
        w = [4.0] * ncols
        for cels in linhas:
            col = 0
            for cel in cels:
                span = int(cel.get("colspan", 1) or 1)
                tam = len(cel.get_text(" ", strip=True))
                for j in range(col, min(col + span, ncols)):
                    w[j] = max(w[j], min(tam / span, 60))
                col += span
        return w

    def tabela(self, el, alvo, ctx: Ctx) -> None:
        c = classes(el)
        linhas = [tr for tr in el.find_all("tr") if tr.find_parent("table") is el]
        if not linhas:
            return
        celulas = [[x for x in tr.find_all(["th", "td"], recursive=False)] for tr in linhas]
        ncols = max(sum(int(x.get("colspan", 1) or 1) for x in cels) for cels in celulas)
        cap = el.find("caption")
        if cap is not None and cap.get_text(strip=True):
            self.paragrafo(cap, alvo, ctx.copia(alinhar="left", tam=None, linha=None), "Caption")
        pesos = self.pesos(celulas, ncols)
        # colunas numéricas não precisam de largura de texto longo
        total = sum(pesos)
        larguras = [max(14.0, ctx.largura * p / total) for p in pesos]
        escala = ctx.largura / sum(larguras)
        larguras = [round(l * escala, 2) for l in larguras]
        t = self.criar_tabela(alvo, len(linhas), larguras)
        margens_tabela(t, 1.6, 2.8, 1.6, 2.8)
        bordas_tabela(t, bottom=(6, CINZA_05), insideH=(4, CINZA_04))
        tem_cab = False
        ocupado = set()
        for r, (tr, cels) in enumerate(zip(linhas, celulas)):
            col = 0
            cab_linha = all(x.name == "th" for x in cels) and bool(cels) and (
                tr.find_parent("thead") is not None or r == 0)
            if cab_linha:
                linha_cabecalho(t.rows[r])
                tem_cab = True
            linha_nao_parte(t.rows[r])
            for cel in cels:
                while (r, col) in ocupado:
                    col += 1
                cs = int(cel.get("colspan", 1) or 1)
                rs = int(cel.get("rowspan", 1) or 1)
                alvo_cel = t.cell(r, col)
                if cs > 1 or rs > 1:
                    alvo_cel = alvo_cel.merge(t.cell(min(r + rs - 1, len(linhas) - 1),
                                                     min(col + cs - 1, ncols - 1)))
                for dr in range(rs):
                    for dc in range(cs):
                        ocupado.add((r + dr, col + dc))
                self.celula_de_tabela(cel, alvo_cel, r, cab_linha, tr, ctx, c)
                col += cs
        fixar_tabela(t, larguras)

    def celula_de_tabela(self, cel, destino, r, cab, tr, ctx, c_tabela) -> None:
        t = self.t
        eh_num = "num" in classes(cel)
        cx = Ctx(tam=t.pt(10.5), linha=1.15, alinhar="right" if eh_num else "left",
                 depois_mm=0.8, largura=max(20.0, ctx.largura / 3))
        if cab:
            fundo(destino._tc.get_or_add_tcPr(), t.marinho)
            cx.cor, cx.negrito, cx.tam = BRANCO, True, t.pt(9)
            self.frescas.add(destino._tc)
            par = self.novo_par(destino, None, cx)
            T = Texto(par, dict(self.base_fmt(cx), caps=True, esp=14))
            self.inline(cel, T)
            T.fechar()
            return
        classes_tr = classes(tr)
        if "total" in classes_tr:
            fundo(destino._tc.get_or_add_tcPr(), CINZA_02)
            cx.negrito = True
        elif tr.find_parent("tbody") is not None or True:
            irmaos = [x for x in tr.parent.find_all("tr", recursive=False)]
            if tr in irmaos and irmaos.index(tr) % 2 == 1:
                fundo(destino._tc.get_or_add_tcPr(), CINZA_01)
        if "destaque" in classes(cel):
            cx.negrito, cx.cor = True, LARANJA_ESCURO
        if "criterio" in classes(cel):
            cx.negrito, cx.cor = True, t.marinho
        if self.tem_blocos(cel):
            self.blocos(cel, destino, cx, corrido=False)
        else:
            par = self.novo_par(destino, None, cx)
            T = Texto(par, self.base_fmt(cx))
            self.inline(cel, T)
            T.fechar()

    @staticmethod
    def tem_blocos(el) -> bool:
        return any(isinstance(x, Tag) and x.name in ("p", "ul", "ol", "table", "div", "dl")
                   for x in el.children)

    def dl(self, el, alvo, ctx: Ctx) -> None:
        pares = []
        dt = None
        for x in el.find_all(["dt", "dd"]):
            if x.name == "dt":
                dt = x
            elif dt is not None:
                pares.append((dt, x))
                dt = None
        if not pares:
            return
        c = classes(el)
        t_ = self.t
        col1 = 42.0 if "glossario" in c else 45.0
        larguras = [col1, ctx.largura - col1]
        t = self.criar_tabela(alvo, len(pares), larguras)
        margens_tabela(t, 1.3, 1.5, 1.3, 1.5)
        if "glossario" in c:
            bordas_tabela(t, top=(4, CINZA_05), bottom=(4, CINZA_05))
        else:
            bordas_tabela(t, top=(4, CINZA_05), bottom=(4, CINZA_05), insideH=(4, CINZA_04))
        for i, (dt, dd) in enumerate(pares):
            linha_nao_parte(t.rows[i])
            cx = Ctx(tam=t_.pt(9.6), linha=1.3, alinhar="left", depois_mm=0, largura=larguras[1])
            par = self.novo_par(t.cell(i, 0), None, cx)
            T = Texto(par, dict(self.base_fmt(cx), b=True, cor=t_.marinho))
            self.inline(dt, T)
            T.fechar()
            if self.tem_blocos(dd):
                self.blocos(dd, t.cell(i, 1), cx, corrido=False)
            else:
                par = self.novo_par(t.cell(i, 1), None, cx)
                T = Texto(par, self.base_fmt(cx))
                self.inline(dd, T)
                T.fechar()

    def figura(self, el, alvo, ctx: Ctx) -> None:
        cap = el.find("figcaption")
        if cap is not None:
            par = self.paragrafo(cap, alvo, ctx.copia(alinhar="left", linha=None, depois_mm=None), "Caption")
            for r in par.runs:
                pass
            borda_paragrafo(par, "left", LARANJA, 24, 8)
            par.paragraph_format.left_indent = Mm(4)
        for img in el.find_all("img"):
            par = self.novo_par(alvo, None, ctx.copia(alinhar="center", linha=1.0, depois_mm=1.5))
            par.paragraph_format.keep_with_next = True
            T = Texto(par, {})
            self.imagem_inline(img, T, maximo=ctx.largura)
        for fonte in el.find_all("p"):
            self.p(fonte, alvo, ctx, False)

    # componentes -------------------------------------------------------

    def c_sintese(self, el, alvo, ctx: Ctx) -> None:
        pode = "pode-quebrar" in classes(el)
        t, cell = self.caixa(alvo, ctx, self.t.acento_fundo,
                             dict(top=(4, self.t.acento_claro), left=(4, self.t.acento_claro),
                                  bottom=(4, self.t.acento_claro), right=(4, self.t.acento_claro)),
                             (2.4, 3.2, 2.4, 3.2), pode)
        cx = ctx.copia(tam=self.t.pt(12), alinhar="left", linha=self.t.entrelinha,
                       depois_mm=2, largura=ctx.largura - 6.4, sem_recuo=True)
        self.blocos(el, cell, cx)
        self.fim_caixa(cell)

    def r_rotulo_caixa(self, el, alvo, ctx: Ctx) -> None:
        par = self.paragrafo(el, alvo, ctx.copia(alinhar="left", linha=1.2, depois_mm=2.4,
                                                 tam=self.t.pt(8.2), cor=self.t.acento, negrito=True),
                             None, extra_fmt={"caps": True, "esp": 20})
        par.paragraph_format.keep_with_next = True

    def fim_caixa(self, cell) -> None:
        """Tira o espaço depois do último parágrafo da caixa."""
        pars = cell.paragraphs
        if pars:
            pars[-1].paragraph_format.space_after = Mm(0)

    def c_atencao(self, el, alvo, ctx: Ctx) -> None:
        t, cell = self.caixa(alvo, ctx, DESTAQUE_FUNDO, dict(left=(27, LARANJA)),
                             (2.4, 3.5, 2.4, 3.5))
        marca = el.select_one(".atencao-marca")
        interior = [x for x in el.children if isinstance(x, Tag) and "atencao-marca" not in classes(x)]
        cx = ctx.copia(tam=self.t.pt(12), alinhar="left", linha=self.t.entrelinha, depois_mm=1.5,
                       largura=ctx.largura - 7,
                       prefixo=((" " + (marca.get_text(strip=True) if marca else "!") + " "),
                                dict(b=True, cor=BRANCO, fundo=LARANJA)))
        for filho in interior:
            self.blocos(filho, cell, cx)
        self.fim_caixa(cell)

    def c_exemplo(self, el, alvo, ctx: Ctx) -> None:
        pode = "pode-quebrar" in classes(el)
        t, cell = self.caixa(alvo, ctx, CINZA_01, dict(left=(20, CINZA_05)), (2.2, 4, 2.2, 4), pode)
        cx = ctx.copia(tam=self.t.pt(12), alinhar="left", linha=self.t.entrelinha, depois_mm=2,
                       largura=ctx.largura - 8)
        self.blocos(el, cell, cx)
        self.fim_caixa(cell)

    def c_nota(self, el, alvo, ctx: Ctx) -> None:
        t, cell = self.caixa(alvo, ctx, CINZA_02, dict(left=(18, CINZA_05)), (2, 3.5, 2, 3.5), True)
        cx = ctx.copia(tam=self.t.pt(9), cor=CINZA_TEXTO, alinhar="left", linha=1.25, depois_mm=1.6,
                       largura=ctx.largura - 7)
        self.blocos(el, cell, cx)
        self.fim_caixa(cell)

    def c_requisitos(self, el, alvo, ctx: Ctx) -> None:
        itens = [d for d in el.find_all("div", recursive=False)]
        if not itens:
            return
        meia = ctx.largura / 2
        linhas = (len(itens) + 1) // 2
        t = self.criar_tabela(alvo, linhas, [meia, meia])
        borda = (4, CINZA_05)
        bordas_tabela(t, top=borda, left=borda, bottom=borda, right=borda, insideH=borda, insideV=borda)
        for i, item in enumerate(itens):
            cell = t.cell(i // 2, i % 2)
            margens_celula(cell, 2, 3, 2, 3)
            cx = Ctx(tam=self.t.pt(10), linha=1.25, alinhar="left", depois_mm=1, largura=meia - 6)
            rot = item.select_one(".r-rotulo")
            tex = item.select_one(".r-texto")
            if rot:
                par = self.paragrafo(rot, cell, cx.copia(cor=self.t.marinho, negrito=True), None,
                                     extra_fmt={"caps": True, "esp": 10})
                par.paragraph_format.keep_with_next = True
            if tex:
                self.paragrafo(tex, cell, cx)
        for row in t.rows:
            linha_nao_parte(row)

    def c_confronto(self, el, alvo, ctx: Ctx) -> None:
        itens = [d for d in el.find_all("div", recursive=False)]
        if not itens:
            return
        larguras = [38.0, ctx.largura - 38]
        t = self.criar_tabela(alvo, len(itens), larguras)
        borda = (4, CINZA_05)
        bordas_tabela(t, top=borda, left=borda, bottom=borda, right=borda, insideH=borda, insideV=borda)
        for i, item in enumerate(itens):
            div = "divergente" in classes(item)
            linha_nao_parte(t.rows[i])
            for j, sel in enumerate((".c-rotulo", ".c-texto")):
                cell = t.cell(i, j)
                margens_celula(cell, 1.8, 3, 1.8, 3)
                if div:
                    fundo(cell._tc.get_or_add_tcPr(), DESTAQUE_FUNDO)
                cx = Ctx(tam=self.t.pt(10), linha=1.25, alinhar="left", depois_mm=0, largura=larguras[j] - 6,
                         negrito=(j == 0), cor=(LARANJA_ESCURO if (div and j == 0) else (self.t.marinho if j == 0 else None)))
                alvo_el = item.select_one(sel)
                if alvo_el is not None:
                    self.paragrafo(alvo_el, cell, cx)

    def c_modelo(self, el, alvo, ctx: Ctx) -> None:
        cab = el.select_one(".modelo-cab")
        corpo = el.select_one(".modelo-corpo")
        t = self.criar_tabela(alvo, 2, [ctx.largura])
        borda = (4, CINZA_05)
        bordas_tabela(t, top=borda, left=borda, bottom=borda, right=borda)
        c0, c1 = t.cell(0, 0), t.cell(1, 0)
        fundo(c0._tc.get_or_add_tcPr(), self.t.marinho)
        margens_celula(c0, 2, 4, 2, 4)
        margens_celula(c1, 3, 4, 3, 4)
        if cab is not None:
            cx = Ctx(tam=self.t.pt(11), cor=BRANCO, negrito=True, alinhar="left", linha=1.2, depois_mm=0)
            par = self.novo_par(c0, None, cx)
            T = Texto(par, self.base_fmt(cx))
            num = cab.select_one(".m-num")
            nome = cab.select_one(".m-nome")
            if num:
                T.bruto(" " + num.get_text(strip=True) + " ", fundo=LARANJA, cor=MARINHO_ESCURO, b=True)
                T.bruto("  ")
            if nome:
                self.inline(nome, T)
            T.fechar()
        linha_nao_parte(t.rows[0])
        par_cab = c0.paragraphs[0]
        par_cab.paragraph_format.keep_with_next = True
        if corpo is not None:
            cx = Ctx(tam=self.t.pt(11), alinhar="left", linha=1.3, depois_mm=2, largura=ctx.largura - 8)
            self.blocos(corpo, c1, cx)
            self.fim_caixa(c1)

    def c_eixo(self, el, alvo, ctx: Ctx) -> None:
        par = self.novo_par(alvo, None, ctx.copia(alinhar="left", linha=1.3, depois_mm=2))
        par.paragraph_format.space_before = Mm(7)
        par.paragraph_format.keep_with_next = True
        self.espaco_apos_tabela = False
        T = Texto(par, {})
        selo = el.select_one(".eixo-selo")
        nome = el.select_one(".eixo-nome")
        if selo:
            T.bruto(" " + selo.get_text(strip=True) + " ", b=True, cor=BRANCO, fundo=self.t.marinho,
                    tam=self.t.pt(8), caps=True, esp=14)
            T.bruto("  ")
        if nome:
            self.inline(nome, T, dict(b=True, cor=self.t.marinho, tam=self.t.pt(12.5)))
        T.fechar()

    def c_acao(self, el, alvo, ctx: Ctx) -> None:
        cab = el.select_one(".acao-cab")
        linhas = el.select(".acao-linha")
        larguras = [40.0, ctx.largura - 40]
        t = self.criar_tabela(alvo, 1 + len(linhas), larguras)
        borda = (4, CINZA_05)
        bordas_tabela(t, top=borda, left=borda, bottom=borda, right=borda, insideH=(4, CINZA_04))
        a = t.cell(0, 0).merge(t.cell(0, 1))
        fundo(a._tc.get_or_add_tcPr(), self.t.marinho)
        margens_celula(a, 2.4, 4, 2.4, 4)
        linha_nao_parte(t.rows[0])
        if cab is not None:
            cx = Ctx(tam=self.t.pt(11), cor=BRANCO, negrito=True, alinhar="left", linha=1.3, depois_mm=0)
            self.frescas.add(a._tc)
            par = self.novo_par(a, None, cx)
            par.paragraph_format.keep_with_next = True
            T = Texto(par, self.base_fmt(cx))
            num = cab.select_one(".acao-num")
            tit = cab.select_one(".acao-titulo")
            if num:
                T.bruto(" " + num.get_text(strip=True) + " ", b=True, cor=MARINHO_ESCURO, fundo=LARANJA,
                        tam=self.t.pt(7.6), caps=True, esp=12)
                T.bruto("  ")
            if tit:
                self.inline(tit, T)
            T.fechar()
        for i, linha in enumerate(linhas, start=1):
            linha_nao_parte(t.rows[i])
            c1, c2 = t.cell(i, 0), t.cell(i, 1)
            for cell in (c1, c2):
                margens_celula(cell, 2, 4, 2, 4)
                if i % 2 == 0:
                    fundo(cell._tc.get_or_add_tcPr(), CINZA_01)
            cx = Ctx(tam=self.t.pt(9.6), linha=1.3, alinhar="left", depois_mm=1.2, largura=larguras[1] - 8)
            rot = linha.select_one(".acao-rot")
            txt = linha.select_one(".acao-txt")
            if rot:
                self.paragrafo(rot, c1, cx.copia(negrito=True, cor=self.t.marinho, largura=larguras[0] - 8))
            if txt:
                self.blocos(txt, c2, cx)
            self.fim_caixa(c2)

    def c_numeros(self, el, alvo, ctx: Ctx) -> None:
        itens = [d for d in el.find_all("div", recursive=False)]
        if not itens:
            return
        w = ctx.largura / len(itens)
        t = self.criar_tabela(alvo, 1, [w] * len(itens))
        bordas_tabela(t, top=(8, self.t.acento), bottom=(4, CINZA_05), insideV=(4, CINZA_05))
        for i, item in enumerate(itens):
            cell = t.cell(0, i)
            margens_celula(cell, 2.5, 2, 2.5, 2)
            cx = Ctx(alinhar="center", linha=1.1, depois_mm=0.5, largura=w - 4)
            v = item.select_one(".n-valor")
            r = item.select_one(".n-rotulo")
            if v:
                self.paragrafo(v, cell, cx.copia(tam=self.t.pt(22), negrito=True, cor=self.t.marinho))
            if r:
                self.paragrafo(r, cell, cx.copia(tam=self.t.pt(8.5), cor=CINZA_TEXTO))
        linha_nao_parte(t.rows[0])

    def c_timeline(self, el, alvo, ctx: Ctx) -> None:
        self.avisos.add("linha do tempo vira tabela de duas colunas (sem a linha e os marcos gráficos)")
        rot = el.select_one(".timeline-rotulo")
        if rot is not None:
            self.paragrafo(rot, alvo, ctx.copia(alinhar="left"), "Caption")
        itens = el.select("li")
        if not itens:
            return
        larguras = [45.0, ctx.largura - 45]
        t = self.criar_tabela(alvo, len(itens), larguras)
        bordas_tabela(t, top=(4, CINZA_05), bottom=(4, CINZA_05), insideH=(4, CINZA_04))
        for i, li in enumerate(itens):
            linha_nao_parte(t.rows[i])
            marco = "marco" in classes(li)
            for j, sel in enumerate((".tl-titulo", ".tl-texto")):
                cell = t.cell(i, j)
                margens_celula(cell, 1.5, 2, 1.5, 2)
                e = li.select_one(sel)
                cx = Ctx(tam=self.t.pt(10.5), linha=1.2, alinhar="left", depois_mm=0,
                         negrito=(j == 0 or marco), cor=(self.t.marinho if j == 0 else None))
                if e is not None:
                    self.paragrafo(e, cell, cx)

    def c_grafico(self, el, alvo, ctx: Ctx) -> None:
        self.avisos.add("gráfico de barras vira barras de texto (caracteres) com o valor ao lado")
        tit = el.select_one(".grafico-titulo")
        if tit is not None:
            self.paragrafo(tit, alvo, ctx.copia(alinhar="left"), "Caption")
        sub = el.select_one(".grafico-sub")
        if sub is not None:
            self.paragrafo(sub, alvo, ctx.copia(alinhar="left", tam=self.t.pt(9.6), cor=CINZA_TEXTO))
        linhas = el.select(".barra-linha")
        if not linhas:
            return
        larguras = [45.0, ctx.largura - 45]
        t = self.criar_tabela(alvo, len(linhas), larguras)
        bordas_tabela(t, insideH=(4, CINZA_04), bottom=(4, CINZA_05))
        for i, lin in enumerate(linhas):
            linha_nao_parte(t.rows[i])
            rot = lin.select_one(".barra-rotulo")
            barra = lin.select_one(".barra")
            val = lin.select_one(".barra-valor")
            mm = 0.0
            if barra is not None:
                m = re.search(r"width:\s*([\d.]+)mm", barra.get("style", ""))
                mm = float(m.group(1)) if m else 0.0
            cx = Ctx(tam=self.t.pt(10), linha=1.2, alinhar="left", depois_mm=0)
            margens_celula(t.cell(i, 0), 1.2, 2, 1.2, 2)
            margens_celula(t.cell(i, 1), 1.2, 2, 1.2, 2)
            if rot:
                self.paragrafo(rot, t.cell(i, 0), cx)
            par = self.novo_par(t.cell(i, 1), None, cx)
            T = Texto(par, self.base_fmt(cx))
            T.bruto("█" * max(1, round(mm / 112 * 28)), cor=self.t.marinho)
            T.bruto("  ")
            if val:
                T.bruto(val.get_text(strip=True), b=True)

    def c_assinatura(self, el, alvo, ctx: Ctx) -> None:
        img = el.find("img")
        if img is not None:
            par = self.novo_par(alvo, None, ctx.copia(alinhar="center", linha=1.0, depois_mm=0))
            par.paragraph_format.keep_with_next = True
            par.paragraph_format.space_before = Mm(8)
            self.imagem_inline(img, Texto(par, {}), maximo=60)
        par = self.novo_par(alvo, None, ctx.copia(alinhar="center", linha=1.0, depois_mm=2))
        par.paragraph_format.keep_with_next = True
        par.paragraph_format.keep_together = True
        if img is None:
            par.paragraph_format.space_before = Mm(14)
        ppr = _ppr(par)
        par.paragraph_format.left_indent = Mm((ctx.largura - 62) / 2)
        par.paragraph_format.right_indent = Mm((ctx.largura - 62) / 2)
        borda_paragrafo(par, "top", self.t.acento, 16, 1)
        tiny(par)
        nome = el.select_one(".nome")
        cargo = el.select_one(".cargo")
        oab = el.select_one(".oab")
        if nome:
            p2 = self.paragrafo(nome, alvo, ctx.copia(alinhar="center", linha=1.2, depois_mm=1,
                                                      tam=self.t.pt(12.8), negrito=True, cor=self.t.marinho))
            p2.paragraph_format.keep_with_next = True
            p2.paragraph_format.space_before = Mm(2)
        if cargo:
            self.paragrafo(cargo, alvo, ctx.copia(alinhar="center", linha=1.3, depois_mm=1,
                                                  tam=self.t.pt(9.6), cor=self.t.marinho))
        if oab:
            self.paragrafo(oab, alvo, ctx.copia(alinhar="center", linha=1.2, depois_mm=3,
                                                tam=self.t.pt(8.2), cor=CINZA_TEXTO),
                           None, extra_fmt={"caps": True, "esp": 20})

    def c_aprovacao(self, el, alvo, ctx: Ctx) -> None:
        for filho in el.children:
            if not isinstance(filho, Tag) or not self.visivel(filho):
                continue
            if "aprovacao-titulo" in classes(filho):
                par = self.paragrafo(filho, alvo, ctx.copia(alinhar="left", negrito=True,
                                                            cor=self.t.marinho, tam=self.t.pt(13)))
                par.paragraph_format.keep_with_next = True
                par.paragraph_format.space_before = Mm(10)
            else:
                self.bloco(filho, alvo, ctx, False)

    def c_abertura(self, el, alvo, ctx: Ctx) -> None:
        self.blocos(el, alvo, ctx)
        # o filete azul fecha a abertura
        corpo = self.doc.element.body
        ultimo = [p for p in corpo.findall(qn("w:p"))][-1]
        from docx.text.paragraph import Paragraph
        par = Paragraph(ultimo, self.doc._body)
        borda_paragrafo(par, "bottom", self.t.acento, 16, 6)
        par.paragraph_format.space_after = Mm(7)

    def r_eyebrow(self, el, alvo, ctx: Ctx) -> None:
        par = self.paragrafo(el, alvo, ctx.copia(alinhar="left", depois_mm=3, linha=1.2,
                                                 tam=self.t.pt(7.3), negrito=True, cor=self.t.marinho),
                             None, extra_fmt={"caps": True, "esp": 32})
        par.paragraph_format.keep_with_next = True

    def r_periodo(self, el, alvo, ctx: Ctx) -> None:
        self.paragrafo(el, alvo, ctx.copia(alinhar="left", depois_mm=1, linha=1.2,
                                           tam=self.t.pt(10.5), cor=CINZA_TEXTO))

    def r_enderecamento(self, el, alvo, ctx: Ctx) -> None:
        self.paragrafo(el, alvo, ctx.copia(alinhar="left", depois_mm=6, negrito=True))

    # sumário ---------------------------------------------------------------

    def c_sumario(self, el, alvo, ctx: Ctx) -> None:
        entradas = []
        for li in el.select("li"):
            num = li.select_one(".s-num")
            tit = li.select_one(".s-tit")
            pag = li.select_one(".s-pag")
            p = pag.get_text(strip=True) if pag else ""
            entradas.append((
                1 if "parte" in classes(li) else 2,
                (num.get_text(strip=True) if num else ""),
                RX_ESPACO.sub(" ", tit.get_text(" ", strip=True)) if tit else "",
                p if re.fullmatch(r"\d+", p) else ""))
        self.avisos.add("sumário é um campo do Word: ao abrir, responda Sim ao pedido de "
                        "atualizar os campos (ou clique no sumário e use F9) para os números "
                        "de página valerem para o Word")
        primeiro = True
        for i, (nivel, num, tit, pag) in enumerate(entradas or [(1, "", "Atualize o campo (F9) para gerar o sumário.", "")]):
            par = self.novo_par(alvo, f"toc {nivel}", ctx.copia(alinhar="left"))
            if i == 0:
                self._abrir_toc(par)
            texto = (num + " " if num else "") + tit
            r = par.add_run(texto)
            par.add_run("\t")
            if pag:
                par.add_run(pag)
            if i == max(len(entradas), 1) - 1:
                self._fechar_toc(par)
        self.espaco_apos_tabela = True

    def _abrir_toc(self, par) -> None:
        for filho in (_el("w:fldChar", fldCharType="begin"),):
            par.add_run()._r.append(filho)
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = ' TOC \\o "1-2" \\h \\z \\u '
        par.add_run()._r.append(instr)
        par.add_run()._r.append(_el("w:fldChar", fldCharType="separate"))

    def _fechar_toc(self, par) -> None:
        par.add_run()._r.append(_el("w:fldChar", fldCharType="end"))

    # --- páginas inteiras: capa, expediente, contracapa ------------------

    def pagina_inteira(self, alvo_doc, largura: float, linhas: list):
        """Tabela de página inteira. linhas: (altura_mm, valign, fundo, margens)."""
        t = self.criar_tabela(alvo_doc, len(linhas), [largura])
        for i, (h, valign, cor, marg) in enumerate(linhas):
            row = t.rows[i]
            row.height = Mm(h)
            row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY
            cell = t.cell(i, 0)
            cell.vertical_alignment = {"top": WD_CELL_VERTICAL_ALIGNMENT.TOP,
                                       "bottom": WD_CELL_VERTICAL_ALIGNMENT.BOTTOM,
                                       "center": WD_CELL_VERTICAL_ALIGNMENT.CENTER}[valign]
            if cor:
                fundo(cell._tc.get_or_add_tcPr(), cor)
            margens_celula(cell, *marg)
            linha_nao_parte(row)
        return t

    def capa(self, el) -> None:
        c = classes(el)
        if "capa-img" in c:
            return self.capa_imagem(el)
        if "capa-branca" in c:
            return self.capa_branca(el)
        return self.capa_azul(el)

    def capa_imagem(self, el) -> None:
        self.entrar("capa", dict(top=0, bottom=0, left=0, right=0))
        img = el.find("img")
        par = self.novo_par(self.doc, None, Ctx(alinhar="left", linha=1.0, depois_mm=0))
        par.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
        if img is not None:
            dados = carregar_imagem(img.get("src", ""), self.base, self.avisos)
            if dados:
                inserir_imagem(par, dados, largura_mm=209, maximo_mm=209,
                               alt=img.get("alt") or "Capa do documento")
                return
        self.avisos.add("capa em imagem não encontrada; a capa ficou em branco")

    def capa_branca(self, el) -> None:
        t_ = self.t
        self.entrar("capa", dict(top=26, bottom=16, left=34, right=30))
        larg = 146.0
        # fundo decorativo: faixa lateral e grafismo, atrás do texto, num parágrafo
        # mínimo antes da tabela (dentro da célula o Word e o LibreOffice o
        # posicionariam em relação à célula, não à página)
        ancora = self.doc.add_paragraph()
        tiny(ancora)
        self.primeiro_da_secao = False
        self.fundo_da_capa(el, ancora)
        tabela = self.pagina_inteira(self.doc, larg, [
            (84, "top", None, (0, 0, 0, 0)),
            (118, "top", None, (0, 0, 0, 0)),
            (38, "bottom", None, (0, 0, 0, 0)),
        ])
        cx = Ctx(alinhar="left", linha=1.0, depois_mm=0, largura=larg)
        # logo
        logo = el.select_one(".cm-logo img")
        c0 = tabela.cell(0, 0)
        par = self.novo_par(c0, None, cx)
        if logo is not None:
            dados = carregar_imagem(logo.get("src", ""), self.base, self.avisos)
            if dados:
                inserir_imagem(par, dados, largura_mm=42, alt=logo.get("alt") or "PGE")
        c1 = tabela.cell(1, 0)
        bloco = el.select_one(".cm-bloco-branco") or el
        sob = bloco.select_one(".cm-sobretitulo")
        if sob is not None and sob.get_text(strip=True):
            self.paragrafo(sob, c1, cx.copia(tam=t_.pt(8.5), negrito=True, cor=LARANJA_ESCURO, depois_mm=6),
                           None, extra_fmt={"caps": True, "esp": 64})
        tit = bloco.select_one(".cm-titulo")
        if tit is not None:
            self.paragrafo(tit, c1, cx.copia(tam=t_.pt(44), negrito=True, cor=MARINHO_ESCURO,
                                             linha=1.08, depois_mm=0))
        fil = c1.add_paragraph()
        fil.paragraph_format.space_before = Mm(9)
        fil.paragraph_format.space_after = Mm(7)
        fil.paragraph_format.right_indent = Mm(larg - 30)
        tiny(fil)
        fil.paragraph_format.space_before = Mm(9)
        fil.paragraph_format.space_after = Mm(7)
        borda_paragrafo(fil, "bottom", LARANJA, 27, 1)
        sub = bloco.select_one(".cm-sub")
        if sub is not None:
            self.paragrafo(sub, c1, cx.copia(tam=t_.pt(13), cor=self.t.marinho, linha=1.35))
        ano = el.select_one(".cm-ano")
        if ano is not None:
            self.paragrafo(ano, tabela.cell(2, 0), cx.copia(tam=t_.pt(8), negrito=True, cor=MARINHO_ESCURO),
                           None, extra_fmt={"esp": 48})

    def fundo_da_capa(self, el, par) -> None:
        """Faixa lateral e grafismo da capa branca, como imagem atrás do texto."""
        grafismo = el.select_one("svg.cm-grafismo")
        interno = "".join(str(x) for x in grafismo.children if isinstance(x, Tag)) if grafismo is not None else ""
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="210" height="297" viewBox="0 0 210 297">'
               + interno +
               f'<rect x="0" y="0" width="14" height="178.2" fill="#{MARINHO}"/>'
               f'<rect x="0" y="178.2" width="14" height="74.25" fill="#{AGUA}"/>'
               f'<rect x="0" y="252.45" width="14" height="44.55" fill="#{LARANJA}"/>'
               '</svg>')
        png = svg_para_png(svg.encode("utf-8"), self.avisos, "grafismo da capa", 1654)
        if not png:
            return
        forma = inserir_imagem(par, png, largura_mm=210, maximo_mm=210, alt="Grafismo decorativo da capa")
        fixar_ao_fundo(forma)

    def capa_azul(self, el) -> None:
        t_ = self.t
        self.entrar("capa", dict(top=0, bottom=0, left=0, right=0))
        if el.select_one(".cm-fundo img") is not None:
            self.avisos.add("capa azul: a arte de fundo (cm-fundo) não vai ao Word; a capa sai em azul liso")
        tabela = self.pagina_inteira(self.doc, 210.0, [
            (110, "top", MARINHO, (30, 25, 0, 25)),
            (160, "bottom", MARINHO, (0, 25, 22, 25)),
            (22, "center", LARANJA, (0, 25, 0, 25)),
        ])
        cx = Ctx(alinhar="left", linha=1.1, depois_mm=0, largura=160, cor=BRANCO)
        c0, c1, c2 = tabela.cell(0, 0), tabela.cell(1, 0), tabela.cell(2, 0)
        logo = el.select_one(".cm-logo img")
        par = self.novo_par(c0, None, cx)
        if logo is not None:
            dados = carregar_imagem(logo.get("src", ""), self.base, self.avisos)
            if dados:
                inserir_imagem(par, dados, largura_mm=52, alt=logo.get("alt") or "PGE")
        tipo = el.select_one(".cm-tipo")
        if tipo is not None:
            self.paragrafo(tipo, c1, cx.copia(tam=t_.pt(12), depois_mm=3), None,
                           extra_fmt={"caps": True, "esp": 40})
        tit = el.select_one(".cm-titulo")
        if tit is not None:
            self.paragrafo(tit, c1, cx.copia(tam=t_.pt(30), negrito=True, depois_mm=4))
        lei = el.select_one(".cm-lei")
        if lei is not None:
            self.paragrafo(lei, c1, cx.copia(tam=t_.pt(13)))
        faixa = el.select_one(".cm-faixa")
        if faixa is not None:
            partes = [s.get_text(strip=True) for s in faixa.find_all("span")]
            par = self.novo_par(c2, None, cx.copia(cor=MARINHO_ESCURO, negrito=True, tam=t_.pt(9.5)))
            par.paragraph_format.tab_stops.add_tab_stop(Mm(160), WD_TAB_ALIGNMENT.RIGHT)
            T = Texto(par, self.base_fmt(cx.copia(cor=MARINHO_ESCURO, negrito=True, tam=t_.pt(9.5))))
            T.add(partes[0] if partes else "")
            if len(partes) > 1:
                T.bruto("\t")
                T.add(partes[1])

    def expediente(self, el) -> None:
        t_ = self.t
        self.entrar("expediente")
        cx = Ctx(alinhar="left", linha=1.3, depois_mm=0, tam=t_.pt(10.5), cor=t_.texto, largura=LARGURA_UTIL)
        logo = el.select_one(".ex-logo img")
        if logo is not None:
            dados = carregar_imagem(logo.get("src", ""), self.base, self.avisos)
            if dados:
                par = self.novo_par(self.doc, None, cx.copia(alinhar="center", depois_mm=7))
                inserir_imagem(par, dados, altura_mm=15, alt=logo.get("alt") or "PGE")
        for bloco in el.select(".ex-bloco"):
            for filho in bloco.find_all("p", recursive=False):
                cl = classes(filho)
                if "ex-rot" in cl:
                    par = self.paragrafo(filho, self.doc, cx.copia(tam=t_.pt(15), negrito=True,
                                                                  cor=t_.marinho, linha=1.25, depois_mm=3.6))
                    borda_paragrafo(par, "top", t_.marinho, 8, 6)
                    borda_paragrafo(par, "bottom", t_.marinho, 8, 6)
                    par.paragraph_format.space_before = Mm(5)
                    par.paragraph_format.keep_with_next = True
                elif "ex-nome" in cl:
                    par = self.paragrafo(filho, self.doc, cx.copia(negrito=True, depois_mm=0))
                    par.paragraph_format.keep_with_next = True
                else:
                    self.paragrafo(filho, self.doc, cx.copia(depois_mm=3.2))
        ficha = el.select_one(".ex-ficha")
        if ficha is not None:
            borda = (4, CINZA_05)
            t, cell = self.caixa(self.doc, cx, None,
                                 dict(top=borda, left=borda, bottom=borda, right=borda), (3, 4, 3, 4))
            t.alignment = None
            cy = cx.copia(tam=t_.pt(9), linha=1.4, depois_mm=1.6, largura=LARGURA_UTIL - 8)
            self.blocos(ficha, cell, cy)
            self.fim_caixa(cell)
            self.avisos.add("expediente: a ficha do documento segue o texto em vez de ficar no pé da página")

    def contracapa(self, el) -> None:
        t_ = self.t
        self.entrar("contracapa")
        tabela = self.pagina_inteira(self.doc, 210.0, [
            (132, "top", MARINHO, (36, 25, 0, 25)),
            (154, "bottom", MARINHO, (0, 25, 30, 25)),
            (3, "center", LARANJA, (0, 0, 0, 0)),
        ])
        cx = Ctx(alinhar="left", linha=1.35, depois_mm=3.4, largura=160, cor=BRANCO)
        c0, c1 = tabela.cell(0, 0), tabela.cell(1, 0)
        logo = el.select_one(".cc-logo img")
        par = self.novo_par(c0, None, cx.copia(alinhar="center", depois_mm=0))
        if logo is not None:
            dados = carregar_imagem(logo.get("src", ""), self.base, self.avisos)
            if dados:
                inserir_imagem(par, dados, largura_mm=60, alt=logo.get("alt") or "PGE")
        unidade = el.select_one(".cc-unidade")
        if unidade is not None:
            self.paragrafo(unidade, c1, cx.copia(tam=t_.pt(15), negrito=True, depois_mm=7, linha=1.3))
        contatos = el.select(".cc-contatos li")
        if contatos:
            self.avisos.add("contracapa: os ícones dos contatos viram um marcador laranja")
        for li in contatos:
            spans = li.find_all("span", recursive=False)
            texto_el = spans[-1] if spans else li
            par = self.novo_par(c1, None, cx.copia(tam=t_.pt(10)))
            T = Texto(par, self.base_fmt(cx.copia(tam=t_.pt(10))))
            T.bruto("●", cor=LARANJA)
            T.bruto("  ")
            self.inline(texto_el, T)
            T.fechar()
        nota = el.select_one(".cc-nota")
        if nota is not None and nota.get_text(strip=True):
            par = self.paragrafo(nota, c1, cx.copia(tam=t_.pt(8), cor="C9D6E1", linha=1.5))
            par.paragraph_format.space_before = Mm(5)

    # --- execução ---------------------------------------------------------

    def converter(self) -> None:
        corpo = self.sopa.body
        if corpo is None:
            raise SystemExit("o HTML não tem <body>")
        corpo_el = corpo
        for tipo, item in list(self.grupos(corpo_el)):
            if tipo == "inline":
                if _so_espaco(item):
                    continue
                self.entrar("corpo")
                self.trecho(item, self.doc, CTX_DOC, True)
            else:
                self.bloco(item, self.doc, CTX_DOC, True)
        if self.n_secoes == 0:
            self.entrar("corpo")
        # a última seção termina com um parágrafo mínimo
        ultimo = self.doc.add_paragraph()
        tiny(ultimo)
        self.finalizar()

    def finalizar(self) -> None:
        doc = self.doc
        props = doc.core_properties
        props.title = self.titulo
        props.author = self.orgao
        props.language = "pt-BR"
        props.comments = "Gerado por diagramacao-pge"
        settings = doc.settings.element

        def antes_de(novo, nomes):
            for n in nomes:
                ref = settings.find(qn("w:" + n))
                if ref is not None:
                    ref.addprevious(novo)
                    return
            settings.append(novo)

        for velho in settings.findall(qn("w:updateFields")):
            settings.remove(velho)
        antes_de(_el("w:updateFields", val="true"),
                 ["hdrShapeDefaults", "footnotePr", "endnotePr", "compat", "docVars", "rsids",
                  "mathPr", "attachedSchema", "themeFontLang", "clrSchemeMapping"])
        compat = settings.find(qn("w:compat"))
        if compat is None:
            compat = _el("w:compat")
            antes_de(compat, ["docVars", "rsids", "mathPr", "attachedSchema", "themeFontLang",
                              "clrSchemeMapping"])
        for velho in compat.findall(qn("w:compatSetting")):
            if velho.get(qn("w:name")) == "compatibilityMode":
                compat.remove(velho)
        cs = _el("w:compatSetting", name="compatibilityMode", uri="http://schemas.microsoft.com/office/word", val=15)
        compat.append(cs)

    def salvar(self, destino: Path) -> Path:
        dados = io.BytesIO()
        self.doc.save(dados)
        try:
            destino.write_bytes(dados.getvalue())
            return destino
        except PermissionError:
            alt = destino.with_name(destino.stem + "-NOVO" + destino.suffix)
            alt.write_bytes(dados.getvalue())
            self.avisos.add(f"{destino.name} está aberto em outro programa; gravei em {alt.name}")
            return alt


def _so_espaco(nos) -> bool:
    return not any((isinstance(n, Tag) and (n.name == "img" or n.get_text(strip=True)))
                   or (isinstance(n, NavigableString) and str(n).strip()) for n in nos)


def _tem_bloco(tag) -> bool:
    return any(isinstance(f, Tag) and f.name in ("p", "div", "ul", "ol", "table", "section", "h1",
                                                  "h2", "h3", "h4", "figure") for f in tag.descendants)


# ---------------------------------------------------------------------------
# API e linha de comando
# ---------------------------------------------------------------------------

AVISOS_FIXOS = [
    "fonte: o .docx declara 'Source Sans 3' mas não a embute. Se ela não estiver instalada no "
    "computador que abrir o Word, o Word troca por outra fonte. Os arquivos estão em "
    "assets/design-system/fonts (SourceSans3-*.ttf).",
    "cabeçalho: o filete cinza perde o trecho laranja de 26 mm do PDF.",
]


def exportar(html: Path, saida: Optional[Path] = None, modo: str = "sobrio",
             tema: Optional[Tema] = None, avisos: Optional[Avisos] = None) -> tuple:
    """Converte `html` em .docx. Devolve (caminho gravado, lista de avisos)."""
    html = Path(html)
    saida = Path(saida) if saida else html.with_name(f"{html.stem}-{modo}.docx")
    avisos = avisos or Avisos()
    conv = Conversor(html, modo, tema or Tema(), avisos)
    conv.converter()
    gravado = conv.salvar(saida)
    return gravado, avisos.linhas() + AVISOS_FIXOS


def imprimir_avisos(linhas: list) -> None:
    print("  Avisos do Word (.docx):")
    for a in linhas:
        print(f"    - {a}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path, help="documento .html final")
    ap.add_argument("--saida", type=Path, default=None, help="caminho do .docx (padrão: ao lado do HTML)")
    ap.add_argument("--modo", choices=["sobrio", "completo"], default="sobrio")
    ap.add_argument("--entrelinha", type=float, default=None, help="entrelinha do corpo (padrão 1,5)")
    ap.add_argument("--espaco-paragrafo", type=float, default=None, dest="espaco_paragrafo")
    ap.add_argument("--corpo", type=float, default=None, help="corpo do texto em pt (padrão 12)")
    ap.add_argument("--paleta", default=None)
    ap.add_argument("--texto", default=None, help="hex do texto de leitura")
    ap.add_argument("--estrutura", default=None, help="hex do azul dos títulos")
    args = ap.parse_args(argv)
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    if not args.html.exists():
        print(f"erro: não encontrei {args.html}", file=sys.stderr)
        return 1
    tema = tema_da_paleta(args.paleta, corpo=args.corpo, entrelinha=args.entrelinha,
                          espaco_paragrafo=args.espaco_paragrafo,
                          texto=args.texto.lstrip("#").upper() if args.texto else None,
                          marinho=args.estrutura.lstrip("#").upper() if args.estrutura else None)
    saida = args.saida
    if saida and not saida.is_absolute() and saida.parent == Path("."):
        saida = args.html.resolve().parent / saida.name
    gravado, avisos = exportar(args.html, saida, args.modo, tema)
    print(f"gerado (Word): {gravado}")
    imprimir_avisos(avisos)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
