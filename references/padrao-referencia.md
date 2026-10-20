# Documento de referência do padrão PGE/MS

O **Programa de Integridade da PGE/MS – Compliance Público** (2026, 37 páginas, revisado) foi definido pela usuária como o padrão dos documentos diagramados da PGE/MS. As imagens das páginas estão em `references/padrao-referencia/`. Abra-as antes de montar uma publicação e compare as páginas de `_conferencia/` com elas antes de entregar.

**Precedência:** onde este arquivo diverge de `identidade.md`, `capa-e-contracapa.md` ou `componentes.md`, vale este arquivo.

## O que é igual ao padrão da skill

Estes elementos do documento de referência já são o que o build produz; não mude:

- Source Sans 3 em todo o documento; corpo de 12 pt preto, entrelinha 1,5, justificado, recuo de 1,25 cm na primeira linha.
- Margens A4 de 25 mm nas laterais e 37 mm no topo (o texto começa a 36,9 mm); texto de 24,6 mm a 185,6 mm; 2,4 mm entre parágrafos.
- **Cabeçalho:** logo horizontal azul à esquerda, com um filete laranja curto (26 mm) sobre o filete cinza `#D2D3D5` de largura cheia; à direita, o nome do documento em caixa alta, 7,6 pt seminegrito, azul `#294964`, com entreletra larga (`vl-peca`).
- **Rodapé:** filete cinza com trecho laranja curto à direita; à esquerda a unidade (6,7 pt seminegrito azul); à direita "PÁG. **n** DE **N**" (rótulo cinza `#5A6673`, números em negrito azul).
- **Título de seção** (`h2.secao`): 16 pt negrito azul, com barra laranja vertical à esquerda e número na frente ("2  Ambiente de integridade"). Títulos sem número (Mensagem da Alta Administração, Apresentação, Instituição do…) usam só `.titulo`.
- **Subseção** (`h3.subsecao`): 13 pt negrito azul, número em 12 pt ("2.1 Instrumentos…").
- **Expediente:** logo azul centralizado no alto; rótulo 15 pt negrito azul entre dois filetes azuis; nome em negrito e cargo normal, 10,5 pt, preto. Blocos usados: Dirigentes, Elaboração, Organização e informações, Orientação técnica, Aprovação.
- **Tabela** (`table.dados`): cabeçalho azul `#294964` com texto branco em caixa alta e entreletra, 8,2 pt; células 9,6 pt pretas, filetes cinza entre linhas, linhas alternadas `#FAFAFA`; coluna de texto alinhada à esquerda.
- **Contracapa:** fundo azul, logo branco centralizado no alto, unidade em 15 pt seminegrito branco, contatos com ícones em círculo laranja (site, endereço), faixa laranja no pé.
- **Citação em destaque:** caixa com fundo azul-claro e filete à esquerda, texto em itálico (missão, visão).
- **Listas:** marcador de bolinha azul; listas numeradas "1." e enumerações "a)" recuadas.
- **Link no corpo:** azul, seminegrito (ex.: "Acesse a RESOLUÇÃO PGE/MS/Nº 494…", "clicando **aqui**").

## O que muda em relação ao padrão anterior da skill

### 1. Capa branca: é o padrão

**A capa padrão é a branca** do Programa de Integridade (`.capa-manual.capa-branca`, ativa no modelo `publicacao.html`). A capa azul (`.capa-manual`, com logo branco e faixa laranja, dos manuais da UPD de 2025) é a variante, com a marcação pronta no comentário do modelo, para usar só quando o usuário pedir. Composição da capa branca:

- Fundo **branco**, com **logo horizontal azul** no alto à esquerda (≈ 30 mm do topo, alinhado à coluna do título).
- **Faixa vertical na borda esquerda**, de largura total da página em altura e ≈ 11 mm de largura, em três segmentos de cima para baixo: azul `#294964` (≈ 60 %), verde-água `#51A8B1` (≈ 25 %), laranja `#F58634` (≈ 15 %).
- **Sobretítulo** em caixa alta, laranja, negrito pequeno com entreletra larga ("COMPLIANCE PÚBLICO"), a ≈ 38 % da altura.
- **Título** em negrito pesado, azul-escuro `#223141`, ≈ 44 pt, em até duas ou três linhas, alinhado à esquerda.
- **Filete laranja** curto (≈ 26 mm × 1 mm) sob o título.
- **Subtítulo** com o nome do órgão ("Procuradoria-Geral do Estado / de Mato Grosso do Sul"), ≈ 13 pt, cinza-azulado.
- **Grafismo** no canto inferior direito: círculos concêntricos de traço fino cinza-azulado, um disco azul-médio com o ícone do tema em branco e um ponto verde-água sobre o círculo externo. O Programa de Integridade usa um "check"; o ícone padrão do modelo é um documento, que serve a qualquer documento institucional. O ícone acompanha o tema do documento e se troca pelo `<path>` do SVG.
- **Ano** no pé, à esquerda, em negrito pequeno com entreletra ("2026").
- Sem faixa laranja horizontal e sem edição na faixa.

A capa branca sai em vetor (HTML e SVG inline), sem imagem; troque o ícone do grafismo conforme o tema. A regra de não pôr texto dentro de imagem gerada continua.

### Design: moderno e profissional

Composição limpa, com muito branco e pouca decoração: a cor fica nas peças de estrutura (cabeçalho de tabela, cabeçalho do cartão, selos, barras, filetes), e não em fundos coloridos atrás do texto. Cantos levemente arredondados (≈ 1,8 mm) nos cartões, filetes finos cinza entre linhas, hierarquia por peso e tamanho, e não por cor. Nada de sombra, gradiente decorativo, clip-art nem caixa alta em texto corrido.

### 2. Sumário em azul (substitui o título laranja)

- Título "Sumário" 17 pt negrito **azul `#294964`** entre dois filetes **azuis**.
- O sumário tem cabeçalho e rodapé e é a **página 1** da numeração (o corpo começa na página 2).
- Entrada principal 11 pt negrito preta, com número seguido de ponto ("1. Conhecendo…"); subitem 10 pt normal, recuado ≈ 4 mm; guia pontilhada; página com dois dígitos ("05").
- Com isso, o laranja não aparece mais em texto no corpo do documento.

### 3. Componentes novos (marcação em `componentes.md`)

**Rótulo de tabela** (acima de uma tabela, no lugar de `caption`): traço azul curto + texto em caixa alta, 7,3 pt negrito azul, entreletra larga — "— I – RESULTADOS DO QUESTIONÁRIO DIAGNÓSTICO DA INTEGRIDADE PÚBLICA:".

**Barra de percentual em célula** (tabela de maturidade): número em negrito azul 9,6 pt ("62%") e, abaixo, barra fina arredondada (trilho cinza `#E6E7E8`, preenchimento azul `#294964` proporcional ao valor).

**Legenda de figura:** "**Figura 1** – Organograma da PGE/MS." — "Figura n" em extranegrito azul, descrição em seminegrito preto, 10,5 pt, acima da figura, com filete laranja à esquerda; "Fonte: …" em 9 pt cinza `#5A6673` abaixo.

**Eixo temático** (abre um grupo de ações): selo azul `#294964` com texto branco em caixa alta, 8 pt negrito ("EIXO TEMÁTICO 1:") seguido do nome do eixo em 12,5 pt negrito azul.

**Cartão de ação** (plano de ação):
- Moldura com filete cinza `#D2D3D5` e cantos levemente arredondados, largura cheia.
- Cabeçalho azul `#294964` com selo laranja `#F58634` ("AÇÃO 01", 7,6 pt negrito, texto azul-escuro `#223141`) e o título da ação em 11 pt negrito branco.
- Linhas rótulo / conteúdo: rótulo em 9,6 pt negrito azul na coluna esquerda (≈ 40 mm), conteúdo em 9,6 pt preto alinhado à esquerda; filetes `#DCDDDF` entre linhas e linhas alternadas `#FAFAFA`.
- Lista numerada dentro do cartão com o número em negrito azul.
- Rótulos usados: Justificativa, Objetivos da ação (ou Objetivo), Descrição das Atividades (ou Atividades), Unidade responsável (ou Setor responsável), Unidades de apoio (ou Setores de apoio), Indicador de Desempenho, Indicador de Resultado, Prazo estimado.
- O cartão pode partir entre páginas; o pedaço que continua repete a moldura, sem repetir o cabeçalho.

**Ficha de anexo** (abre um anexo): linha de contexto em 9,6 pt cinza; quadro de duas colunas com rótulos em caixa alta 8,2 pt negrito azul (ÓRGÃO, DATA DE ELABORAÇÃO, ELABORADO POR) e valores em 9,6 pt médio preto.

**Bloco de aprovação e assinatura** (fim do documento): título "Aprovação e assinaturas" em 13 pt negrito azul; filete azul grosso centralizado (≈ 75 mm); nome em 13 pt negrito azul com entreletra leve; cargo em 10 pt azul, centralizados.

**Infográficos** (cadeia de valor, estrutura de governança): diagramas em blocos com cabeçalhos azuis, fundos azul-claro e laranja-claro e rótulos pequenos; entram como figura, com legenda "Figura n".
