# Guia de tipografia

Guia de consulta para montar e revisar publicações institucionais (manual,
cartilha, apostila, relatório, ofício) compostas com este design system.

> **Nota da skill.** As regras de composição (fonte, corpo, entrelinha, medida, espaço não separável, caracteres, títulos, quebra) valem para qualquer documento da skill. Trechos sobre peça processual, protocolo e RTF são herança e não se aplicam aqui. Nos caminhos, `design-system/` é `assets/design-system/`.

A base é **Matthew Butterick, _Typography for Lawyers_ (Jones McClure, 2011)**.
O livro é escrito para o processo civil americano e para Word; o que segue é a
regra dele traduzida para português do Brasil, para peça brasileira e para o
nosso pipeline HTML → Chrome → PDF. Onde a nossa escolha contraria o livro, o
motivo está registrado na §9.

Cada regra vem com três coisas: o que fazer, por que, e onde isso já está (ou
não está) resolvido no CSS. O que dá para verificar por máquina está no
`scripts/dpge.py checar`.

---

## 1. A premissa

Não existe "tipografia jurídica". Existe tipografia. Peça processual é material
publicado profissionalmente e responde ao mesmo padrão de um livro ou de uma
revista. Boa parte do que se toma por praxe forense é herança de máquina de
escrever: sublinhado, fonte monoespaçada, dois espaços depois do ponto, entrelinha
dupla, filete feito de parênteses empilhados. Nada disso é exigência de norma.

O critério de qualidade é utilitário, não estético. Tipografia boa é a que
reforça o objetivo do texto. Numa peça o objetivo é duplo: dizer ao juízo o que
se pede e convencê-lo de que se tem direito ao que se pede. Layout que não
serve a esses dois objetivos falhou, ainda que seja bonito.

O recurso escasso é a atenção do leitor. O leitor de um documento institucional
não separou a tarde para lê-lo: ele é um item numa fila de centenas. Tudo que faz o
leitor gastar atenção na mecânica da leitura é atenção que não sobra para o
argumento.

Consequência prática para quem monta modelo: **peça que respeita a norma pode
ser legível**. A norma processual fixa mínimos e máximos ("no mínimo", "no
máximo"); ela quase nunca elimina a escolha. Quando a norma manda usar corpo 12,
usa-se 12 e não mais. Quando ela permite margem "de no mínimo" tanto, a folga
acima do mínimo é nossa e deve ser usada para encurtar a linha.

---

## 2. As quatro decisões que definem a página

Nesta ordem, e antes de qualquer outra coisa: **fonte, corpo, entrelinha e
medida da linha**. Como há mais texto corrido do que qualquer outro elemento, o
corpo do texto é que dá a aparência do documento. Definir capa, caixa e gráfico
antes disso é decorar uma casa sem parede.

Os números do nosso design system, medidos em peça compilada:

| Decisão | Nosso valor | Faixa do livro | Situação |
|---|---|---|---|
| Fonte | Montserrat (sans serif geométrica) | recomenda serifada | divergência medida, §9 |
| Corpo | 12 pt | 10–12 pt em impresso | no teto da faixa |
| Entrelinha | 1,22 (122% do corpo) | 120–145% | dentro |
| Medida da linha | 160 mm, **72 caracteres** | 45–90 caracteres | meio da faixa |
| Espaço entre parágrafos | 3 mm (8,5 pt) | 4–10 pt | dentro |

O corpo é uma régua inteira, não um número solto: os oito tokens `--t-*` do
`tokens.css` guardam a proporção entre corpo, seção, citação, rótulo e apoio, e o
fator `--k` multiplica os 23 tamanhos que só fazem sentido dentro do componente.
`build.py --corpo` reescreve os dois. Mexer só no `--t-corpo` desmontaria a
hierarquia, contra a máxima nº 1 (decidir o corpo primeiro) e a nº 6 (relacionar
cada elemento aos que já existem).

A medida da linha foi medida, não estimada: só as linhas cheias de PDFs
já compostos. Com os 165 mm anteriores dava média de 83 caracteres,
encostada no limite; com os 160 mm atuais fica em torno de 80. Linha mais curta é
mais confortável porque o olho percorre menos distância para achar o começo da
linha seguinte.

**Corpo menor pede margem maior, não menor.** Se o corpo cair, a margem tem de
crescer junto, senão a linha estoura os 90 caracteres.

O corpo subiu de 10,8 para 12 pt, e a linha caiu de 83 para 72 caracteres, o
meio da faixa. O custo é página: em peças de 6 a 7 páginas, o corpo maior
acrescentou cerca de uma. A entrelinha 1,22 paga parte da conta, porque
**entrelinha mexe no tamanho do documento mais que corpo de fonte**: a 1,30 o
documento ganhava mais uma página.

O outro custo é quebra. Bloco indivisível cresce junto com o corpo e passa a não
caber no pé da página, e cada vez que isso acontece abre buraco na página
anterior. Foi o que fez uma linha do tempo abrir 116 mm; a correção não
foi diminuir o corpo, foi deixar a linha do tempo partir entre marcos (§5.8).

Um detalhe de alavancagem: **entrelinha muda o tamanho do documento muito mais
que corpo da fonte**. Quando a peça precisa perder uma página, o primeiro botão
é a entrelinha, não a fonte.

---

## 3. Composição: os caracteres

### 3.1 Espaço não separável é a regra que mais nos custa

Marcador de referência nunca fica separado do número que ele governa. Depois de
`§`, `art.`, `n.`, `inc.`, `fls.`, `R$`, `Lei`, `Tema`, `Súmula`, `Ex.`, `Fig.`
e `©` entra espaço não separável (`&nbsp;`), que tem a mesma largura do espaço
comum e funciona como cola.

Sem isso o navegador quebra a linha ali, porque para ele espaço é lugar seguro de
quebra. Errado:

```
O prazo do art.
1.003 do CPC
```

Isto não é hipótese. Em PDFs compostos sem esse cuidado aparecem dezenas de
linhas que terminam em marcador órfão (`art.`, `n.`, `§`, `Lei`, `Tema`,
`Súmula`, `R$`): uma linha composta só de `n.`, ou uma só com `Lei` e a seguinte
só com `n.`.

Regra de escrita, então: **ao escrever `art.`, `n.`, `§` e companhia, o espaço
seguinte é `&nbsp;`**. O `dpge.py checar` acusa o que passar e o
`--corrigir` insere.

Duas consequências que já morderam, e que valem para qualquer script novo:

- **Script que compara texto do HTML com texto do PDF tem de resolver as
  entidades primeiro.** O `preencher_sumario.py` normalizava o título para
  comparar e transformava `&nbsp;` nas letras `nbsp`: "Lei&nbsp;n." virava
  "leinbspn" e nunca casava com o PDF. Um `html.unescape()` resolve.
- **Em Python, `\s` casa com U+00A0.** Um padrão que procure "marcador seguido
  de espaço comum" e use `\s` volta a acusar o que já foi corrigido. A classe
  certa é `[ \t\r\n]`.

E dois limites do que dá para colar: entre o marcador e o número só pode haver
tag inline. `<dt>Processo n.</dt>` com o número no `<dd>` ao lado está em outra
célula da grade, nunca cai na mesma linha, e não há `&nbsp;` que sirva.

Duas ressalvas. Em referência longa e sem espaço interno o `&nbsp;` cria um
bloco inquebrável grande e piora a justificação; nesse caso deixa quebrar. E
quando o marcador abre a frase, escreve-se a palavra inteira: "O artigo 5º
prevê", não "O art. 5º prevê" no começo do período.

### 3.2 Aspas curvas, sempre

Aspas retas (`"` e `'`) são herança de máquina de escrever, onde as duas vagas
economizadas valiam mais que o desenho correto. Em peça usa-se `“ ” ‘ ’`.
O apóstrofo aponta sempre para baixo (`’`).

Aspas retas no corpo vêm de texto colado de `.docx` e de e-mail. Colou texto de
fora, converte antes de compor (`checar --corrigir`).

Aspas não servem para dar ênfase.

### 3.3 Travessão, meia-risca e hífen são três coisas

| Sinal | Nome | Uso |
|---|---|---|
| `-` | hífen | palavra composta, adjetivo composto, nome de norma com parte múltipla (`Lei n. 13.105-A`, `art. 19-Q`) |
| `–` | meia-risca (en dash) | intervalo e par contrastante: `fls. 12–19`, `2020–2024`, `arts. 5º–7º`, `Sarbanes–Oxley` |
| `—` | travessão (em dash) | pausa forte no meio da frase |

Nunca aproximar com `--` ou `---`.

O intervalo é onde mais erramos: hoje há 5 meia-riscas em todo o repositório, e
intervalo de folhas e de exercício aparece com hífen. Cuidado com o caso
inverso, que é frequente em citação de norma: `art. 19-Q` e `Tema 1.033` levam
hífen, porque é o nome de um dispositivo só, não um intervalo.

Sobre o travessão há um conflito deliberado. O livro defende o travessão e diz
que ele é subutilizado em texto jurídico. **A norma da casa proíbe travessão
para dar ênfase** (`pauta/normas_escrita.md`), e a norma da casa prevalece. A
meia-risca em intervalo não é ênfase e continua obrigatória.

### 3.4 Reticência

Uma reticência (`…`), não três pontos (`...`) e muito menos três pontos com
espaço (`. . .`). Três pontos separados dão ao navegador três lugares de quebra
e a supressão se parte no fim da linha. Se a supressão precisar de espaço de um
lado só, esse espaço é `&nbsp;`.

Exceção: **`[...]` entre colchetes**, que é a convenção brasileira de supressão
dentro de citação, fica como está. O colchete já indica intervenção de quem
cita, e a forma é reconhecida em juízo. O checador não acusa `[...]`, só o `...`
solto.

### 3.5 Ordinais em português

O ordinal masculino é `º` (U+00BA) e o feminino é `ª` (U+00AA). Não é `o`
sobrescrito, não é `<sup>o</sup>`, e não é o sinal de grau `°` (U+00B0), que é
outro caractere e sai com desenho diferente. Sobrescrito em citação é
proibido em manual de citação e fica ilegível em corpo pequeno.

Estado atual: 258 `º` e 11 `ª` corretos, zero uso do sinal de grau, zero
`<sup>`. Este ponto está resolvido; o checador só guarda a porta.

### 3.6 `n.` ou `nº`, escolha uma

Hoje conviverem as duas formas nas peças (108 `n.` contra 63 `nº`) é
inconsistência visível. O rodapé do `build.py` já rotula `Processo n.`, e o
padrão da PGE nas peças é `n.` seguido de `&nbsp;`. **`n.` é a forma da casa.**

### 3.7 Um espaço, nunca dois

Um espaço depois de qualquer pontuação. Dois espaços é convenção de fonte
monoespaçada e, em fonte proporcional, abre rios de branco na página. Em HTML o
espaço duplo colapsa e não faz dano visual, mas atravessa para o RTF, onde faz.

### 3.8 Branco é caractere, e cada um tem função

Não usar espaço, `<br>` ou parágrafo vazio como dispensador genérico de branco.
Espaço serve para separar palavra. Espaço vertical vem de margem no CSS.
Quebra de linha dentro do mesmo bloco (endereço, bloco de assinatura, título que
precisa quebrar em ponto lógico) é `<br>`. Quebra de página é
`.quebra-antes`, nunca uma sequência de parágrafos vazios: à primeira edição do
texto o vão migra para o meio da página e ninguém entende por quê.

Não preencher o resto da página com barras (`/ /`) antes de uma quebra. É ritual
obsoleto e dá retrabalho a cada reflow.

### 3.9 Símbolos de verdade

`©` e não `(c)`; `×` e não `x` em multiplicação e em dimensão (`1122 × 1402`);
`−` (menos) e não hífen em expressão negativa. Sinal de pé e polegada, se
aparecer, é aspa reta, não curva.

---

## 4. Formatação de texto

### 4.1 Nunca sublinhar

Não há exceção em documento impresso. Sublinhado é contorno de máquina de
escrever, que não tinha negrito nem itálico. Ele corta as descendentes das
letras e piora a leitura. Onde daria vontade de sublinhar, usa-se negrito, ou
itálico, ou mudança pequena de corpo.

O `componentes.css` não tem nenhum `text-decoration: underline`. Manter assim.
Cuidado ao colar HTML de fora, que traz `<u>`.

### 4.2 Negrito **ou** itálico, e o mínimo possível

Os dois são ferramenta de ênfase e mutuamente exclusivos: negrito itálico, ou
negrito sublinhado, é escalada de ênfase que não leva a lugar nenhum. Se tudo
está enfatizado, nada está, e não sobra recurso para a palavra que realmente
precisa.

Em fonte sans serif, como a nossa, **a ênfase é o negrito**. O itálico de sans
serif é só uma inclinação suave e não se destaca na página; o de fonte serifada
muda o desenho da letra e por isso funciona. Consequência para nós: itálico fica
reservado para o que ele marca por convenção (título de obra, expressão em
língua estrangeira, nome de julgado quando o padrão de citação pedir), e não
para dar ênfase.

Parágrafo inteiro em negrito é o vício do superenfatizador. Não fazemos.

### 4.3 Caixa alta só em rótulo curto

Letra maiúscula é mais difícil de ler em corpo de texto. As minúsculas têm
altura variada, algumas altas, algumas baixas, algumas descendentes, e esse
contorno irregular ajuda o cérebro a reconhecer a palavra. Caixa alta achata
tudo num retângulo.

Onde cabe: rótulo com menos de uma linha, cabeçalho, rodapé, legenda de tabela,
tarja de categoria. Onde não cabe: frase, título de seção com mais de uma linha,
e sobretudo parágrafo inteiro.

Parágrafo em caixa alta é tipografia que se autodestrói: usa-se justamente onde
se quer atenção máxima, e o efeito é o leitor pular o trecho. Para destacar
parágrafo há caixa com filete, rótulo "Em síntese", corpo um pouco maior.

É defeito conhecido dos rótulos dos números-chave da capa. A regra completa é esta.

Um detalhe de citação: em texto em caixa alta, não maiúscula a letra da alínea,
que muda o sentido da referência. `ART. 8º, IX` sim; a alínea `a)` continua
minúscula.

### 4.4 Caixa alta e versalete pedem entreletra

Maiúscula é desenhada para ficar ao lado de minúscula, então maiúsculas juntas
ficam apertadas. Acrescenta-se **5% a 12%** de entreletra em caixa alta, e isso
importa mais quanto menor o corpo. Nunca esticar até caber outra letra no vão.

No nosso CSS, o teto de 12% está estourado em treze seletores, todos em rótulo
de 7,4 pt ou 6,6 pt, com valores de 0,13em a 0,22em. Abaixo de 9 pt o próprio
livro admite entreletra maior para manter as letras distintas, então isso é
defensável, mas convém um teto explícito:

- corpo ≥ 9 pt em caixa alta: **0,05em a 0,12em**;
- micro-rótulo abaixo de 8 pt: até **0,18em**;
- acima de 0,18em, não.

Havia um defeito real: `.capa-titulo` era caixa alta com entreletra **negativa**
(`-0,01em`, a 23 pt). Apertar caixa alta contraria a regra. Está em `+0,015em`,
no piso da faixa, porque a 23 pt pouco já resolve. Isso mexe só na capa e não
reflui o corpo do texto.

### 4.5 Versalete falso, não

Versalete (small caps) verdadeiro é desenhado com altura e peso calibrados para
conviver com a minúscula. O que `font-variant: small-caps` produz é maiúscula
reduzida por escala: alta demais e com traço fino demais. **Se não há versalete
de verdade na fonte, não se usa versalete.** A Montserrat variável do
repositório não tem, então a regra é simples: `font-variant-caps` não entra no
`componentes.css`. Hoje não está lá. Manter fora.

### 4.6 Kerning ligado, ligadura desligada

Kerning é o ajuste de pares específicos de letras, e vem de fábrica na fonte.
Sempre ligado. Ligadura resolvia colisão física de tipo de metal e hoje só é
necessária se `f` e `i` colidirem; em sans serif geométrica não colidem, e a
ligadura dá ar antiquado. Declarar isso explicitamente evita depender do padrão
do motor, sobretudo porque outros motores (o Word, por exemplo) fazem diferente:

```css
body { font-kerning: normal; font-variant-ligatures: no-common-ligatures; }
```

### 4.7 Cor

A regra do livro é categórica: documento impresso para leitura vai em tipo
preto, sem exceções. Cor ele admite em papelaria (timbre, cartão), não em corpo
de texto. **Nós seguimos a regra.**

Isso pede dois papéis de cor, e é assim que o `tokens.css` está montado:

- **`--texto: #000000`** é o texto de leitura: corpo, célula de tabela, item de
  lista, corpo de citação, texto de marco da linha do tempo, dado da ficha.
- **`--marinho: #152B3F`** é a moldura institucional: título, subtítulo, tarja
  da capa, cabeçalho de tabela, assinatura, gráfico.
- **`--acento: #294964`** é o azul médio da estrutura fina: numeração de seção,
  filete, rótulo, marcador.

O caminho até aqui: o corpo era `#294964`, contraste 9,0:1 sobre o off-white.
Escureceu para `#152B3F` (13,8:1) e depois foi a preto (20:1). O `#223141` que
existe como `--marinho-escuro` daria 12,6:1, mas dessatura e lê como grafite.

**Negrito no corpo é preto.** Testar as duas versões deixou claro por quê: o
azul é mais claro que o preto, então colorir o negrito **reduz** o contraste
dele contra o texto ao redor. O negrito passa a pesar menos, não mais, e o
trecho ganha cara de link. É a mesma lógica do "negrito ou itálico, um ou
outro": empilhar dois sinais de ênfase enfraquece os dois.

Um efeito colateral bom de escurecer o marinho: o `--acento` ficou um tom acima
dele. Antes os dois eram o mesmo valor e a numeração de seção não se distinguia
do texto.

Três consequências que valem para nós sem ressalva:

**Fundo cinza médio, não.** Ao copiar ou digitalizar, o cinza escurece e fica
granulado, e o texto por cima perde legibilidade. Os fundos do
`componentes.css` são claríssimos (`#F4F7FA`, `#FFF9F2`), o que é o certo. Novo
componente segue esse patamar.

**Texto branco sobre fundo escuro custa.** Gasta cerca de vinte vezes mais toner
que texto normal e é mais um motivo para o **modo sóbrio, sem capa, ser o padrão
de protocolo**. No modo completo a tarja marinho é intencional e fica limitada à
capa.

**Marca d'água, não.** Rótulo diagonal gigante atravessando o texto cria ruído e
escurece na cópia. "Minuta" e "Confidencial" vão para o cabeçalho ou para o
rodapé.

---

## 5. Layout da página

### 5.1 Recuo de primeira linha **ou** espaço entre parágrafos

Os dois marcam o início do parágrafo. São cinto e suspensório: um resolve, os
dois juntos é erro.

**Documento institucional** usa espaço entre parágrafos e nenhum recuo. (Peça
processual usa recuo de 1,5 cm, por convenção do foro; fora do escopo desta skill.)

Isso deixa a peça com os dois — recuo *e* espaço entre parágrafos — o que o
livro chama de erro. É uma divergência consciente, registrada na seção 9: num
documento que será impresso, grampeado e folheado por terceiros, o espaço entre
parágrafos é o que permite retomar a leitura depois de uma interrupção, e o
recuo é o que faz o documento *parecer* peça. Perder qualquer um dos dois custa
mais do que a incoerência custa.

O recuo se liga sozinho: `<meta name="vl-tipo" content="peca">` faz o
`build.py` pôr `doc-peca` no `<body>`, e é a classe que define
`--recuo-corpo`. Fora dela a variável não existe, `text-indent: var(--recuo-corpo)`
cai como declaração inválida, e o recuo é zero. Não há segunda regra para
esquecer de manter em dia.

Lista e citação recuam o **bloco** inteiro, 1 cm além do recuo do corpo
(`--recuo-bloco`, 2,5 cm) — o item não se alinha à primeira linha do parágrafo,
fica depois dela.

### 5.2 Margem e assimetria

Uma polegada não basta em fonte proporcional. Em A4 nossas margens são 25 mm à
esquerda e 20 mm à direita, 31 mm no topo e 19 mm no pé.

As laterais eram 25 mm e 20 mm, e o problema não era o tamanho, era a
assimetria: **5 mm de diferença entre esquerda e direita lê como erro de
composição, não como escolha.** Layout assimétrico precisa de diferença grande e
evidente, da ordem de 25 mm; abaixo disso, o certo é igualar. Como a peça circula
em PDF e não é encadernada, não há margem de lombada para justificar a folga.
Foram igualadas em 25 mm, o que também encurtou a linha de 83 para cerca de 80
caracteres.

Mexer nisso é mexer em dois lugares, porque a medida não vive só no CSS:
`MARGENS` no `build.py` e a largura útil usada nas medições.

Topo maior que pé é justificado aqui, porque o cabeçalho ocupa o topo. A regra
ótica clássica (pé cerca de 6 mm maior que topo, senão o bloco de texto parece
escorregar) vale para o bloco de texto depois de descontado o cabeçalho, não para
a folha crua.

Não temer o branco. A folha A4 é uma convenção histórica, não uma medida
projetada para leitura. Nenhuma revista do tamanho de uma A4 roda texto em bloco
único com margem de uma polegada; ou usa coluna, ou divide a página. Trabalhar
do texto para fora, não da borda para dentro: se o texto está bom, o branco se
resolve.

### 5.3 Justificado, e sem hifenização no corpo

O livro é categórico: texto justificado **exige** hifenização, senão o vão entre
palavras fica enorme. Aqui a decisão é outra, e é editorial: **hifenização
desligada no corpo**, porque palavra partida no fim da linha incomoda mais na
leitura da peça do que o vão que ela evita.

```css
body { text-align: justify; hyphens: none; }
.tese-texto, .precedente p { hyphens: auto; }
```

**Citação em bloco é a exceção e pede hifenização.** Ali a medida já é mais
curta por causa do recuo, e menos espaço por linha significa menos ponto possível
de quebra, que é exatamente a condição em que a hifenização passa de opcional a
necessária.

**Ressalva importante, medida e não suposta: `hyphens: auto` nunca funcionou
neste pipeline.** O Chromium do Playwright não traz os dicionários de
hifenização (no Chrome de mesa eles vêm por atualização de componente, não no
binário), então a regra era inerte. A prova: o manual compilado com
`hyphens: auto` e com `hyphens: none` sai com as mesmas 2.636 linhas e as mesmas
5 linhas terminadas em hífen, que são hífens de palavra composta. O RTF vai no
mesmo caminho em outros programas, que também não ligam a hifenização automática.

Consequências práticas:

- **Nada compilado com esta skill é hifenizado.** Desligar a
  hifenização não muda nada na página; só torna o CSS honesto sobre o que
  acontece.
- A declaração nas citações fica no CSS por intenção e para o dia em que o motor
  tiver dicionário, mas **hoje não produz efeito**. Não contar com ela.
- Quando uma palavra específica precisar quebrar, a ferramenta que funciona é o
  **hífen opcional** (`&shy;`), que marca à mão o ponto de quebra e é invisível
  enquanto não for usado. É o mesmo recurso que o livro chama de _optional
  hyphen_, e serve para nome próprio comprido, termo técnico e palavra que o
  motor quebraria mal.
- `<html lang="pt-BR">` continua no checklist, porque governa também a
  separação de sílabas de um motor futuro, a busca no PDF e o leitor de tela.

O preço vem em vão de justificação, e há uma válvula de escape: **se um parágrafo
abrir rio de branco visível no `_conferencia/*.png`, alinhar aquele bloco à
esquerda.** Justificar é preferência, não sinal de profissionalismo, e o próprio
autor prefere alinhar à esquerda justamente porque o motor de justificação de
navegador é rústico. O que não se faz é religar a hifenização do corpo.

### 5.4 Citação em bloco

Corpo e entrelinha ligeiramente menores, recuo de 12 a 25 mm à esquerda (e
opcionalmente à direita), **sem aspas nas pontas**, porque o recuo já diz que é
citação. Espaço antes e depois para o bloco parecer alinhado verticalmente.

O conteúdo importa mais que a forma: citação longa comunica ao leitor "não
escrevi nada disto" e convida a pular. Ementa que precisa ser lida entra editada
e integrada ao texto.

### 5.5 Listas

Lista é elemento automático, com marcador vindo do CSS, nunca marcador digitado
à mão no começo da linha. Marcador vazado é mais discreto que marcador cheio;
asterisco não serve, por ser pequeno e alto demais. Marcador grande demais
compete com o texto.

Cabe usar cor e peso diferentes no índice da lista (é o que as letras dos
pedidos fazem: `a)` em negrito na cor da marca). O que não cabe é fundo colorido
atrás do marcador, e isso já está registrado como armadilha de RTF: fundo de run
cobre a altura da linha inteira e vira retângulo desalinhado no Word.

### 5.6 Tabela

Tabela é a ferramenta certa para grade de dados e para qualquer layout em que
elementos precisam ficar lado a lado. Dois defeitos de padrão a corrigir sempre:

**Borda.** Começar com todas as bordas desligadas e religar só as necessárias. O
texto das células já cria uma grade implícita; borda em toda célula transforma
a tabela em ruído. É o `chartjunk` de Tufte.

**Margem interna.** O padrão é sempre apertado, e aumentar o `padding` é a
maneira mais eficiente de melhorar a leitura de uma tabela densa. Um pouco
resolve muito: partir de 0,8 mm e subir de 0,25 em 0,25. Não precisa ser igual
nos quatro lados; em cima e embaixo pode ser maior que nas laterais.

**Coluna de número usa algarismo tabular.** `font-variant-numeric: tabular-nums`
faz os dígitos terem a mesma largura e as colunas alinharem. Já está aplicado
em `.numeros`, `.ficha dd .num` e alguns outros pontos; **toda célula numérica
nova precisa dele**.

`thead { display: table-header-group }` já repete o cabeçalho na página
seguinte.

### 5.7 Filete e moldura, pouco

Antes de traçar um filete, perguntar se mais branco não resolve. Costuma
resolver.

Espessura de moldura entre **0,5 e 1 pt**. Mais fino que isso não reproduz em
impressora de escritório; mais grosso cria ruído que rouba a atenção do dado que
a moldura devia emoldurar. Os nossos 0,3 mm e 0,35 mm dão 0,85 pt e 0,99 pt, na
faixa. Filete solto (não moldura) tem mais liberdade, porque não acumula, e é
o que justifica os 1,2 mm e 1,4 mm decorativos da capa e das caixas.

Nada de moldura pontilhada, tracejada ou dupla. E nada de filete feito de
caractere repetido: `-----`, `_____` ou parênteses empilhados.

Filete de título vai **acima** do título, não abaixo. Acima ele separa o fim da
seção anterior do título novo; abaixo ele separa o título do próprio texto que
ele anuncia, o que é o contrário do que se quer.

### 5.8 Viúva, órfã e o buraco no pé da página

Órfã é a primeira linha do parágrafo sozinha no pé da página; viúva é a última
linha sozinha no topo da seguinte. Controlar as duas move linhas entre páginas e
**por isso abre vão no pé**. Isso é normal, é o preço do controle, e explica
metade dos buracos que o `checar` aponta.

O livro é pragmático: só ligar o controle quando viúva e órfã estiverem causando
problema visível, porque o vão no pé costuma incomodar mais que a linha solta.
Nossa configuração é `orphans: 2; widows: 2`, e o comentário no CSS registra por
que não é 3 (com 3, um título de subseção no pé empurrava o parágrafo inteiro e
abria quase 3 cm). Está calibrado. Não subir sem medir.

**A caixa de citação não começa partida.** `.precedente` é `break-inside: avoid`,
e a razão é um defeito que o `auto` produzia: o motor abria a caixa — filete,
fundo e 5 mm de padding — no que restava da página, o parágrafo indivisível
migrava inteiro, e sobrava uma **barra colorida sem uma linha de texto** no pé.
Com `avoid`, a caixa que não cabe migra inteira.

O preço disso é o buraco, e o remédio tem nome: **`.partivel`** na caixa. Ela
libera a quebra na caixa *e* no parágrafo, que é o ponto — liberar só a caixa
devolve o fragmento vazio. Use quando a ementa passar de umas dez linhas: abaixo
disso o pior buraco que ela abre fica em torno de um quinto da página, e migrar
é mais limpo que partir. Ementa atravessando a quebra é normal em peça; meia
página em branco não é. O `dpge.py checar` mede o buraco e sugere a classe
quando o bloco que não caiu é alto.

**Bloco grande parte entre itens.** Travar inteiro um quadro de requisitos ou
uma linha do tempo de 140 mm garante que ele raramente caiba no pé da página, e
cada vez que não cabe ele migra inteiro e deixa o buraco atrás. A regra geral:
**o que é indivisível é o item, não a coleção de itens.** Hoje partem entre
itens o quadro de requisitos (entre linhas), a linha do tempo (entre marcos), a
ementa (entre parágrafos) e as tabelas `dados` e `criterios` (entre linhas, com
o cabeçalho repetido por `table-header-group`). Em todas, o item continua
indivisível. Tabela pequena que precise ficar inteira leva `.nao-quebrar`, e a
classe tem par com `table.dados`/`table.criterios` no CSS, senão perde por
especificidade e a tabela quebra do mesmo jeito.

Confirmado por teste que o Chrome fragmenta grid na impressão, então
`display: grid` não é obstáculo. O que sobra de buraco depois disso é **um item
mais alto que a sobra da página**, e aí a saída não é mais de CSS: é enxugar o
texto da célula ou reordenar. É a ordem a seguir.

**Folga antes de título não é buraco.** Quando a página termina e a seguinte
abre com um título, a folga é o `break-after: avoid` funcionando: sem ela o
título ficaria órfão no pé. Somando a margem superior do título, o filete e as
duas linhas que o `orphans: 2` arrasta, dá uns 30 mm de folga esperada. Medir
folga sem essa distinção acusa como defeito o que é o comportamento correto.

Título é caso diferente e não tem meio-termo: **título sempre com `break-after:
avoid`** (não fica órfão no pé, sem o texto que anuncia) e, se tiver duas
linhas, `break-inside: avoid`. Isso já está no `componentes.css`.

Bloco de assinatura viaja inteiro: linhas unidas por `<br>` dentro de um
parágrafo só, com `break-inside: avoid`. Assinatura partida em duas páginas é
defeito visível em peça assinada.

Linha de assinatura se faz com sequência de sublinhados (`____`), não com espaços
sublinhados: espaço sublinhado desaparece quando alguém tira o sublinhado do
documento inteiro e se parte quando alguém troca espaço duplo por simples.

### 5.9 Coluna

Duas ou três colunas em A4 funcionam, quatro não. É a maneira mais fácil de
encurtar a linha sem inflar a margem, e cabe em contrato e anexo longo. Para as
linhas alinharem entre colunas, o espaço entre parágrafos tem de ser zero ou
múltiplo exato da entrelinha.

---

## 6. Títulos

Problema de título é primeiro estrutural, depois tipográfico. Resolvido o
estrutural, o tipográfico fica fácil.

**No máximo três níveis, e dois é melhor.** Título é placa de sinalização da
estrutura do argumento, não sumário do documento. Título para cada tópico,
subtópico e sub-subtópico exaure o leitor, e cada nível novo obriga a inventar
outra combinação de negrito, corpo, caixa alta e recuo para diferenciar, o que
produz o empilhamento que se vê nas peças.

**Título é substantivo, não rótulo.** "I. Introdução" não informa nada: o que
vem depois do primeiro título é obviamente a introdução. O que informa é o
conteúdo: "1. Dos fatos", "2. Da tempestividade", e melhor ainda o título que
adianta a tese: "3. O adicional não incide no período vedado pelo art. 8º da LC
n. 173/2020". Quem lê só os títulos deve entender o esqueleto do argumento.

O oposto também é defeito: título que não avança o argumento e só anuncia que ele
virá ("Pelas razões abaixo, o recurso deve ser provido") é obstáculo, não placa.

Tipografia do título, então:

- sem caixa alta se for frase (e título substantivo quase sempre é frase);
- sem sublinhado;
- sem centralizar, salvo convenção local ("PEDIDOS");
- negrito, não itálico, e negrito é opção e não obrigação;
- corpo maior, mas **no menor incremento visível**: de 10,8 pt vai-se a 11,5 ou
  12 pt, não a 14; se o título é negrito, cabe até reduzir meio ponto para
  compensar o peso;
- no máximo dois níveis de recuo, mesmo com três níveis de título. Título que
  perde a âncora na margem esquerda fica flutuando;
- hifenização desligada;
- `break-after: avoid`.

Sobre numeração: numeral romano e romanete são ruins de ler e fáceis de
confundir (`II` e `III`, `IV` e `VI`, `XXI` e `XII`; e quanto é `XLIX`?). Letra
piora depois do `F` (quanto é `T`?). Misturar romano com letra gera referência
ambígua: `i` é o primeiro item ou o nono? O livro propõe numeração em camadas
(`1`, `1.1`, `1.2.3`), que só usa dígito e sempre diz onde se está na
hierarquia. Garner discorda justamente deste ponto no prefácio do livro, e a
praxe forense brasileira usa numeral arábico simples por seção. Nossa peça usa
numeração de seção arábica com o nível dois em `1.1`, o que já é a solução em
camadas. Manter.

---

## 7. Misturar fontes

Misturar não é requisito, é opção, e rende pouco. Uma fonte com variação de
corpo, peso e caixa cobre quase tudo. Segunda fonte, muitos documentos toleram;
terceira, poucos; quarta, nenhum.

Se misturar, cada fonte precisa de papel fixo no documento: uma no corpo e outra
nos títulos; ou uma no centro da página (corpo e títulos) e outra nas bordas
(cabeçalho, rodapé, numeração). Nunca duas fontes no mesmo parágrafo. Não é
verdade que só serifada mistura com sans serif; contraste baixo entre duas
fontes costuma funcionar melhor que contraste alto, e mistura mais segura é
entre fontes do mesmo desenhista.

Para nós isto deixou de ser acadêmico. **Documento institucional é todo
Montserrat.** **Peça processual mistura duas famílias, com papel fixo**, que é
justamente a forma que o livro admite:

| Papel | Família |
|---|---|
| Corpo, título, subtítulo, citação, valor da ficha | Source Serif 4, peso 450 |
| Rótulo, endereçamento, assinatura, cabeçalho de tabela, capa, gráfico | Source Sans 3 |
| Cabeçalho e rodapé da página (fora do CSS, no template do Chrome) | Montserrat |

É a divisão "uma no centro da página, outra nas bordas", com o acréscimo de que
os rótulos — que são etiquetas, não prosa — ficam do lado das bordas. O corpo
serifado é a razão de tudo: a peça é lida em papel, por páginas seguidas, e é
aí que a serifa paga.

O título ficou serifado junto com o corpo. Sans com entreletra larga puxava a
página para apresentação de slides, e a hierarquia do título não vem da família
— vem do caixa-alta, do filete e do corpo maior. A entreletra do `h2` caiu de
0,055em para praticamente zero pelo mesmo motivo.

Peso 450 e não 400: no eixo variável da Source Serif o 400 fica leve demais a
12 pt sobre papel. E o negrito do corpo subiu para 700 porque, na mesma família
e no mesmo corpo, o 600 não se distinguia de um 450.

---

## 7-A. Nota de rodapé

Nota de rodapé sai **no pé da página em que a chamada aparece** — não no fim da
seção, não no fim do documento. Isso não é CSS comum: é `float: footnote`, do
CSS Paged Media, que o Chrome não implementa. Quem implementa é o polyfill em
`design-system/vendor/paged.min.js`, e o `build.py` o carrega **só quando o
documento tem `.nota-rodape`** — ele repagina o documento inteiro no DOM, e não
vale correr esse risco onde não resolve nada.

```html
<p>O prazo é de quinze dias<span class="nota-rodape">Art. 183 do CPC, com a
prerrogativa de prazo em dobro.</span> contados da intimação.</p>
```

A chamada nasce sozinha, numerada por **ordem de ocorrência no texto**. Escreva
a nota onde a chamada deve aparecer; ela é movida para o pé pelo paginador.

Três coisas que custam caro se esquecidas:

- **A classe é `.nota-rodape`, não `.nota`.** `.nota` já é caixa de nota
  explicativa no fluxo do texto, em uso no manual da Lei do Processo
  Administrativo. Aplicar `float: footnote` naquela classe arrancaria as caixas
  do texto e as despejaria no rodapé, sem erro e sem aviso.
- **Não combina com `vl-capa: propria`.** A capa imprime numa segunda passada,
  com margem zero, e o paginador já compôs as páginas com a margem do `@page`.
  O build recusa a combinação em vez de entregar a capa fora de esquadro.
- **Se o polyfill falhar, o build falha.** É deliberado: sem ele o navegador
  ignora a declaração e o texto da nota sai **dentro do parágrafo**, no meio da
  frase — um PDF errado com cara de certo, que ninguém revisando por cima
  percebe. Não gerar nada é o desfecho seguro.

## 8. As máximas de layout

As nove máximas do livro, na ordem dele, que servem de régua final:

1. **Decidir primeiro a aparência do corpo do texto.** É o que há em maior
   quantidade e o que define o documento.
2. **Dividir a página em primeiro e segundo plano.** O corpo do texto é primeiro
   plano; cabeçalho, rodapé, filete e numeração são fundo, e fundo não sobe ao
   palco. Os instrumentos para marcar a diferença são poucos: posição, tamanho,
   fonte e, às vezes, cor.
3. **Ajustar no menor incremento visível.** A diferença entre pouco e demais é
   pequena.
4. **Na dúvida, fazer dos dois jeitos.** Decisão tipográfica não se resolve por
   lógica; imprime-se as duas e olha-se. É o que os `_conferencia/*.png` e o
   comparações lado a lado de entrelinha servem para fazer.
5. **Ser consistente.** O que é igual parece igual; o que parece diferente é
   diferente. Sem isso o documento soa aleatório. É a razão de existir o
   `componentes.css` em vez de estilo caso a caso.
6. **Relacionar cada elemento novo aos que já existem.** Só a página em branco dá
   liberdade total; depois disso é quebra-cabeça.
7. **Manter simples.** Se parece que faltam três cores e cinco fontes, é sinal
   contrário.
8. **Imitar o que se gosta.** Os modelos de `assets/modelos/` e os documentos já
   compilados existem para isso.
9. **Não temer o branco.** Muita tipografia mediana nasce da vontade de
   preencher espaço. Não é preciso ocupar cada centímetro que a norma permite.

---

## 9. Onde divergimos do livro, e por quê

Registrar a divergência importa: divergência decidida é escolha, divergência
esquecida é defeito.

**Sans serif no corpo do texto — encerrada na peça, mantida no documento.**
Desde 10/09/2026 a peça processual compõe em **Source Serif 4**, que é uma das
equivalentes OFL que esta própria seção apontava como saída. O documento
institucional segue em Montserrat. A identidade não se perde: ela passou a viver
onde o livro admite cor e marca — rótulo, endereçamento, capa, cabeçalho e
rodapé —, e é isso que a §7 chama de "uma no centro da página, outra nas bordas".

Fica registrado o que **não** foi medido. A troca veio de decisão do operador,
não de uma repetição do teste comparativo abaixo, e a Source Serif 4 nunca
entrou naquela tabela. O que se mediu na troca foi menos que isso: recompilando
as peças existentes, a contagem de páginas **não subiu** e a medida da linha ficou dentro da faixa de 45–90
caracteres. A taxa de linhas esticadas além de 2× o espaço — que é o critério em
que a Montserrat ganhou — **não foi remedida**. Quem for rever esta decisão
comece por aí.

O texto abaixo é o teste original, de agosto, e continua valendo para o que ele
de fato comparou: seis serifadas da Microsoft contra a Montserrat.

A mitigação da §4.2 continua de pé: a ênfase é o negrito, e o itálico fica
restrito ao uso convencional.

Isto foi testado, não presumido. Seis serifadas da lista A do livro que existem
no Windows (Palatino Linotype, Calisto MT, Century Schoolbook, Garamond, Goudy
Old Style, Bell MT) foram compiladas na mesma peça, **na mesma medida ótica** —
que é o método do livro, porque duas fontes no mesmo corpo nominal não têm o
mesmo tamanho aparente. A diferença é grande: para dar os mesmos 72 caracteres
por linha, a Montserrat precisa de 12 pt e a Garamond de 16 pt.

Igualada a medida, a Montserrat ganhou nos dois critérios que importam aqui:

| | páginas | linhas esticadas além de 2× o espaço |
|---|---|---|
| Montserrat 12 | 8 | 27% |
| Century Schoolbook 13 | 9 | 44% |
| Palatino Linotype 14 | 9 | 50% |
| Calisto MT 14,5 | 9 | 44% |
| Garamond 16 | 10 | 49% |

A vantagem na justificação é consequência direta da nossa própria escolha de não
hifenizar (§5.3): sem hífen, o vão entre palavras é o único ajuste, e as
serifadas testadas esticam mais. A vantagem em página vem de que, na mesma
medida ótica, a serifada precisa de um corpo nominal maior e portanto de mais
altura de linha.

Há ainda um impedimento prático: as seis são fontes da Microsoft, não têm licença
aberta e não poderiam viajar em `design-system/fonts/`. Adotar uma exigiria a
equivalente com licença OFL (EB Garamond, Source Serif 4, Spectral, Literata,
Libre Baskerville) e um novo teste. **A conclusão de agosto era que a divergência
se mantinha, agora por medida e não só por identidade** — e foi exatamente por
esse caminho que ela acabou encerrada: a fonte adotada é a segunda da lista, com
licença OFL, viajando em `design-system/fonts/`. As variantes seguem
reproduzíveis com `build.py --fonte`.

**Cor do corpo: esta divergência foi encerrada.** O corpo era marinho e passou
a ser preto, seguindo a regra do livro. O azul ficou onde o livro admite cor, na
moldura institucional. Ver §4.7. O resto da regra de cor nunca se relaxou: nada
de fundo cinza médio, nada de texto claro sobre escuro fora da capa, nada de
marca d'água.

**Justificado.** O autor não justifica, por preferência e por desconfiança do
motor de justificação de processador de texto. A praxe forense brasileira
justifica, e a nossa peça justifica.

**Justificado e sem hifenizar ao mesmo tempo.** Esta é a divergência mais dura,
porque o livro trata a hifenização como obrigatória em texto justificado, e não
como preferência. A escolha é editorial: palavra partida incomoda mais que vão
largo. As contrapartidas estão na §5.3, e são duas: citação em bloco hifeniza, e
parágrafo que abrir rio de branco vai alinhado à esquerda em vez de hifenizado.
Se o vão se mostrar pior que a palavra partida na conferência visual, o caminho
é alinhar à esquerda o corpo inteiro, não voltar a hifenizar.

**Travessão.** O livro pede mais travessão; a norma da casa proíbe travessão
para ênfase. A norma da casa vence.

---

## 10. Antes de protocolar

Roteiro curto. O que dá para automatizar está no
`scripts/dpge.py checar`; o resto é olho.

**Máquina:**

```bash
python scripts/dpge.py checar documento.html
```

Ele acusa marcador sem `&nbsp;`, aspas retas, `...` no lugar de `…`, `--` no
lugar de travessão, intervalo numérico com hífen, `<u>`, `font-variant:
small-caps`, `<sup>` em ordinal, sinal de grau no lugar de `º`, mistura de `n.`
com `nº`, ausência de `lang="pt-BR"` e, se o PDF já existir, linha terminada em
marcador órfão e medida de linha acima de 90 caracteres.

**Olho, no `_conferencia/*.png`:**

- folga no pé de cada página dentro de ~20 mm (`build.py --conferir` gera as imagens);
- nenhum título órfão no pé, nenhuma assinatura partida;
- vão de justificação sem rio de branco visível;
- caixa alta em rótulo, nunca em frase;
- tabela com margem interna suficiente e sem borda desnecessária;
- coluna de número alinhada (algarismo tabular);
- nome das partes e do signatário conferidos contra o documento de origem, com
  acentuação.

---

## Fonte

Matthew Butterick, _Typography for Lawyers_, Jones McClure Publishing, 2011
(ISBN 978-1-59839-078-0). 

Do próprio livro, o que vale consultar depois: Robert Bringhurst, _The Elements
of Typographic Style_; Ellen Lupton, _Thinking With Type_; Edward Tufte, _The
Visual Display of Quantitative Information_ e _Envisioning Information_.
