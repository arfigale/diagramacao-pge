#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
imagem.py, prepara a imagem de capa anexada pelo usuário.

    python scripts/dpge.py imagem inspecionar <arquivo>
    python scripts/dpge.py imagem fundo  <arquivo> [--saida capa-fundo.png] [--foco centro]
    python scripts/dpge.py imagem faixa  <arquivo> [--saida capa-faixa.png] [--foco centro]
    python scripts/dpge.py imagem pagina <arquivo> [--saida capa-pagina.png] [--foco centro]

A skill não gera imagem. Ela recebe a que o usuário anexa e a ajusta a um dos
dois usos da capa:

    fundo    A4 inteiro (proporção 0,707), para ir POR BAIXO da capa padrão: o
             build a passa para cinza e a 18% sobre o azul da marca, e o logo,
             o título e a faixa laranja vêm por cima, do HTML. É o uso padrão.
             Arquivo final: 1985 x 2808 px.
    faixa    tira de 210 mm de largura por 71 mm de altura (proporção 2,94:1)
             entre o logo e o campo marinho. O título e o logo vêm por cima do
             HTML, nunca da imagem. Arquivo final: 2480 x 843 px.
    pagina   A4 inteiro (proporção 0,707). A imagem é a capa; nada é desenhado
             por cima. Arquivo final: 1985 x 2808 px.

O recorte nunca deforma: a imagem é cortada na proporção do uso, e o script diz
quanto perdeu. Se perder mais de um terço, escolha outro `--foco` ou outra arte.
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps

USOS = {
    # nome: (largura px, altura px, descrição)
    "fundo": (1985, 2808, "fundo da capa, A4 inteiro"),
    "faixa": (2480, 843, "faixa de 210 x 71 mm"),
    "pagina": (1985, 2808, "A4 inteiro"),
}
FOCOS = {
    "centro": (0.5, 0.5),
    "topo": (0.5, 0.0),
    "base": (0.5, 1.0),
    "esquerda": (0.0, 0.5),
    "direita": (1.0, 0.5),
}


def abrir(caminho: Path) -> Image.Image:
    if not caminho.is_file():
        raise SystemExit(f"não encontrei {caminho}")
    im = ImageOps.exif_transpose(Image.open(caminho))
    if im.mode in ("RGBA", "LA", "P"):
        base = Image.new("RGB", im.size, (255, 255, 255))
        im = im.convert("RGBA")
        base.paste(im, mask=im.split()[-1])
        return base
    return im.convert("RGB")


def inspecionar(caminho: Path) -> int:
    im = abrir(caminho)
    l, a = im.size
    prop = l / a
    print(f"{caminho.name}: {l} x {a} px, proporção {prop:.3f}")
    for nome, (lw, ah, desc) in USOS.items():
        alvo = lw / ah
        # fração da imagem que sobra depois do recorte na proporção do uso
        sobra = min(prop, alvo) / max(prop, alvo)
        ampliacao = max(lw / l, ah / a) if (l < lw or a < ah) else 1.0
        # largura útil depois do recorte, contra a largura final
        util_l = l if prop <= alvo else a * alvo
        dpi = util_l / (210 / 25.4)
        aviso = []
        if sobra < 0.67:
            aviso.append(f"perde {100 * (1 - sobra):.0f}% da imagem no recorte")
        if dpi < 150:
            aviso.append(f"resolução baixa para impressão (~{dpi:.0f} dpi em 210 mm)")
        print(f"  como {nome} ({desc}): fica com {100 * sobra:.0f}% da imagem, "
              f"~{dpi:.0f} dpi" + (f"; ATENÇÃO: {'; '.join(aviso)}" if aviso else ""))
    melhor = min(USOS, key=lambda n: abs(prop - USOS[n][0] / USOS[n][1]))
    print(f"  uso mais natural: {melhor}")
    print("  confira a olho: texto ou logo desenhado dentro da arte não serve (acento "
          "errado, marca fora do padrão); a imagem deve ser só grafismo, a menos que "
          "seja uma capa completa aprovada.")
    return 0


def ajustar(caminho: Path, uso: str, saida: Path, foco: str) -> int:
    im = abrir(caminho)
    lw, ah, desc = USOS[uso]
    if foco in FOCOS:
        fx, fy = FOCOS[foco]
    else:
        try:
            fx, fy = (float(v) for v in foco.split(","))
        except ValueError:
            raise SystemExit("--foco: use centro, topo, base, esquerda, direita ou 'x,y' de 0 a 1")
    l, a = im.size
    alvo = lw / ah
    if l / a > alvo:      # larga demais: corta nas laterais
        nl, na = round(a * alvo), a
    else:                 # alta demais: corta em cima e embaixo
        nl, na = l, round(l / alvo)
    x0 = round((l - nl) * min(max(fx, 0), 1))
    y0 = round((a - na) * min(max(fy, 0), 1))
    recorte = im.crop((x0, y0, x0 + nl, y0 + na))
    perdido = 1 - (nl * na) / (l * a)
    ampliou = lw / nl
    final = recorte.resize((lw, ah), Image.LANCZOS)
    saida.parent.mkdir(parents=True, exist_ok=True)
    final.save(saida, optimize=True)
    print(f"gravado: {saida}  ({lw} x {ah} px, {desc})")
    print(f"  recorte: perdeu {100 * perdido:.0f}% da área"
          + ("  ← muito: tente outro --foco ou outra imagem" if perdido > 0.33 else ""))
    if ampliou > 1.25:
        print(f"  AVISO: a imagem foi ampliada {ampliou:.2f}x; deve sair com pouca "
              "nitidez. Peça ao usuário um arquivo maior.")
    return 0


def main() -> int:
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("inspecionar")
    p.add_argument("arquivo", type=Path)
    for uso in USOS:
        p = sub.add_parser(uso)
        p.add_argument("arquivo", type=Path)
        p.add_argument("--saida", type=Path, default=None)
        p.add_argument("--foco", default="centro")
    args = ap.parse_args()
    if args.cmd == "inspecionar":
        return inspecionar(args.arquivo)
    saida = args.saida or args.arquivo.with_name(f"{args.arquivo.stem}-{args.cmd}.png")
    return ajustar(args.arquivo, args.cmd, saida, args.foco)


if __name__ == "__main__":
    raise SystemExit(main())
