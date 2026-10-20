# Capa e contracapa

O desenho segue os manuais da UPD de 2025 (Guia, Plano e Orientações), com as cores e os logos do manual da marca da PGE. Ver `identidade.md`.

## A capa padrão

De cima para baixo:

1. faixa laranja de 6 mm no topo, de borda a borda;
2. campo inteiro no azul da marca (`#294964`), com a arte do usuário por baixo, se houver (`.cm-fundo`);
3. logo horizontal branco, centralizado (`.cm-logo`, arquivo `@ds/logo-pge-branco.png`);
4. bloco do título com contorno laranja e canto superior esquerdo arredondado (`.cm-bloco`), com o tipo da publicação em caixa alta (`.cm-tipo`: GUIA, PLANO, MANUAL), o título (`.cm-titulo`) e o subtítulo ou a norma (`.cm-lei`);
5. faixa laranja que fecha o bloco (`.cm-faixa`), com a unidade à esquerda e edição e ano à direita (`.cm-edicao`);
6. filete laranja de 3 mm no pé.

O título, o logo e a faixa são sempre HTML, nunca parte da imagem. O texto da faixa é azul-escuro, porque branco sobre o laranja não tem contraste para leitura.

`.cm-tipo` é opcional: sem ele, o título ocupa o lugar e cresce para 21 pt. `.cm-lei` também é opcional.

## Quatro capas possíveis

| Capa | Quando | Como |
|---|---|---|
| Azul liso (padrão) | o usuário não tem arte | apague o bloco `.cm-fundo` do modelo |
| Azul com arte de fundo | o usuário anexou uma foto ou ilustração | `imagem fundo`, e o arquivo entra em `.cm-fundo` |
| Imagem de página inteira | o usuário anexou uma capa completa, já aprovada | `imagem pagina`; nada é desenhado por cima |
| Branca (variante) | só quando o usuário pedir uma capa clara, como a do Programa de Integridade 2026 | troque a seção pela marcação `capa-branca` do comentário do modelo; ver `padrao-referencia.md` |

A arte de fundo entra em cinza e a 18% sobre o azul. O efeito é o dos manuais da UPD: a imagem vira textura azulada e o título branco continua legível em qualquer foto.

## Receber e preparar a imagem

A skill não gera imagem. Quando o usuário anexar um arquivo:

```bash
<dpge> imagem inspecionar arte.png
<dpge> imagem fundo  arte.png --saida capa-fundo.png    # arte por baixo da capa padrão
<dpge> imagem pagina arte.png --saida capa-pagina.png   # capa completa
```

`inspecionar` informa tamanho, proporção, quanto perde no recorte e a resolução em A4. Abaixo de uns 150 dpi a arte sai com pouca nitidez no papel; peça arquivo maior. `fundo` e `pagina` recortam em A4 sem deformar e dizem quanto da imagem se perdeu; acima de um terço, tente `--foco topo|base|esquerda|direita` ou `--foco 0.3,0.5` (posição x,y de 0 a 1), ou peça outra arte. Mostre o resultado ao usuário antes de seguir.

Depois, no `documento.html`, a arte de fundo vai em

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

Ofereça duas saídas: capa azul lisa (documento pronto agora) ou gerar uma arte em outra ferramenta e anexar depois. Para a segunda, entregue este pedido pronto, ajustando o tema do documento:

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
