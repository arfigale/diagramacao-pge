#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fontes.py, instala a Source Sans 3 para o usuário atual (sem administrador).

O PDF não precisa disto: o HTML carrega as fontes da própria skill. O Word precisa,
porque o .docx só leva a fonte Regular embutida. Sem a Source Sans 3 instalada, o
Word troca o texto por outra fonte e a paginação muda.

    dpge fontes              instala (ou confirma) as fontes
    dpge fontes --verificar  só diz se estão instaladas, sem instalar

Usa só a biblioteca padrão. Windows: copia para a pasta de fontes do usuário e
registra em HKCU. Mac: ~/Library/Fonts. Linux: ~/.local/share/fonts e fc-cache.
"""

import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

PASTA_FONTES = Path(__file__).resolve().parent.parent / "assets" / "design-system" / "fonts"
# Variantes que o Word usa. Os arquivos "Cab" são recortes para o PDF e não entram.
ARQUIVOS = [
    "SourceSans3-Regular.ttf", "SourceSans3-Italic.ttf", "SourceSans3-Medium.ttf",
    "SourceSans3-SemiBold.ttf", "SourceSans3-SemiBoldItalic.ttf",
    "SourceSans3-Bold.ttf", "SourceSans3-BoldItalic.ttf", "SourceSans3-ExtraBold.ttf",
]


def nome_completo(caminho: Path) -> str:
    """Lê o nome completo (nameID 4) da tabela 'name' do TrueType."""
    d = caminho.read_bytes()
    n_tab = struct.unpack(">H", d[4:6])[0]
    for i in range(n_tab):
        tag, _, off, ln = struct.unpack(">4sIII", d[12 + 16 * i: 28 + 16 * i])
        if tag == b"name":
            _, cont, base = struct.unpack(">HHH", d[off:off + 6])
            achados = {}
            for j in range(cont):
                p, e, _, nid, tam, o = struct.unpack(">6H", d[off + 6 + 12 * j: off + 18 + 12 * j])
                bruto = d[off + base + o: off + base + o + tam]
                if nid == 4 and (p, e) in ((3, 1), (0, 3), (3, 10)):
                    achados["w"] = bruto.decode("utf-16-be")
                elif nid == 4 and p == 1:
                    achados["m"] = bruto.decode("latin-1")
            return achados.get("w") or achados.get("m") or caminho.stem
    return caminho.stem


def destino() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "Microsoft" / "Windows" / "Fonts"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Fonts"
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "fonts"


def instaladas() -> list:
    d = destino()
    return [a for a in ARQUIVOS if (d / a).is_file()]


def avisar_windows() -> None:
    try:
        import ctypes
        ctypes.windll.user32.SendMessageTimeoutW(0xFFFF, 0x001D, 0, 0, 0x0002, 1000, None)  # WM_FONTCHANGE
    except Exception:
        pass


def instalar() -> int:
    falta = [a for a in ARQUIVOS if not (PASTA_FONTES / a).is_file()]
    if falta:
        print("Arquivos de fonte ausentes na skill: " + ", ".join(falta), file=sys.stderr)
        return 1
    d = destino()
    d.mkdir(parents=True, exist_ok=True)
    novas = 0
    if os.name == "nt":
        import winreg
        chave = winreg.CreateKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows NT\CurrentVersion\Fonts")
    for a in ARQUIVOS:
        origem, alvo = PASTA_FONTES / a, d / a
        if not alvo.is_file() or alvo.stat().st_size != origem.stat().st_size:
            shutil.copy2(origem, alvo)
            novas += 1
        if os.name == "nt":
            winreg.SetValueEx(chave, nome_completo(origem) + " (TrueType)", 0,
                              winreg.REG_SZ, str(alvo))
    if os.name == "nt":
        winreg.CloseKey(chave)
        avisar_windows()
    elif sys.platform != "darwin" and shutil.which("fc-cache"):
        subprocess.run(["fc-cache", "-f", str(d)], check=False)
    print(f"Source Sans 3: {len(ARQUIVOS)} variantes em {d} ({novas} copiadas agora).")
    if novas:
        print("Feche e abra o Word para ele enxergar as fontes.")
    return 0


def main(argv: list) -> int:
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    if "--verificar" in argv:
        ok = instaladas()
        print(f"Source Sans 3: {len(ok)} de {len(ARQUIVOS)} variantes em {destino()}")
        return 0 if len(ok) == len(ARQUIVOS) else 1
    return instalar()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
