# Entrevista: o que perguntar antes de diagramar

Pergunte só o que o texto recebido e o pedido não respondem. Use `AskUserQuestion` quando houver opções fechadas, no máximo três perguntas por vez, em linguagem simples, com a opção recomendada primeiro e o motivo em uma frase. Para dado que o usuário tem de digitar (nomes, endereço), peça em texto livre e junte vários em uma mensagem.

## 1. Tipo e tamanho

| Pergunta | Muda o quê |
|---|---|
| O que é o documento? (manual, cartilha, apostila, programa, informativo, ofício, relatório, nota técnica) | escolhe o modelo e o texto do cabeçalho |
| Quantas páginas, mais ou menos? Precisa de capa e sumário? | acima de umas 8 páginas ou com capa: `publicacao.html`; abaixo disso: `documento.html` |
| Vai ser lido na tela ou impresso? | na tela, nada muda; impresso, avise que a capa sangra e confira a margem com a gráfica |

## 2. Capa (publicação)

| Pergunta | Onde entra |
|---|---|
| Que tipo de publicação é (Guia, Plano, Manual, Cartilha, Orientações)? | `.cm-tipo`, em caixa alta; pode ficar sem, se o título já disser o tipo |
| Título completo, em até três linhas | `h1.cm-titulo`, com `<br>` nas quebras |
| Subtítulo ou norma de referência (ex.: Lei n. 13.709/2018) | `.cm-lei`; apague se não houver |
| Unidade responsável, como deve aparecer na faixa (ex.: UPD – PGE/MS – Unidade de Proteção de Dados Pessoais) | `.cm-faixa`, à esquerda |
| Edição e ano (ex.: 1ª edição \| 2026) | `.cm-edicao`, à direita da faixa |
| Tem arte para a capa? Veja `capa-e-contracapa.md` | fundo da capa padrão, página inteira ou azul liso |

## 3. Expediente (verso da capa)

Pergunte quem consta e em qual papel: Dirigentes, elaboração ou atualização do conteúdo, revisão, diagramação, capa, apoio, aprovação. Para cada pessoa, nome completo com acento e cargo, na ordem em que devem aparecer. Cada papel é um `.ex-bloco`; várias pessoas no mesmo papel ficam no mesmo bloco, um par `.ex-nome` e `.ex-cargo` para cada uma. Pergunte se o crédito de diagramação é do próprio usuário e com qual cargo. Não preencha nome nem cargo de memória, nem copie de outro documento sem o usuário confirmar.

Pergunte também se a publicação leva a ficha do documento no pé do expediente (`.ex-ficha`): autoria institucional, unidade, título, local e ano, palavras-chave numeradas. É a ficha que os manuais da UPD trazem na página 3. Sem resposta, apague o bloco.

## 4. Cabeçalho e rodapé

| Pergunta | Onde entra |
|---|---|
| Qual nome curto aparece no topo de cada página? | `<meta name="vl-peca">` |
| Qual unidade aparece no rodapé? | `<meta name="vl-unidade">`, à esquerda da paginação |
| O rodapé leva um número de referência (ofício, processo)? | `vl-processo` e `vl-rodape-rotulo`, no lugar da unidade |

## 5. Sumário

Pergunte se quer sumário e até que nível (partes e seções, ou só partes). O texto do corpo precisa ter título em cada nível. Se o texto de origem não tem a numeração escrita, ofereça `converter --numerar`.

## 6. Contracapa

Pergunte, com a opção "nenhuma contracapa" à vista, e depois o que entra. Cada item é opcional:

- unidade responsável;
- telefone, e-mail, site e endereço com CEP;
- versão, data, tiragem, ISSN ou ISBN, ou condição de reprodução do conteúdo, numa nota pequena.

Item sem resposta não entra: apague a linha do modelo em vez de deixar o marcador. A contracapa leva sempre o logo horizontal branco.

## 7. Conteúdo especial

Se o texto pede quadro de modelo de documento, glossário, tabela de prazos, linha do tempo ou gráfico, confirme quais e use os componentes de `componentes.md`. Para "caixa de síntese" e "caixa de atenção", pergunte se o usuário quer que a skill proponha o texto (redação nova, a conferir) ou se ele já tem.

## 8. Fecho

Antes de compilar, repita em três linhas o que será feito (modelo, capa, o que entra no expediente e na contracapa) e só então rode o build, se o usuário não tiver dito que dispensa a conferência.
