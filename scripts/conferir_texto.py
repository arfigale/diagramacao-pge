#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
conferir_texto.py, confere se o texto do documento diagramado é o ORIGINAL.

    python scripts/dpge.py conferir-texto <fonte.docx|.md|.txt> [--pdf doc.pdf]
                           [--html documento.html] [--correcoes correcoes.tsv]
                           [--saida relatorio.md] [--json relatorio.json]
                           [--ignorar SELETOR ...]

Compara o texto-fonte (o que o usuário entregou) com o texto extraído do PDF
final e/ou do documento.html. Regra de fidelidade: o texto só pode mudar em
ortografia ou concordância, e só quando a correção estiver autorizada num
arquivo de correções. Todo o resto reprova.

O que é descartado antes de comparar (não vem do texto-fonte):
    capa, expediente, contracapa, sumário, cabeçalho, rodapé, numeração de
    página, blocos de identificação do documento curto (.doc-abertura, .ficha)
    e o que o usuário passar em --ignorar. No PDF, capa, expediente, contracapa
    e sumário são reconhecidos pelas páginas, cruzando com o texto do HTML.

Normalização: espaço, quebra de linha, hifenização de quebra, aspas retas ou
curvas, espaço não separável, caixa, ligaduras e pontuação. A comparação é por
palavra. Por isso a pontuação isolada (vírgula trocada por ponto) NÃO é vista
por este script; o revisor lê os trechos de frase que ele aponta.

Arquivo de correções (TSV, UTF-8, uma por linha, colunas separadas por TAB):
    trecho original <TAB> trecho corrigido <TAB> regra
Linhas vazias e linhas começando por # são ignoradas. A correção vale para
todas as ocorrências do trecho original no texto-fonte. Numeral, nome, cargo,
data e citação de norma não são aceitos como correção (o script recusa quando
os algarismos mudam; nomes e cargos são conferidos pelo revisor).

Cada divergência cai numa destas classes:
    formatação                  ignorada (quebra de linha, hífen de quebra,
                                numeração de título e de lista, aspas)
    correção autorizada         está no arquivo de correções e foi aplicada
    alteração não autorizada    ortografia ou concordância que NÃO está na lista
    alteração de conteúdo       palavra trocada, frase suprimida, acrescentada,
                                duplicada ou reordenada, numeral, nome, cargo,
                                data, citação de norma

Saída: relatório na tela e em arquivo. Código 0 só se não houver alteração de
conteúdo nem alteração não autorizada em nenhum dos alvos conferidos; 1 se
houver; 2 para erro de uso.
"""

import argparse
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

try:
    import pymupdf as fitz
except ImportError:  # versões antigas
    import fitz

# Faixas do PDF (pt, A4 = 842) onde ficam cabeçalho e rodapé das páginas de corpo.
FAIXA_CABECALHO = 88
FAIXA_RODAPE = 800

SELETORES_FIXOS = {
    "capa": ".capa-manual",
    "expediente": ".expediente",
    "contracapa": ".contracapa",
    "sumario": ".sumario, .sumario-titulo",
    "abertura": ".doc-abertura, .ficha",
}
BLOCOS = ["p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "td", "th", "tr", "div",
          "br", "dt", "dd", "figcaption", "ol", "ul", "table", "section", "blockquote",
          "caption", "pre", "hr"]

NUMERAIS = set("""um uma dois duas tres três quatro cinco seis sete oito nove dez onze doze
treze quatorze catorze quinze dezesseis dezessete dezoito dezenove vinte trinta quarenta
cinquenta sessenta setenta oitenta noventa cem cento duzentos trezentos quinhentos mil
milhao milhão milhoes milhões primeiro primeira segundo segunda terceiro terceira quarto
quinto sexto setimo sétimo oitavo nono decimo décimo""".split())

RX_PALAVRA = re.compile(r"[^\W_]+", re.UNICODE)
RX_MARCADOR = re.compile(
    r"^[\(\[]?(?:\d{1,3}(?:\.\d{1,3})*|[A-Za-z][\.\)\]]|[ivxlcdmIVXLCDM]{2,6}[\.\)\]])[\.\)\]]?$")


class Tok:
    __slots__ = ("n", "d", "loc", "marc", "bs", "corr", "pos")

    def __init__(self, n, d, loc, marc, bs, pos):
        self.n, self.d, self.loc, self.marc, self.bs, self.corr, self.pos = n, d, loc, marc, bs, None, pos


def norm(s: str) -> str:
    return unicodedata.normalize("NFKC", s).casefold()


def sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))


def tokenizar(blocos):
    """blocos: lista de (texto, localização). Cada bloco começa um 'início de bloco'."""
    toks = []
    for texto, loc in blocos:
        primeira = True
        for palavra in texto.replace("­", "").split():
            partes = RX_PALAVRA.findall(unicodedata.normalize("NFKC", palavra))
            if not partes:
                continue
            marc = bool(primeira and RX_MARCADOR.match(palavra))
            for p in partes:
                toks.append(Tok(norm(p), p, loc, marc, primeira, len(toks)))
                primeira = False
    return toks


def tokens_de_frase(frase: str):
    return tokenizar([(frase, None)])


# ---------------------------------------------------------------- leitura


def blocos_de_html(bruto: str, tirar=()):
    """Devolve (blocos do texto, {nome: tokens das regiões descartadas})."""
    sopa = BeautifulSoup(bruto, "html.parser")
    for t in sopa.find_all(["script", "style", "head", "svg", "noscript", "template"]):
        t.decompose()
    from bs4 import Comment
    for c in sopa.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    extras = {}
    for nome, sel in list(SELETORES_FIXOS.items()) + [("ignorado", ", ".join(tirar))] * bool(tirar):
        achados = sopa.select(sel)
        partes = []
        for el in achados:
            partes.extend(linhas_de(el))
        extras.setdefault(nome, [])
        extras[nome] += tokenizar([(l, None) for l in partes])
        for el in achados:
            el.decompose()
    return [(l, None) for l in linhas_de(sopa)], extras


def linhas_de(no):
    for t in no.find_all(BLOCOS):
        t.insert_before(NavigableString("\n"))
        t.insert_after(NavigableString("\n"))
    for t in no.select("span.num, span.titulo"):
        t.insert_before(NavigableString(" "))
        t.insert_after(NavigableString(" "))
    texto = no.get_text()
    return [l for l in (x.strip() for x in texto.split("\n")) if l]


def ler_fonte(caminho: Path):
    ext = caminho.suffix.lower()
    if ext == ".docx":
        import mammoth
        with open(caminho, "rb") as f:
            bruto = mammoth.convert_to_html(f).value
        return blocos_de_html(bruto)[0]
    if ext in (".md", ".markdown"):
        import markdown
        bruto = markdown.markdown(caminho.read_text(encoding="utf-8"),
                                  extensions=["tables", "sane_lists"])
        return blocos_de_html(bruto)[0]
    texto = caminho.read_text(encoding="utf-8", errors="replace")
    return [(l.strip(), None) for l in texto.splitlines() if l.strip()]


def paginas_do_pdf(caminho: Path):
    """Lista de páginas; cada uma é lista de linhas (texto) já sem cabeçalho e rodapé."""
    doc = fitz.open(str(caminho))
    paginas = []
    for pg in doc:
        linhas = []
        for b in pg.get_text("blocks", sort=True):
            x0, y0, x1, y1, txt = b[:5]
            if len(b) > 6 and b[6] != 0:  # bloco de imagem
                continue
            linhas.append((y0, y1, txt))
        paginas.append(linhas)
    return paginas


def blocos_de_pdf(caminho: Path, extras, relato):
    """Descarta páginas de capa, expediente, contracapa e sumário e as faixas
    de cabeçalho e rodapé. Devolve os blocos com a página de cada linha."""
    paginas = paginas_do_pdf(caminho)
    n = len(paginas)

    def toks_pag(i, corpo=False):
        return tokenizar([(t, None) for (y0, y1, t) in paginas[i]
                          if not corpo or (y1 >= FAIXA_CABECALHO and y0 <= FAIXA_RODAPE)])

    def cobre(i, nomes, limite=0.6):
        ref = {t.n for nome in nomes for t in extras.get(nome, [])}
        ts = juntar_soletrado([t.n for t in toks_pag(i)])
        return bool(ts) and bool(ref) and sum(1 for x in ts if x in ref) / len(ts) >= limite

    descartadas = {}
    i = 0
    while i < n and cobre(i, ["capa", "expediente"]):
        descartadas[i] = "capa/expediente"
        i += 1
    if n and (n - 1) not in descartadas and cobre(n - 1, ["contracapa"]):
        descartadas[n - 1] = "contracapa"
    # sumário: a página que abre com o título e as seguintes, até esgotar as entradas
    alvo = [t.n for t in extras.get("sumario", [])]
    if alvo and i < n:
        conjunto = set(alvo)
        ts = [t.n for t in toks_pag(i, True)]
        if ts and ts[0] in ("sumário", "sumario"):
            descartadas[i] = "sumário"
            restante = len(alvo) - sum(1 for x in ts if x in conjunto)
            j = i + 1
            while j < n and restante > 0:
                ts = [t.n for t in toks_pag(j, True)]
                if ts and sum(1 for x in ts if x in conjunto) / len(ts) >= 0.95:
                    descartadas[j] = "sumário"
                    restante -= len(ts)
                    j += 1
                else:
                    break
    for k, v in sorted(descartadas.items()):
        relato.append(f"página {k + 1} descartada ({v})")

    blocos = []
    for k, linhas in enumerate(paginas):
        if k in descartadas:
            continue
        for (y0, y1, t) in linhas:
            if y1 < FAIXA_CABECALHO or y0 > FAIXA_RODAPE:
                continue
            for l in t.splitlines():
                if l.strip():
                    blocos.append((l.strip(), k + 1))
    return blocos


def juntar_soletrado(ns):
    """'t e s t e' (letras espaçadas por CSS) vira 'teste'."""
    out, run = [], []
    for x in ns + [None]:
        if x is not None and len(x) == 1 and x.isalpha():
            run.append(x)
            continue
        if len(run) >= 3:
            out.append("".join(run))
        else:
            out.extend(run)
        run = []
        if x is not None:
            out.append(x)
    return out


def tirar_sequencia(toks, seq):
    """Remove a primeira ocorrência da sequência (best effort)."""
    ns = [t.n for t in seq]
    if len(ns) < 2:
        return toks
    alvo = [t.n for t in toks]
    for i in range(len(alvo) - len(ns) + 1):
        if alvo[i:i + len(ns)] == ns:
            return toks[:i] + toks[i + len(ns):]
    return toks


# ---------------------------------------------------------------- correções


def ler_correcoes(caminho: Path):
    """Lista de dicts {orig, corr, regra, linha}."""
    out = []
    for k, linha in enumerate(caminho.read_text(encoding="utf-8").splitlines(), 1):
        if not linha.strip() or linha.lstrip().startswith("#"):
            continue
        cols = linha.split("\t")
        if len(cols) < 2:
            raise SystemExit(f"{caminho}:{k}: esperado 'original<TAB>corrigido<TAB>regra'")
        out.append({"orig": cols[0].strip(), "corr": cols[1].strip(),
                    "regra": cols[2].strip() if len(cols) > 2 else "", "linha": k})
    return out


def aplicar_correcoes(fonte, correcoes):
    """Aplica as correções autorizadas aos tokens da fonte. Devolve (tokens, avisos, invalidas)."""
    avisos, invalidas = [], []
    for ci, c in enumerate(correcoes):
        o, r = tokens_de_frase(c["orig"]), tokens_de_frase(c["corr"])
        no, nr = [t.n for t in o], [t.n for t in r]
        c["achadas"] = 0
        if not no or no == nr:
            avisos.append(f"correção da linha {c['linha']} não muda nenhuma palavra: ignorada")
            continue
        if {x for x in no if re.search(r"\d", x) or x in NUMERAIS} != {x for x in nr if re.search(r"\d", x) or x in NUMERAIS}:
            invalidas.append(c)
            continue
        i = 0
        saida = []
        ns = [t.n for t in fonte]
        while i < len(fonte):
            if ns[i:i + len(no)] == no:
                for k, t in enumerate(r):
                    nt = Tok(t.n, t.d, fonte[i].loc, False, k == 0 and fonte[i].bs, 0)
                    nt.corr = ci
                    nt.marc = fonte[i].marc and k == 0
                    saida.append(nt)
                c["achadas"] += 1
                i += len(no)
            else:
                saida.append(fonte[i])
                i += 1
        fonte = saida
        for p, t in enumerate(fonte):
            t.pos = p
        if not c["achadas"]:
            avisos.append(f"correção da linha {c['linha']} ('{c['orig']}') não aparece no texto-fonte")
    return fonte, avisos, invalidas


# ---------------------------------------------------------------- comparação


def parecida(x: str, y: str) -> bool:
    ax, ay = sem_acento(x), sem_acento(y)
    if ax == ay:
        return True
    r = difflib.SequenceMatcher(None, ax, ay).ratio()
    return r >= (0.8 if min(len(ax), len(ay)) >= 4 else 0.66)


def tem_numero(t: Tok) -> bool:
    return bool(re.search(r"\d", t.n)) or sem_acento(t.n) in {sem_acento(x) for x in NUMERAIS}


def pode_ser_nome(t: Tok, ant: Tok | None) -> bool:
    """Palavra com inicial maiúscula fora de início de frase: nome, cargo ou sigla."""
    return t.d[:1].isupper() and not t.bs


def contexto(toks, i, j, raio=6):
    a = " ".join(t.d for t in toks[max(0, i - raio):i])
    b = " ".join(t.d for t in toks[j:j + raio])
    return a, b


def texto(toks):
    return " ".join(t.d for t in toks)


def contem(toks, seq):
    ns, ss = [t.n for t in toks], [t.n for t in seq]
    if not ss:
        return False
    return any(ns[i:i + len(ss)] == ss for i in range(len(ns) - len(ss) + 1))


def comparar(fonte, saida, extras, correcoes):
    """Compara dois fluxos de tokens e classifica cada divergência."""
    mapa = {}
    ia = [mapa.setdefault(t.n, len(mapa)) for t in fonte]
    ib = [mapa.setdefault(t.n, len(mapa)) for t in saida]
    sm = difflib.SequenceMatcher(None, ia, ib, autojunk=False)
    ops = sm.get_opcodes()

    iguais = 0
    formatacao = []
    autorizadas_ok = set()
    corridas = []  # (a_ini, a_fim, b_ini, b_fim)
    for tag, a0, a1, b0, b1 in ops:
        if tag == "equal":
            iguais += a1 - a0
            for t in fonte[a0:a1]:
                if t.corr is not None:
                    autorizadas_ok.add(t.corr)
            continue
        A, B = fonte[a0:a1], saida[b0:b1]
        # hifenização de quebra e palavra partida: mesma sequência de letras
        if A and B and "".join(t.n for t in A) == "".join(t.n for t in B):
            iguais += len(A)
            formatacao.append(("quebra de palavra", texto(A), texto(B)))
            for t in A:
                if t.corr is not None:
                    autorizadas_ok.add(t.corr)
            continue
        # numeração de título e marcador de lista: não vêm do texto
        while A and A[0].marc:
            formatacao.append(("numeração/marcador do original", A[0].d, ""))
            A = A[1:]
            a0 += 1
        while B and B[0].marc:
            formatacao.append(("numeração/marcador do documento", "", B[0].d))
            B = B[1:]
            b0 += 1
        if not A and not B:
            continue
        corridas.append([a0, a0 + len(A), b0, b0 + len(B)])

    achados = {"ausente": [], "acrescentado": [], "trocada": [], "reordenada": [],
               "duplicada": [], "nao_autorizada": [], "coberto": [], "nao_aplicada": []}

    # reordenação: trecho suprimido numa posição e idêntico acrescentado em outra
    puras_del = [c for c in corridas if c[2] == c[3] and c[1] - c[0] >= 3]
    puras_ins = [c for c in corridas if c[0] == c[1] and c[3] - c[2] >= 3]
    usadas = set()
    for d in puras_del:
        da = fonte[d[0]:d[1]]
        for ins in puras_ins:
            if id(ins) in usadas:
                continue
            ib_ = saida[ins[2]:ins[3]]
            if difflib.SequenceMatcher(None, [t.n for t in da], [t.n for t in ib_],
                                       autojunk=False).ratio() >= 0.9:
                usadas.add(id(ins))
                usadas.add(id(d))
                achados["reordenada"].append({
                    "texto": texto(da), "de": local(fonte, d[0]), "para": local(saida, ins[2])})
                iguais += len(da)
                break

    for c in corridas:
        if id(c) in usadas:
            continue
        a0, a1, b0, b1 = c
        A, B = fonte[a0:a1], saida[b0:b1]
        info = {"antes": texto(A), "depois": texto(B),
                "onde_fonte": local(fonte, a0), "onde_saida": local(saida, b0),
                "ctx": contexto(fonte if A else saida, a0 if A else b0, a1 if A else b1)}
        corr_ids = {t.corr for t in A if t.corr is not None}
        if corr_ids:
            # a fonte já traz o texto corrigido e o documento não o tem
            orig = " ".join(correcoes[k]["orig"] for k in sorted(corr_ids))
            if B and [t.n for t in B] == [t.n for t in tokens_de_frase(orig)][:len(B)]:
                info["regra"] = "; ".join(correcoes[k]["regra"] for k in corr_ids)
                achados["nao_aplicada"].append(info)
                continue
        if A and not B:
            if len(A) >= 1 and any(contem(extras.get(n, []), A) for n in ("capa", "expediente", "contracapa", "abertura", "ignorado")):
                achados["coberto"].append(info)
                iguais += len(A)
            else:
                achados["ausente"].append(info)
            continue
        if B and not A:
            if len(B) >= 4 and contem(fonte, B):
                achados["duplicada"].append(info)
            else:
                achados["acrescentado"].append(info)
            continue
        # substituição
        if len(A) == len(B) and not any(tem_numero(t) for t in A + B) \
                and not any(pode_ser_nome(t, None) for t in A + B) \
                and all(parecida(x.n, y.n) for x, y in zip(A, B)):
            achados["nao_autorizada"].append(info)
        else:
            achados["trocada"].append(info)
    return {"iguais": iguais, "formatacao": formatacao, "achados": achados,
            "autorizadas_ok": autorizadas_ok, "n_fonte": len(fonte), "n_saida": len(saida)}


def local(toks, i):
    if i >= len(toks):
        return "fim"
    t = toks[i]
    return f"página {t.loc}" if t.loc else f"palavra {t.pos + 1}"


# ---------------------------------------------------------------- relatório


def reprovou(r):
    a = r["achados"]
    return any(a[k] for k in ("ausente", "acrescentado", "trocada", "reordenada", "duplicada", "nao_autorizada"))


def percentuais(r):
    m = r["iguais"]
    na, nb = r["n_fonte"], r["n_saida"]
    return (100 * m / na if na else 100.0, 100 * m / nb if nb else 100.0,
            100 * 2 * m / (na + nb) if na + nb else 100.0)


def linhas_relatorio(nome, r, avisos):
    a = r["achados"]
    pa, pb, pc = percentuais(r)
    L = [f"## {nome}", ""]
    L.append(f"Palavras: original {r['n_fonte']}, documento {r['n_saida']}. "
             f"Coincidência {pc:.2f}%. Original presente {pa:.2f}%. "
             f"Documento que vem do original {pb:.2f}%.")
    L.append(f"Resultado: {'REPROVADO' if reprovou(r) else 'APROVADO'}.")
    L.append("")
    for av in avisos:
        L.append(f"Aviso: {av}")
    if avisos:
        L.append("")

    def bloco(titulo, itens, fmt):
        if not itens:
            return
        L.append(f"### {titulo} ({len(itens)})")
        L.append("")
        for k, it in enumerate(itens, 1):
            L.extend(fmt(k, it))
        L.append("")

    def ctx(it):
        return f"   contexto: ...{it['ctx'][0]} [...] {it['ctx'][1]}..."

    bloco("Alteração de conteúdo: trecho do original ausente no documento", a["ausente"],
          lambda k, it: [f"{k}. {it['onde_fonte']}: \"{it['antes']}\"", ctx(it)])
    bloco("Alteração de conteúdo: trecho acrescentado que não está no original", a["acrescentado"],
          lambda k, it: [f"{k}. {it['onde_saida']}: \"{it['depois']}\"", ctx(it)])
    bloco("Alteração de conteúdo: palavra ou trecho trocado", a["trocada"],
          lambda k, it: [f"{k}. {it['onde_fonte']} / {it['onde_saida']}",
                         f"   antes: \"{it['antes']}\"", f"   depois: \"{it['depois']}\"", ctx(it)])
    bloco("Alteração de conteúdo: trecho reordenado", a["reordenada"],
          lambda k, it: [f"{k}. \"{it['texto'][:200]}\" estava em {it['de']} e foi para {it['para']}"])
    bloco("Alteração de conteúdo: trecho duplicado", a["duplicada"],
          lambda k, it: [f"{k}. {it['onde_saida']}: \"{it['depois']}\""])
    bloco("Alteração não autorizada (ortografia ou concordância fora da lista de correções)",
          a["nao_autorizada"],
          lambda k, it: [f"{k}. {it['onde_fonte']} / {it['onde_saida']}",
                         f"   antes: \"{it['antes']}\"", f"   depois: \"{it['depois']}\"", ctx(it)])
    bloco("Correção autorizada que não foi aplicada (informativo)", a["nao_aplicada"],
          lambda k, it: [f"{k}. {it['onde_saida']}: o documento mantém \"{it['depois']}\" "
                         f"e a lista manda \"{it['antes']}\""])
    bloco("Trecho do original que aparece só na capa, expediente ou contracapa (informativo)",
          a["coberto"], lambda k, it: [f"{k}. \"{it['antes']}\""])
    return L


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("fonte", type=Path, help="texto original: .docx, .md ou .txt")
    ap.add_argument("--pdf", type=Path, help="PDF final")
    ap.add_argument("--html", type=Path, help="documento.html que gerou o PDF")
    ap.add_argument("--correcoes", type=Path, help="TSV: original, corrigido, regra")
    ap.add_argument("--saida", type=Path, help="relatório em Markdown (padrão: ao lado do alvo)")
    ap.add_argument("--json", type=Path, help="relatório também em JSON")
    ap.add_argument("--ignorar", action="append", default=[], metavar="SELETOR",
                    help="seletor CSS de blocos do HTML que não vêm do texto-fonte (repetível)")
    args = ap.parse_args()

    if not args.pdf and not args.html:
        print("informe --pdf e/ou --html", file=sys.stderr)
        return 2
    for p in (args.fonte, args.pdf, args.html, args.correcoes):
        if p and not p.is_file():
            print(f"arquivo não encontrado: {p}", file=sys.stderr)
            return 2

    correcoes = ler_correcoes(args.correcoes) if args.correcoes else []
    fonte0 = tokenizar(ler_fonte(args.fonte))
    fonte, avisos_c, invalidas = aplicar_correcoes(fonte0, correcoes)

    extras = {}
    html_blocos = None
    if args.html:
        html_blocos, extras = blocos_de_html(args.html.read_text(encoding="utf-8"), args.ignorar)

    saidas = []
    if args.html:
        saidas.append(("documento.html", args.html, tokenizar(html_blocos), []))
    if args.pdf:
        relato = []
        blocos = blocos_de_pdf(args.pdf, extras, relato)
        toks = tokenizar(blocos)
        for nome in ("abertura", "ignorado"):
            if extras.get(nome):
                toks = tirar_sequencia(toks, extras[nome])
        saidas.append(("PDF", args.pdf, toks, relato))

    L = ["# Conferência do texto original", "",
         f"Fonte: {args.fonte}",
         f"Correções autorizadas: {len(correcoes)} ({args.correcoes})" if correcoes
         else "Correções autorizadas: nenhuma", ""]
    if invalidas:
        L.append("### Correção recusada (muda numeral, que nunca é correção) ")
        for c in invalidas:
            L.append(f"- linha {c['linha']}: \"{c['orig']}\" para \"{c['corr']}\"")
        L.append("")
    resultados, falhou = {}, bool(invalidas)
    for nome, caminho, toks, relato in saidas:
        r = comparar(fonte, toks, extras, correcoes)
        nao_achadas = [c for c in correcoes if c.get("achadas") == 0]
        avisos = list(relato) + avisos_c
        for k, c in enumerate(correcoes):
            if c.get("achadas") and k in r["autorizadas_ok"]:
                avisos.append(f"correção autorizada aplicada ({c['achadas']}x): "
                              f"\"{c['orig']}\" para \"{c['corr']}\"" +
                              (f" [{c['regra']}]" if c["regra"] else ""))
        if r["formatacao"]:
            avisos.append(f"{len(r['formatacao'])} diferença(s) de formatação ignorada(s) "
                          "(hífen de quebra, numeração de título e de lista)")
        L.extend(linhas_relatorio(f"{nome} ({caminho.name})", r, avisos))
        falhou = falhou or reprovou(r)
        resultados[nome] = {
            "aprovado": not reprovou(r),
            "palavras_fonte": r["n_fonte"], "palavras_documento": r["n_saida"],
            "coincidencia": round(percentuais(r)[2], 2),
            "achados": {k: len(v) for k, v in r["achados"].items()},
            "detalhe": r["achados"],
        }
    L.append(f"Resultado geral: {'REPROVADO' if falhou else 'APROVADO'}.")
    rel = "\n".join(L) + "\n"
    print(rel)

    base = args.pdf or args.html
    destino = args.saida or base.with_name(base.stem + "-conferencia-texto.md")
    destino.write_text(rel, encoding="utf-8")
    print(f"relatório gravado em {destino}")
    if args.json:
        args.json.write_text(json.dumps({"aprovado": not falhou, "alvos": resultados},
                                        ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if falhou else 0


if __name__ == "__main__":
    raise SystemExit(main())
