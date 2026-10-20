# Capa e contracapa

A capa padrão é a branca do Programa de Integridade 2026 (`padrao-referencia.md`); a azul dos manuais da UPD de 2025 (Guia, Plano e Orientações) é a variante. A contracapa é azul nos dois casos. Cores e logos seguem o manual da marca da PGE; ver `identidade.md`.

## A capa padrão: branca

A capa do Programa de Integridade da PGE/MS (2026), toda em HTML e SVG, sem imagem. De cima para baixo e da esquerda para a direita:

1. fundo branco, com a faixa vertical na borda esquerda (`.cm-lateral`, 14 mm), em azul, verde-água e laranja;
2. logo horizontal azul, no alto, alinhado à coluna do título (`.cm-logo`, arquivo `@ds/logo-pge.png`);
3. bloco do título (`.cm-bloco-branco`): sobretítulo em caixa alta (`.cm-sobretitulo`, o tema ou programa), título em azul-escuro (`.cm-titulo`), filete laranja curto (`.cm-filete`) e o nome do órgão (`.cm-sub`);
4. grafismo no canto inferior direito (`.cm-grafismo`): círculos concêntricos de traço fino, um disco azul-médio com o ícone em branco e um ponto verde-água;
5. ano no pé, à esquerda (`.cm-ano`).

O título e o logo são sempre HTML, nunca parte de imagem. O sobretítulo é opcional: sem ele, apague a linha. Não há faixa laranja horizontal nem edição na capa branca; a edição, se existir, vai no expediente.

### O ícone do grafismo

O modelo traz um documento (folha de canto dobrado com duas linhas de texto), que serve a qualquer documento institucional. É um único `<path>` branco, sem preenchimento, no SVG do modelo, centrado em (165, 244) e com uns 20 mm de largura. Se o tema pedir outro ícone (escudo, balança, livro, cadeado), troque só o atributo `d` desse `<path>` por outro traço simples, mantendo `stroke="#fff"` e `fill="none"`. O ícone acompanha o tema do documento. Os ícones dos contatos da contracapa são outros e não mudam.

## Capas possíveis

| Capa | Quando | Como |
|---|---|---|
| Branca (padrão) | sempre, se o usuário não pedir outra | o modelo já vem assim; preencha sobretítulo, título e ano |
| Azul (variante) | o usuário pedir uma capa azul, como a dos manuais da UPD de 2025 | troque a seção pela marcação `capa-manual` do comentário do modelo; descrição abaixo |
| Azul com arte de fundo | o usuário anexou uma foto ou ilustração e quer a capa azul | `imagem fundo`, e o arquivo entra em `.cm-fundo` da capa azul |
| Imagem de página inteira | o usuário anexou uma capa completa, já aprovada | `imagem pagina`; nada é desenhado por cima |

## A capa azul (variante)

Segue os manuais da UPD de 2025. De cima para baixo:

1. faixa laranja de 6 mm no topo, de borda a borda;
2. campo inteiro no azul da marca (`#294964`), com a arte do usuário por baixo, se houver (`.cm-fundo`);
3. logo horizontal branco, centralizado (`.cm-logo`, arquivo `@ds/logo-pge-branco.png`);
4. bloco do título com contorno laranja e canto superior esquerdo arredondado (`.cm-bloco`), com o tipo da publicação em caixa alta (`.cm-tipo`: GUIA, PLANO, MANUAL), o título (`.cm-titulo`) e o subtítulo ou a norma (`.cm-lei`);
5. faixa laranja que fecha o bloco (`.cm-faixa`), com a unidade à esquerda e edição e ano à direita (`.cm-edicao`);
6. filete laranja de 3 mm no pé.

O texto da faixa é azul-escuro, porque branco sobre o laranja não tem contraste para leitura. `.cm-tipo` e `.cm-lei` são opcionais: sem `.cm-tipo`, o título ocupa o lugar e cresce para 21 pt. Sem arte, apague o bloco `.cm-fundo` e a capa sai em azul liso.

Na capa azul, a arte de fundo entra em cinza e a 18% sobre o azul. O efeito é o dos manuais da UPD: a imagem vira textura azulada e o título branco continua legível em qualquer foto.

## Receber e preparar a imagem

A skill não gera imagem. Quando o usuário anexar um arquivo:

```bash
<dpge> imagem inspecionar arte.png
<dpge> imagem fundo  arte.png --saida capa-fundo.png    # arte por baixo da capa padrão
<dpge> imagem pagina arte.png --saida capa-pagina.png   # capa completa
```

`inspecionar` informa tamanho, proporção, quanto perde no recorte e a resolução em A4. Abaixo de uns 150 dpi a arte sai com pouca nitidez no papel; peça arquivo maior. `fundo` e `pagina` recortam em A4 sem deformar e dizem quanto da imagem se perdeu; acima de um terço, tente `--foco topo|base|esquerda|direita` ou `--foco 0.3,0.5` (posição x,y de 0 a 1), ou peça outra arte. Mostre o resultado ao usuário antes de seguir.

Depois, no `documento.html`, a arte de fundo vai na capa azul (variante), em

```html
<div class="cm-fundo"><img src="capa-fundo.png" alt=""></div>
```

e a capa de página inteira substitui toda a seção `capa-manual`:

```html
<section class="capa-manual capa-img">
  <img src="capa-pagina.png" alt="Título do documento, órgão e ano">
</section>
```

O texto alternativo repete o que está escrito na arte.

### O que olhar na imagem

- Texto ou logo desenhado dentro da arte não serve como fundo: aparece por baixo do título e briga com ele, e o acento costuma sair errado. Só a capa completa aprovada pode trazer texto, e então vale como foi entregue.
- O terço de baixo da página fica coberto pelo bloco do título; o assunto principal da foto deve estar no alto ou no meio.
- Foto com muito contraste (céu branco e sombra preta) vira manchas no fundo. Imagem de tom médio funciona melhor.

### Quando o usuário não tem arte

A capa branca padrão dispensa arte. Se o usuário quiser a capa azul com imagem e não tiver arte, ofereça duas saídas: capa azul lisa (documento pronto agora) ou gerar uma arte em outra ferramenta e anexar depois. Para a segunda, entregue este pedido pronto, ajustando o tema do documento:

> Fotografia ou ilustração em A4 retrato (1985 x 2808 px) sobre o tema: [tema do documento, em uma frase concreta]. Assunto principal no terço de cima e no meio da página; o terço de baixo pode ser só textura, porque será coberto por um bloco de título. Tons médios, sem áreas de branco puro ou de preto puro. Sem nenhum texto, sem letras, sem números, sem logotipo e sem brasão.

## Contracapa

Página inteira no azul da marca, com filete laranja de 3 mm no pé, como nos manuais da UPD:

- logo horizontal branco, centralizado no alto (`.cc-logo`, `@ds/logo-pge-branco.png`);
- no pé, a unidade responsável (`.cc-unidade`) e a lista de contatos (`ul.cc-contatos`), um por linha, cada um com o círculo laranja e o ícone genérico do modelo (telefone, e-mail, site, endereço);
- uma nota pequena opcional (`.cc-nota`) para versão, data, tiragem, ISSN ou condição de reprodução.

Regras:

- Cada contato é opcional. Apague a linha que o usuário não informou; não deixe marcador nem linha vazia.
- Confira telefone, e-mail e endereço com o usuário: os manuais da UPD de 2025 trazem telefones diferentes para a mesma unidade.
- A contracapa se identifica pela classe `contracapa` e vai no fim do `<body>`. O build a imprime em página inteira, sem cabeçalho e sem número, depois do corpo.
- A ficha do documento (autoria institucional, título, local, ano, palavras-chave) fica no expediente, no pé da página (`.ex-ficha`), e não na contracapa.

## Cuidados com a gráfica

A capa e a contracapa sangram (a cor vai até a borda). Para impressão profissional, combine com a gráfica a sangria e o perfil de cor; este PDF é feito para tela e para impressão de escritório. O arquivo sai em A4 (210 x 297 mm). As cores do manual da marca têm código CMYK próprio (ver `identidade.md`), que a gráfica deve usar no lugar da conversão automática do RGB.
