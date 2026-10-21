# diagramacao-pge

Skill para o Claude Code e para o Claude Desktop que diagrama documentos institucionais da Procuradoria-Geral do Estado de Mato Grosso do Sul em PDF A4, com a identidade visual do órgão: capa, expediente, sumário com número de página calculado, corpo, contracapa, cabeçalho e rodapé.

Serve a manual, cartilha, apostila, programa, informativo, relatório, nota técnica e ofício. Não faz peça processual e não gera imagens: a capa padrão é a branca, toda em vetor, e a arte só entra se o usuário anexar uma capa pronta ou pedir a capa azul com imagem de fundo.

A skill conduz uma entrevista curta (título, expediente, contracapa, arte), converte o texto de um `.docx` ou `.md`, monta o documento, confere a tipografia, compila o PDF e mostra cada página para conferência antes de entregar.

## Instalação

Precisa de Python 3.10 ou mais novo (python.org; no Windows, marque "Add python.exe to PATH" ao instalar) e de internet na primeira vez. Funciona em Windows e Mac.

Claude Code, com Git:

```bash
git clone https://github.com/kaoyeoshiro/diagramacao-pge ~/.claude/skills/diagramacao-pge
```

No Windows (PowerShell), o destino é `$env:USERPROFILE\.claude\skills\diagramacao-pge`. Sem Git, use o botão Code > Download ZIP do GitHub e extraia a pasta no mesmo lugar. No Claude Desktop, adicione a pasta (ou um `.zip` dela) como skill pelas configurações.

Na primeira vez, a skill prepara o ambiente sozinha: cria um ambiente virtual, instala as bibliotecas de `scripts/requirements.txt` e usa o Edge ou o Chrome que já estão no computador para gerar o PDF (só baixa o Chromium se não houver nenhum dos dois). Leva alguns minutos. Para adiantar, rode de dentro da pasta da skill:

```bash
python3 scripts/dpge.py setup      # Mac e Linux
dpge.cmd setup                     # Windows (PowerShell: .\dpge.cmd setup)
```

e depois `doctor` no lugar de `setup` para conferir.

## Fontes e versão em Word

O PDF carrega as fontes da própria skill. O Word precisa da Source Sans 3 instalada no computador. No Windows, dê dois cliques em `instalar-fontes.cmd`; no Mac e no Linux, rode `python3 scripts/dpge.py fontes`. O `setup` já faz isso. A instalação é só para o seu usuário e não pede administrador.

O `build` gera o `.docx` junto com o PDF (comando `dpge docx`, desligável com `--sem-docx`). A pasta `exemplos/word-programa-de-integridade/` guarda uma versão alternativa do Programa de Integridade, feita com docx-js e conferida no Word 2016, com os scripts que a geram (`LEIAME.md`).

## Uso

Peça ao Claude, por exemplo: "diagrama este manual no padrão da PGE" anexando o `.docx`. A skill pergunta o que faltar. Também dá para usar os comandos direto, a partir de uma pasta de trabalho onde esteja o `documento.html` (copie `assets/modelos/documento.html` ou `publicacao.html` para lá com esse nome). Abaixo, `dpge` é `python3 <pasta-da-skill>/scripts/dpge.py` no Mac e `<pasta-da-skill>\dpge.cmd` no Windows:

```bash
dpge converter manual.docx --saida corpo.html
dpge imagem faixa arte.png --saida capa-faixa.png
dpge checar documento.html --corrigir
dpge build documento.html --saida Manual.pdf --conferir
dpge sumario documento.html Manual.pdf --ate-estabilizar
```

## O que há no repositório

| Pasta | Conteúdo |
|---|---|
| `SKILL.md` | o fluxo que o Claude segue |
| `assets/design-system/` | tokens, componentes, kit de publicação, fontes, logo, faixa padrão |
| `assets/modelos/` | `publicacao.html` (capa, expediente, sumário, corpo, contracapa) e `documento.html` (documento curto) |
| `scripts/` | `dpge.py` (ponto de entrada), build, sumário, checador de tipografia, conversor, preparo de imagem |
| `references/` | entrevista, componentes, capa e contracapa, build, identidade, tipografia |

## Licença e marca

O código e a documentação são MIT. O logo e a marca da PGE-MS são do órgão e não estão cobertos pela licença; as fontes são OFL. Esta skill não é um produto oficial da PGE-MS. Detalhes em `NOTICE.md`.
