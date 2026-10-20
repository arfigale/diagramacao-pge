# Compilar, conferir e resolver problemas

Todos os comandos passam pelo lançador `<dpge>`, que roda de qualquer pasta:

```bash
python3 <pasta-da-skill>/scripts/dpge.py <comando> ...      # Mac e Linux
<pasta-da-skill>\dpge.cmd <comando> ...                     # Windows
```

No Windows o `dpge.cmd` acha o Python (`py` ou `python`) sozinho.

## Comandos

| Comando | O que faz |
|---|---|
| `setup` | cria o ambiente, instala as bibliotecas e confere o navegador (uma vez); baixa o Chromium só se não houver Edge nem Chrome. `--forcar` refaz do zero |
| `doctor` | confere Python, ambiente, fontes, logo e CSS |
| `build doc.html` | compila em PDF A4 e gera o .docx editável ao lado (mesmo nome). Opções abaixo |
| `docx doc.html [--saida X.docx]` | gera só o .docx, sem recompilar o PDF |
| `sumario doc.html [pdf] --ate-estabilizar` | compila, lê o PDF e grava os números de página no sumário, repetindo até estabilizar |
| `checar doc.html [--corrigir]` | relata (e corrige o que é mecânico) problemas de tipografia |
| `converter arq.docx\|.md` | gera o corpo em HTML e o esqueleto do sumário |
| `imagem inspecionar\|fundo\|faixa\|pagina arq` | prepara a imagem de capa (`fundo` é o uso padrão) |

## Opções do build

| Opção | Efeito |
|---|---|
| `--modo sobrio` (padrão) | tipografia, quadros, caixas e tabelas; serve a manual e apostila |
| `--modo completo` | acrescenta números-chave, linha do tempo e gráfico (blocos `so-completo`); para documento curto |
| `--saida arquivo.pdf` | nome do PDF final (padrão: `<html>-<modo>.pdf` ao lado do HTML); o .docx usa o mesmo nome |
| `--sem-docx` | não gera o .docx (por padrão o build gera PDF e Word) |
| `--conferir` | grava um PNG por página em `_conferencia/` |
| `--entrelinha 1.25` | entrelinha do corpo (padrão 1,22) |
| `--espaco-paragrafo 2.5` | espaço entre parágrafos em mm (padrão 3) |
| `--corpo 11.5` | corpo do texto em pt; escala toda a régua junto (padrão 12) |
| `--paleta agua` | cor de acento alternativa: `institucional` (padrão), `agua`, `marinho`, `bordo`, `bronze`, `laranja` |
| `--permitir-pendencias` | compila com `[PREENCHER]` no texto, só para teste |

O build também grava título e autor no PDF a partir de `<title>` e `vl-orgao`. Se o PDF estiver aberto em outro programa no Windows, ele grava `-NOVO.pdf` ao lado e avisa.

## Como o documento é montado

- **Capa e contracapa próprias.** Com `<meta name="vl-capa" content="propria">`, o build imprime a capa numa passada sem margem e sem cabeçalho, o corpo noutra, e a contracapa (`<section class="contracapa">`) numa terceira, e emenda as três. O expediente sai na passada da capa, logo depois dela. Capa, expediente e contracapa não têm número nem cabeçalho; a paginação do rodapé começa no sumário, que é a página 1. O `sumario` desconta essas duas páginas sozinho (`--capas` força outro valor).
- **Cabeçalho e rodapé** vêm do build, não do CSS (o Chromium ignora as margens do CSS paginado). Mexer neles é mexer em `scripts/build.py`. O rodapé leva à esquerda a unidade de `<meta name="vl-unidade">` (ou o número de `vl-processo`, quando houver) e à direita a paginação; os filetes têm um trecho em laranja da marca.
- **Caminhos do design system.** O HTML aponta para `@ds/tokens.css`, `@ds/logo-pge.png` etc.; o build troca pelo caminho da skill numa cópia temporária que some ao fim. Imagens do documento ficam ao lado do HTML e entram por caminho relativo.
- **Número de página do sumário** depende do PDF; por isso `sumario` compila e relê. Rode de novo depois de qualquer mudança de texto.

## Quebra de página

Folga aceitável no pé: até uns 20 mm. Acima de 25 mm, quase sempre um bloco indivisível não coube. Resolva nesta ordem:

1. enxugue o bloco (menos texto, `pode-quebrar` em caixa ou tabela longa);
2. reordene, levando um bloco menor para o buraco;
3. só então force a quebra com `quebra-antes`.

A última página sempre sobra, e a página que termina antes de um título de seção também (o título não fica órfão no pé). Para ganhar uma página inteira, reduza `--entrelinha` (de 1,22 para 1,18, por exemplo): ela mexe no tamanho do documento muito mais do que o corpo da fonte. Não passe de 10 pt de corpo.

## Problemas conhecidos

- **Linha terminando em `art.`, `n.`, `§`, `Lei`**: falta `&nbsp;` depois do marcador. `checar --corrigir` insere; depois recompile e rode `sumario` de novo, porque o texto reflui.
- **Capa vazando para o corpo ou página sumindo**: o CSS declarou `display` duas vezes para `.capa-manual` ou `.contracapa`. Mantenha a regra única de `publicacao.css`.
- **Título do sumário "não encontrado no PDF"**: o texto do `s-tit` difere do título do corpo (acento, espaço, `&nbsp;`). Copie o título do corpo.
- **Fonte fora do padrão no PDF**: `doctor` aponta arquivo de fonte ausente em `assets/design-system/fonts/`.
- **`[PREENCHER]` bloqueia o build**: é proposital. Preencha ou apague o trecho.
- **Nota de rodapé com capa própria**: o build recusa. Use nota de rodapé só em documento curto.
- **Linha de tabela cortada no pé da página**: linha longa demais para a coluna; use `pode-quebrar` na tabela e encurte o texto.
- **PDF grande demais para e-mail**: as imagens da capa em 2480 px bastam; imagem maior não melhora o papel. Reduza a arte de origem com `imagem fundo`.

## Word (.docx)

O build gera, depois do PDF, um `.docx` com o mesmo nome (`exportar_docx.py`, biblioteca python-docx). Ele lê o HTML final e reconstrói o documento com recursos do Word, em vez de converter o PDF. O resumo do build lista os dois arquivos e, logo abaixo da linha `gerado (Word)`, os avisos do que o Word não reproduz igual. Se o .docx falhar, o PDF fica gravado e o erro aparece em vermelho; `--sem-docx` desliga.

- **Página e texto.** A4, margens de 37 mm (topo), 19 mm (pé) e 25 mm (laterais), como no PDF. Corpo preto de 12 pt, entrelinha 1,5, texto justificado. O recuo de primeira linha de 1,25 cm vale só para o texto corrido (estilo Corpo de texto), pela mesma regra do `componentes.css`. `--corpo`, `--entrelinha`, `--espaco-paragrafo`, `--paleta`, `--texto` e `--estrutura` valem para o Word também.
- **Fonte.** O estilo declara `Source Sans 3` e o .docx não embute a fonte. Se ela não estiver instalada no computador que abrir o arquivo, o Word troca por outra, sem aviso na tela. Os arquivos `SourceSans3-*.ttf` estão em `assets/design-system/fonts/`; instalá-los resolve. O negrito usa o peso Bold; os pesos SemiBold e ExtraBold do PDF viram Bold.
- **Títulos.** `h2` vira Título 1 (com a barra laranja), `h3` vira Título 2, `h4` a `h6` viram Título 3, todos em azul `#294964`; aparecem no painel de navegação do Word.
- **Sumário.** É um campo TOC (níveis 1 e 2), com as entradas do HTML já escritas e os números de página que o `sumario` gravou. O arquivo pede ao Word que atualize os campos ao abrir: responda **Sim**. Se responder Não, clique no sumário e use F9. Os números do Word podem diferir dos do PDF, porque a paginação é outra.
- **Seções.** Capa, expediente, corpo (cabeçalho com logo, rodapé com unidade e `Pág. N de M`, numeração reiniciada no sumário) e contracapa são seções separadas. O total `de M` é o campo SECTIONPAGES, que conta só o corpo. O LibreOffice não o calcula e mostra 1; o Word calcula.
- **Caixas e tabelas.** Síntese, atenção, exemplo, nota, requisitos, confronto, modelo e plano de ação são tabelas, com a cor de fundo e a borda do PDF. `table.dados` e `table.criterios` são tabelas reais com linha de cabeçalho repetida entre páginas.

O que sai diferente do PDF, e o aviso que o build imprime:

| No PDF | No Word |
|---|---|
| Barra de percentual (`pct`) | só o número |
| Gráfico de barras (`grafico`) | barras de texto com o valor |
| Linha do tempo (`timeline`) | tabela de duas colunas |
| Nota de rodapé (`nota-rodape`) | texto `[nota: ...]` no ponto da chamada |
| Ícones dos contatos da contracapa | marcador laranja |
| Ficha do expediente no pé da página | logo após o último bloco do expediente |
| Filete do cabeçalho com trecho laranja | filete cinza |
| Capa azul com arte de fundo (`cm-fundo`) | azul liso |
| Imagem SVG ou WebP | convertida em PNG; se falhar, fica de fora e há aviso |
| Classe que não consta em `componentes.md` | o texto entra sem o visual, com aviso |

A capa branca (faixa lateral e grafismo) entra como imagem decorativa atrás do texto; o título, o logo e o ano continuam editáveis. Toda imagem leva texto alternativo; imagem sem `alt` no HTML gera aviso.
