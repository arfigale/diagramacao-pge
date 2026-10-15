#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sumario.py — acerta os números de página do sumário de um manual ou apostila.

    python scripts/dpge.py sumario <documento.html> --ate-estabilizar

O sumário é escrito à mão no HTML com um travessão no lugar do número:

    <li class="parte">
      <span class="s-num">2</span>
      <span class="s-tit"><span>Aspectos práticos</span></span>
      <span class="s-pag">—</span>
    </li>

Este script lê o PDF já compilado, procura cada título e grava a página no
`.s-pag`. Como preencher o sumário muda a altura dele, e isso pode empurrar as
seções, o build precisa ser repetido até os números pararem de mudar. O laço
está no `--ate-estabilizar`, que chama o build.py entre as passadas.

A página impressa não é o índice do PDF: manual tem capa sem numeração, então
a paginação do rodapé começa na primeira página de conteúdo. O deslocamento
vem de `--capas`, que é 1 por padrão.
"""

import argparse
import os
import re
import subprocess
import sys
import html as html_mod
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

ITEM = re.compile(
    r'<li class="(?P<classe>parte|sub)">'
    r'\s*<span class="s-num">(?P<num>[^<]*)</span>'
    r'\s*<span class="s-tit"><span>(?P<titulo>.*?)</span></span>'
    r'\s*<span class="s-pag"(?P<attrs>[^>]*)>(?P<pag>[^<]*)</span>',
    re.DOTALL,
)


def chave(texto: str) -> str:
    """Normaliza para comparar com o texto extraído do PDF: sem acento, sem
    caixa, sem espaço. O texto do PDF vem com quebras de linha no meio dos
    títulos e com os títulos de seção em caixa alta pelo text-transform."""
    texto = re.sub(r"<[^>]+>", "", texto)
    # Sem isto, `&nbsp;` entra na chave como as letras "nbsp" e o título deixa
    # de casar com o texto do PDF. Desde que os marcadores de referência passaram
    # a levar espaço não separável (ver references/tipografia.md §3.1), todo título com
    # "Lei&nbsp;n." caía nessa armadilha.
    texto = html_mod.unescape(texto)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.replace("—", "-").replace("–", "-")
    return re.sub(r"[^a-z0-9]", "", texto.lower())


def paginas_do_pdf(pdf: Path) -> list[str]:
    import pymupdf as fitz

    doc = fitz.open(pdf)
    paginas = [chave(p.get_text()) for p in doc]
    doc.close()
    return paginas


def localizar(alvo: str, paginas: list[str], inicio: int) -> int | None:
    """Primeira página, a partir de `inicio`, cujo texto contém o alvo."""
    for i in range(inicio, len(paginas)):
        if alvo in paginas[i]:
            return i
    return None


def preencher(html_path: Path, pdf: Path, capas: int) -> tuple[bool, list[str]]:
    """Grava os números no HTML. Devolve se algo mudou e o que não foi achado."""
    html = html_path.read_text(encoding="utf-8")
    paginas = paginas_do_pdf(pdf)

    faltando: list[str] = []
    mudou = False
    cursor = capas

    # O próprio sumário repete todos os títulos, então a busca só começa depois
    # dele. Página de sumário é a que contém vários títulos do próprio sumário
    # ao mesmo tempo, e o sumário pode ocupar mais de uma.
    chaves = [chave(m.group("num") + m.group("titulo")) for m in ITEM.finditer(html)]
    if chaves:
        minimo = min(4, len(chaves))
        # No sumário o título vem colado ao número da página (a chave descarta
        # a pontuação), no corpo vem colado ao texto. É o que separa as duas.
        padroes = [re.compile(re.escape(c) + r"\d") for c in chaves]
        densas = [i for i in range(capas, len(paginas))
                  if sum(1 for r in padroes if r.search(paginas[i])) >= minimo]
        if densas:
            ultima = densas[0]
            while ultima + 1 in densas:
                ultima += 1
            cursor = ultima + 1

    def troca(m: re.Match) -> str:
        nonlocal mudou, cursor
        num, titulo = m.group("num").strip(), m.group("titulo")
        alvo = chave(num + titulo)
        achou = localizar(alvo, paginas, cursor)
        if achou is None:
            # Título de parte quebrado em duas linhas no PDF entra sem o número.
            achou = localizar(chave(titulo), paginas, cursor)
        if achou is None:
            faltando.append(f"{num} {re.sub('<[^>]+>', '', titulo)}")
            return m.group(0)
        cursor = achou
        novo = str(achou + 1 - capas)
        if novo != m.group("pag").strip():
            mudou = True
        return (
            f'<li class="{m.group("classe")}">'
            f'<span class="s-num">{m.group("num")}</span>'
            f'<span class="s-tit"><span>{titulo}</span></span>'
            f'<span class="s-pag"{m.group("attrs")}>{novo}</span>'
        )

    novo_html = ITEM.sub(troca, html)
    if novo_html != html:
        html_path.write_text(novo_html, encoding="utf-8")
    return mudou, faltando


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("html", type=Path)
    ap.add_argument("pdf", type=Path, nargs="?")
    ap.add_argument("--capas", type=int, default=1,
                    help="páginas antes da paginação começar (padrão: 1)")
    ap.add_argument("--modo", default="sobrio")
    ap.add_argument("--ate-estabilizar", action="store_true",
                    help="recompila e repete até os números não mudarem")
    ap.add_argument("--max-passadas", type=int, default=5)
    ap.add_argument("--permitir-pendencias", action="store_true",
                    dest="permitir_pendencias",
                    help="repassa ao build: compila mesmo com [PREENCHER] (teste)")
    # O que o script não conhece (--conferir, --paleta, --corpo...) vai direto
    # para o build, para o sumário ser medido com o mesmo PDF que será entregue.
    args, extras = ap.parse_known_args()

    pdf = args.pdf or args.html.parent / f"{args.html.stem}-{args.modo}.pdf"

    def compilar() -> None:
        nonlocal pdf
        r = subprocess.run(
            [sys.executable, str(RAIZ / "scripts" / "build.py"),
             str(args.html.resolve()), "--modo", args.modo,
             *(["--saida", str(pdf.resolve())] if args.pdf else []),
             *(["--permitir-pendencias"] if args.permitir_pendencias else []),
             *extras],
            stdout=subprocess.PIPE, text=True, encoding="utf-8",
            errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"),
        )
        print(r.stdout, end="")
        if r.returncode != 0:
            raise SystemExit(r.returncode)
        # O build pode ter gravado em outro nome (ex.: -NOVO.pdf se o PDF
        # estava aberto); o sumário tem de ler o arquivo que ele realmente gerou.
        gerados = re.findall(r"^gerado: (.+?)  \(\d+ páginas\)", r.stdout, re.M)
        if gerados:
            pdf = Path(gerados[-1])

    # Compilar antes de ler. Sem isto o laco le o PDF que estiver no disco: se
    # o sumario por acaso casar com um PDF velho, ele declara "estavel" e nunca
    # recompila. Foi o que deixou o manual com sumario de 51 paginas depois de o
    # design system passar a gerar 54.
    if args.ate_estabilizar:
        compilar()

    for passada in range(1, args.max_passadas + 1):
        mudou, faltando = preencher(args.html, pdf, args.capas)
        if faltando:
            print("  não encontrados no PDF:")
            for f in faltando:
                print(f"    - {f}")
        if not args.ate_estabilizar:
            print(f"  sumário preenchido ({'mudou' if mudou else 'sem mudança'})")
            return 0
        if not mudou:
            print(f"  sumário estável na passada {passada}")
            return 0
        print(f"  passada {passada}: números mudaram, recompilando")
        compilar()

    print("  AVISO: número de passadas esgotado sem estabilizar")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
