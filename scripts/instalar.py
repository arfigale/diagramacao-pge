#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
instalar.py, instala ou atualiza a skill diagramacao-pge em um comando.

    python3 scripts/instalar.py              instala/atualiza e prepara tudo
    python3 scripts/instalar.py --sem-setup  só copia/atualiza a pasta e gera o zip
    python3 scripts/instalar.py --destino X  usa outra pasta de skills (padrão: ~/.claude/skills)

O que faz, nesta ordem:
  1. Coloca a skill em <pasta de skills>/diagramacao-pge. Se a pasta já é um
     repositório git, atualiza com git pull; se não existe, copia a que está
     rodando este script; se este script já está lá, só segue.
  2. Roda o setup: ambiente Python, bibliotecas, navegador do PDF e a fonte
     Source Sans 3 (necessária para o Word).
  3. Gera diagramacao-pge.zip na pasta Downloads, para quem usa o Claude no site
     ou no aplicativo (Customize > Skills > Adicionar > Fazer upload de Skill).
  4. Roda o doctor e imprime o que deu certo e o que falta.

Usa só a biblioteca padrão. Não precisa de administrador.
"""

import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
NOME = "diagramacao-pge"
IGNORAR = {".git", "__pycache__", "node_modules"}


def rodar(cmd, **kw) -> int:
    return subprocess.run([str(c) for c in cmd], **kw).returncode


def copiar(origem: Path, destino: Path) -> None:
    def filtro(_dir, nomes):
        return [n for n in nomes if n in IGNORAR]
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(origem, destino, ignore=filtro)


def colocar_skill(skills: Path) -> Path:
    destino = skills / NOME
    skills.mkdir(parents=True, exist_ok=True)
    if destino.resolve() == RAIZ:
        print(f"[1/4] a skill já está em {destino}")
        if (destino / ".git").is_dir() and shutil.which("git"):
            rodar(["git", "-C", destino, "pull", "--ff-only"])
        return destino
    if (destino / ".git").is_dir() and shutil.which("git"):
        print(f"[1/4] atualizando {destino} (git pull)")
        if rodar(["git", "-C", destino, "pull", "--ff-only"]) == 0:
            return destino
        print("      git pull falhou; vou substituir pela cópia atual")
    print(f"[1/4] copiando a skill para {destino}")
    copiar(RAIZ, destino)
    return destino


def gerar_zip() -> Path:
    pasta = Path.home() / "Downloads"
    pasta = pasta if pasta.is_dir() else Path.home()
    zip_path = pasta / f"{NOME}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for arq in sorted(RAIZ.rglob("*")):
            rel = arq.relative_to(RAIZ)
            if arq.is_dir() or IGNORAR & set(rel.parts):
                continue
            z.write(arq, Path(NOME) / rel)
    return zip_path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--destino", help="pasta de skills (padrão: ~/.claude/skills)")
    ap.add_argument("--sem-setup", action="store_true", help="não prepara o ambiente")
    a = ap.parse_args()

    if sys.version_info < (3, 10):
        print("Precisa de Python 3.10 ou mais novo (python.org).", file=sys.stderr)
        return 1

    skills = Path(a.destino).expanduser() if a.destino else Path.home() / ".claude" / "skills"
    destino = colocar_skill(skills)
    dpge = destino / "scripts" / "dpge.py"

    status = 0
    if a.sem_setup:
        print("[2/4] setup ignorado (--sem-setup)")
    else:
        print("[2/4] preparando o ambiente e instalando a fonte (alguns minutos na primeira vez)")
        status = rodar([sys.executable, dpge, "setup"])

    print("[3/4] gerando o zip para o Claude no site ou no aplicativo")
    zip_path = gerar_zip()
    print(f"      {zip_path}")

    print("[4/4] conferindo")
    if not a.sem_setup:
        status = rodar([sys.executable, dpge, "doctor"]) or status

    print()
    print(f"Skill instalada em: {destino}")
    print("Claude Code: já vale, abra uma conversa nova.")
    print(f"Claude no site ou no aplicativo: envie {zip_path} em Customize > Skills > "
          "Adicionar > Fazer upload de Skill.")
    print("Word: feche e abra o Word depois da instalação da fonte.")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
