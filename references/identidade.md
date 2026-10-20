# Identidade visual da PGE-MS

Valores do design system. Estão em `assets/design-system/tokens.css`; esta página resume o que não pode mudar.

O padrão vale para manuais, guias, cartilhas, planos e documentos informativos da PGE. Ele junta duas fontes: o manual da marca da PGE (cores, versões do logo, área de proteção) com as variações oficiais do logo publicadas no anexo do Decreto n. 15.281, de 13 de setembro de 2019, e a composição dos manuais da UPD de 2025 (Guia de Prevenção a Incidentes de Segurança Cibernético, Plano de Resposta a Incidentes de Segurança com Dados Pessoais e Orientações sobre a LGPD), que é a referência de capa, expediente, títulos e contracapa.

## Cores

As três primeiras são as do manual da marca, com os códigos dele.

| Cor | Hex | CMYK | Uso |
|---|---|---|---|
| Azul da marca | `#294964` | 100 / 75 / 40 / 30 | títulos, capa, contracapa, cabeçalho de tabela, estrutura |
| Laranja | `#F58634` | 0 / 60 / 100 / 0 | barra dos títulos de seção, faixas da capa, filetes, marcadores; em texto, nunca |
| Verde-água | `#51A8B1` | 60 / 0 / 20 / 20 | apoio, grafismo; uso raro |
| Preto | `#000000` | | texto de leitura: corpo, células, listas, negrito do corpo |
| Cinza do texto de apoio | `#5A6673` | | legendas de figura, rodapé |
| Cinza de filete | `#D2D3D5` | | filetes, bordas, fundos de quadro |

Texto de leitura é preto e a cor fica na moldura institucional. Negrito do corpo é preto, não azul.

O laranja não serve para texto corrido sobre o branco: o contraste é de 2,5:1, e as WCAG pedem 4,5:1 para texto comum. Pelo mesmo motivo, o texto da faixa laranja da capa azul (variante) é azul-escuro (`#223141`, 5,3:1), e não branco (2,5:1).

Os manuais da UPD usavam cinco azuis e cinco laranjas diferentes. O padrão fica com um de cada, os do manual da marca.

## Fontes

Source Sans 3 no documento inteiro: corpo, títulos, sumário, expediente, capa e contracapa. É sem serifa humanista, de altura de x grande e formas abertas, o que a deixa confortável em leitura longa no papel e na tela. É livre (SIL OFL) e vai dentro da skill, em `assets/design-system/fonts/`, então o documento sai igual em qualquer computador.

As fontes do logotipo, segundo o manual da marca (Nirmala UI Bold no "PGE" e Bahnschrift SemiLight Condensed no nome do órgão), fazem parte do desenho do logo e não se usam em texto. A Helvetica LT Pro dos manuais da UPD é comercial e não pode ir dentro da skill.

Cabeçalho e rodapé também saem em Source Sans 3: o build embute nos dois um subconjunto pequeno da fonte. A Source Sans 3 vai em instâncias estáticas (um arquivo por peso), para o PDF registrar a fonte pelo nome; a versão variável saía como Type 3, sem nome. Montserrat e Source Serif 4 ficam só para a peça processual, fora do escopo.

## Página e texto

A4, margens de 25 mm nas laterais, 37 mm no topo (o texto não encosta no cabeçalho) e 19 mm no pé. Área útil de 160 mm por 241 mm.

Corpo de 12 pt, entrelinha 1,5, 2,4 mm entre parágrafos, recuo de 1,25 cm na primeira linha, texto corrido justificado e sem hifenização. Cerca de 78 caracteres por linha. Entrelinha, espaço entre parágrafos e medida seguem o critério 1.4.8 das WCAG 2.2 (Apresentação visual, nível AAA); a justificação é decisão do padrão da PGE. Coluna estreita (célula de tabela, glossário, ficha, quadro) vai alinhada à esquerda, porque justificada sem hifenização abre vão entre as palavras.

Títulos de seção em 16 pt, subseção em 13 pt, ambos em azul e negrito, só com a primeira letra em maiúscula.

## Marca

- Os logos são os arquivos de `assets/design-system/`, entregues pela usuária, e a regra é fixa:
  - `logo-pge.png`, horizontal azul (letras e brasão em azul, filetes laranja, fundo transparente), em todo o documento: cabeçalho de cada página, expediente e qualquer página de fundo claro;
  - `logo-pge-branco.png`, horizontal branco (letras brancas, brasão em cor, filetes laranja, fundo transparente), só na contracapa e na capa azul (variante), que têm fundo azul. A capa branca, que é o padrão, leva o azul.
- Não se usa outra versão do logo (vertical, policromia sobre branco). Os logos não se alteram, não se recolorem, não se esticam e nunca se pedem a um modelo de imagem. A marca da PGE e os logos pertencem à Procuradoria-Geral do Estado de Mato Grosso do Sul e não estão cobertos pela licença deste repositório.
- A área de proteção do manual da marca é de dois módulos em volta do logo; não encoste texto nem filete nele.
- Nenhuma marca de terceiro entra no documento sem o usuário pedir.
- O documento fala em nome da PGE só se o usuário tem autoridade para isso. Para material de autoria pessoal ou de equipe, o expediente diz quem assina.

## Texto

- Caracteres certos: aspas curvas, reticência `…`, meia-risca `–` em intervalo (`fls. 12–19`), ordinal `º` e `ª`, `n.` e não `nº` (a exceção é o texto citado da norma).
- Espaço não separável depois de `art.`, `n.`, `§`, `inc.`, `Lei`, `Tema`, `Súmula`, `R$`.
- Nunca sublinhar. Ênfase é o negrito.
- Caixa alta só em rótulo curto, com entreletra positiva, e no tipo da publicação na capa (GUIA, PLANO, MANUAL).
- Título que diz o argumento. Máximo de três níveis.

As regras de composição, com o motivo de cada uma, estão em `tipografia.md`. Onde aquele arquivo fala em texto justificado e entrelinha 1,22, vale esta página.

## Layout obrigatório do expediente, do sumário e do cabeçalho

Definido pela usuária a partir do Manual de Condutas Eleitorais 2026 e não negociável:

- **Expediente** (verso da capa): logo horizontal azul centralizado no alto; cada papel (Dirigentes, Elaboração, Revisão, Diagramação…) com o rótulo em azul, 15 pt negrito, entre dois filetes azuis de largura cheia; nome em negrito e cargo em texto normal, ambos em preto, em 10,5 pt. Com capa própria, a página sai junto da capa, sem cabeçalho e sem número.
- **Sumário**: título "Sumário" em azul, 17 pt negrito, entre dois filetes azuis; entrada principal em negrito com o número seguido de ponto ("1. Apresentação"); subitem recuado, em texto normal e corpo menor; guia pontilhada até a página, que tem dois dígitos ("04").
- **Cabeçalho**: logo à esquerda e, à direita, só o nome do manual ou informativo (`vl-peca`). O nome da PGE não se repete, porque já está no logo.
