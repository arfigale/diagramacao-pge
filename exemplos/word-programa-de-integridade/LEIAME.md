# Versão em Word do Programa de Integridade

O caminho padrão da skill para o Word é `dpge docx` (o `build` já o executa), com `scripts/exportar_docx.py`. Esta pasta guarda uma versão alternativa, feita com docx-js, que foi conferida no Word 2016 e serve de comparação.

Exemplo de como o `documento.html` diagramado pela skill vira um `.docx` editável. Os scripts são deste documento (capa, expediente, rodapé e figuras são os dele). Para outro documento, copie a pasta e ajuste `build.js`.

Já estão aqui o resultado (`Programa-de-Integridade-PGE-MS.docx`), a versão em PDF para comparação e as imagens que o Word usa (`capa.png`, `contracapa.png`, `logo-azul.png`, `fig1.jpg`, `fig2.png`, `fig3.png`).

## Antes de abrir o Word

Instale a Source Sans 3. Sem ela o Word troca o texto por outra fonte (o corpo vira Calibri) e as páginas mudam de lugar.

- Windows: dois cliques em `instalar-fontes.cmd`, na raiz da skill. Não pede administrador e não usa PowerShell.
- Mac e Linux: `python3 scripts/dpge.py fontes`.

O `dpge setup` também instala as fontes. Depois feche e abra o Word.

Ao abrir o `.docx`, o Word pergunta se deve atualizar os campos. Responda "Sim": é o sumário.

## Como refazer o arquivo

Precisa de Node 18 ou mais novo, do Python da skill (`dpge setup`) e do LibreOffice. A partir desta pasta:

```bash
npm install                                  # instala o docx 9.7.1
python3 extrair.py ../../caminho/documento.html   # gera conteudo.json
node build.js                                # gera bruto.docx
python3 pos.py                               # gera Programa-de-Integridade-PGE-MS.docx
```

Os números de página do sumário vêm de `pages.json`. Para recalculá-los depois de mudar o texto:

1. Rode `build.js` e `pos.py` uma vez sem se preocupar com os números.
2. Converta o `.docx` em PDF com o LibreOffice: `soffice --headless --convert-to pdf Programa-de-Integridade-PGE-MS.docx`.
3. `python3 pages.py Programa-de-Integridade-PGE-MS.pdf` grava o novo `pages.json`.
4. Rode `build.js` e `pos.py` de novo.

No Word, os números podem diferir um pouco dos do LibreOffice. Clique com o botão direito no sumário e escolha "Atualizar campo".

## O que `pos.py` corrige

O docx-js gera o arquivo, e `pos.py` ajusta o que ele não faz: transforma o sumário em campo `TOC` do Word, marca Título 1 e 2 com nível de estrutura, normaliza o `fontKey` da fonte embutida e reordena as bordas dos parágrafos para o arquivo passar na validação do formato.

## Limites conhecidos

- Só a variante Regular da fonte vai embutida no `.docx`. Negrito e itálico dependem da fonte instalada.
- As barras de maturidade são caracteres de bloco, não formas desenhadas.
- Capa, contracapa e as figuras 2 e 3 entram como imagem. O organograma é a imagem original.
- O total em "Pág. X de Y" usa o campo de total da seção.
