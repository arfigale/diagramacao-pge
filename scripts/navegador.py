#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
navegador.py, escolhe o navegador que imprime o PDF.

Ordem: o Chromium do próprio Playwright (se foi baixado), o Google Chrome e o
Microsoft Edge instalados no computador. Computador institucional que não baixa
nada quase sempre tem o Edge, e o Playwright o conduz sem instalar nada.

`DPGE_NAVEGADOR=chromium|chrome|edge` escolhe o primeiro a tentar.

Rodado como script, imprime o nome do navegador que abriu (usado pelo
`dpge.py setup` e `doctor`) e sai com 1 se nenhum abriu.
"""

import os
import sys

OPCOES = [
    ("chromium", {}),
    ("chrome", {"channel": "chrome"}),
    ("edge", {"channel": "msedge"}),
]


def abrir(p):
    """Devolve (navegador, nome). Levanta SystemExit se nenhum abrir."""
    preferido = os.environ.get("DPGE_NAVEGADOR", "").strip().lower()
    ordem = sorted(OPCOES, key=lambda o: 0 if o[0] == preferido else 1)
    falhas = []
    for nome, kw in ordem:
        try:
            return p.chromium.launch(**kw), nome
        except Exception as e:  # navegador ausente, versão recusada, sem permissão
            falhas.append(f"  {nome}: {str(e).splitlines()[0][:110]}")
    raise SystemExit(
        "Nenhum navegador abriu para gerar o PDF.\n" + "\n".join(falhas) +
        "\nInstale o Microsoft Edge ou o Google Chrome, ou rode "
        "`python scripts/dpge.py setup` com internet para baixar o Chromium.")


if __name__ == "__main__":
    from playwright.sync_api import sync_playwright

    try:
        with sync_playwright() as p:
            nav, nome = abrir(p)
            print(f"{nome} {nav.version}")
            nav.close()
    except SystemExit:
        sys.exit(1)
