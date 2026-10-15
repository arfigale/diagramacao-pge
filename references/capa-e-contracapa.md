# Capa e contracapa

## Três capas possíveis

| Capa | Quando | Como |
|---|---|---|
| **Composta com faixa padrão** | o usuário não tem arte | já vem no modelo; o SVG `assets/design-system/faixa-padrao.svg` é a faixa |
| **Composta com faixa do usuário** | o usuário anexou uma imagem de grafismo | `imagem faixa`, depois trocar o `<img>` da faixa |
| **Imagem de página inteira** | o usuário anexou uma capa completa, já aprovada | `imagem pagina`; nada é desenhado por cima |

A capa composta tem, de cima para baixo, o logo e o nome do órgão, a faixa de grafismo (210 mm de largura por 71 mm), o campo marinho com a linha pequena, o título, o subtítulo e o descritor, e o mês e o ano no pé. O título e o logo são sempre HTML, nunca parte da imagem.

## Receber e preparar a imagem

A skill não gera imagem. Quando o usuário anexar um arquivo:

```bash
<dpge> imagem inspecionar arte.png
<dpge> imagem faixa  arte.png --saida capa-faixa.png    # grafismo
<dpge> imagem pagina arte.png --saida capa-pagina.png   # capa completa
```

`inspecionar` informa tamanho, proporção, o que a imagem comporta como faixa e como página, quanto perde no recorte e a resolução em 210 mm. Abaixo de uns 150 dpi a arte sai com pouca nitidez no papel; peça arquivo maior. `faixa` e `pagina` recortam na proporção do uso, sem deformar, e dizem quanto da imagem se perdeu; acima de um terço, tente `--foco topo|base|esquerda|direita` ou `--foco 0.3,0.5` (posição x,y de 0 a 1), ou peça outra arte. Mostre o resultado ao usuário antes de seguir.

Depois, no `documento.html`:

```html
<img class="cm-arcadas" src="capa-faixa.png" alt="">
```

no lugar do `<img ... faixa-padrao.svg>`, e para a capa de página inteira, no lugar de toda a seção `capa-manual`:

```html
<section class="capa-manual capa-img">
  <img src="capa-pagina.png" alt="Título do documento, órgão e ano">
</section>
```

O texto alternativo repete o que está escrito na arte.

### O que olhar na imagem

- **Texto ou logo desenhado dentro da arte** não serve em faixa: acento sai errado e o símbolo da PGE sai fora do padrão (um ponto azul a mais sob a diagonal, por exemplo). Só a capa completa aprovada pode trazer texto, e então vale como foi entregue.
- **Cores.** A arte deve conversar com marinho `#152B3F`, azul `#366586`, verde-água `#51A8B1`, cinza `#D2D3D5` e, só em pontos, laranja `#F58634`. Se fugir muito, avise; a decisão é do usuário.
- **Zona calma.** Na faixa, o título fica abaixo dela, então a arte pode ser densa. Na capa de página inteira, ela mesma carrega o título.

### Quando o usuário não tem arte

Ofereça duas saídas: usar a faixa padrão (documento pronto agora) ou gerar uma arte em outra ferramenta e anexar depois. Para a segunda, entregue este pedido pronto, ajustando o tema do documento:

> Ilustração vetorial plana, faixa horizontal de proporção 2,94 para 1 (2480 x 843 px), fundo branco. Composição leve, com elementos concentrados à esquerda e ao centro, sobre o tema: [tema do documento, em uma frase concreta]. Paleta restrita: azul-marinho #152B3F, azul #366586, verde-água #51A8B1, cinza claro #D2D3D5 e, só em pequenos pontos, laranja #F58634. Estilo geométrico e limpo, formas arredondadas, linhas finas. Sem nenhum texto, sem letras, sem números, sem logotipo e sem brasão.

Para capa de página inteira, troque a proporção por A4 retrato (1985 x 2808 px), diga em que parte da página ficam o título e o logo (sempre uma zona calma) e explique que o título e o logo serão sobrepostos depois, com texto, por isso a arte não pode trazê-los. Capa que sai da ferramenta já com título escrito costuma errar o acento.

## Contracapa

Espelho da capa. Topo claro com o logo e o nome do órgão, a mesma faixa (ou nenhuma), miolo com blocos opcionais e base marinho com o filete laranja e o nome do órgão. Blocos do miolo (`.cc-bloco`): **Como citar**, **Contato**, **Uso do conteúdo**. A base (`.cc-base`) leva o nome do órgão, o site (`.cc-site`) e uma nota pequena (`.cc-nota`) para versão, data, tiragem ou ISSN.

Regras:

- Cada bloco é opcional. Apague o que o usuário não informou; não deixe marcador nem linha vazia.
- Sem site, apague `.cc-site`. A base nunca fica sem o nome do órgão.
- A contracapa se identifica pela classe `contracapa` e vai no fim do `<body>`. O build a imprime em página inteira, sem cabeçalho e sem número, depois do corpo.
- Para a faixa igual à da capa, repita o mesmo `<img>`. Para contracapa mais limpa, apague a faixa.
- Texto em preto e justificado à esquerda; a medida do miolo é de 120 mm para a linha não ficar longa.
- Conferir no PDF: a base encosta no pé da folha e o filete laranja marca o topo dela.

## Cuidados com a gráfica

A capa e a contracapa sangram (a cor vai até a borda). Para impressão profissional, combine com a gráfica a sangria e o perfil de cor; este PDF é feito para tela e para impressão de escritório. O arquivo sai em A4 (210 x 297 mm).
