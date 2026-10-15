# Identidade visual da PGE-MS

Valores do design system. Estão em `assets/design-system/tokens.css`; esta página resume o que não pode mudar.

## Cores

| Cor | Hex | Uso |
|---|---|---|
| Preto | `#000000` | texto de leitura: corpo, células, listas, negrito do corpo |
| Marinho | `#152B3F` | títulos, tarja da capa, cabeçalho de tabela, estrutura |
| Azul médio | `#294964` | numeração de seção, filetes, rótulos |
| Laranja | `#F58634` | destaque e filete da capa; no máximo dois ou três lugares por documento |
| Verde-água | `#51A8B1` | apoio e grafismo |
| Cinza | `#D2D3D5` | filetes, bordas, fundos de quadro |

Texto de leitura é preto e a cor fica na moldura institucional. Negrito do corpo é preto, não azul: azul é mais claro que o preto e reduz o contraste do trecho em vez de aumentá-lo.

## Fontes

Todas variáveis, licença SIL OFL, dentro de `assets/design-system/fonts/`: Source Sans 3 (corpo e rótulos da publicação), Montserrat (cabeçalho e rodapé de todas as páginas, documento institucional sem sobrescrita) e Source Serif 4 (herança de peça processual, fora do escopo). Nunca dependa da fonte instalada no computador do usuário.

## Página

A4, margens de 25 mm nas laterais, 31 mm no topo e 19 mm no pé. Área útil de 160 mm e 247 mm de altura. Corpo de 12 pt, entrelinha 1,22, texto justificado e sem hifenização. Cerca de 72 caracteres por linha.

## Marca

- O logo é `assets/design-system/logo-pge.png`, retirado do cabeçalho oficial da PGE. Não se altera, não se recolora, não se redesenha e nunca se pede a um modelo de imagem (sai com defeito). A marca da PGE e o logo pertencem à Procuradoria-Geral do Estado de Mato Grosso do Sul e não estão cobertos pela licença deste repositório.
- Nenhuma marca de terceiro entra no documento sem o usuário pedir.
- O documento fala em nome da PGE só se o usuário tem autoridade para isso. Para material de autoria pessoal ou de equipe, o expediente diz quem assina.

## Texto

- Caracteres certos: aspas curvas, reticência `…`, meia-risca `–` em intervalo (`fls. 12–19`), ordinal `º` e `ª`, `n.` e não `nº` (a exceção é o texto citado da norma).
- Espaço não separável depois de `art.`, `n.`, `§`, `inc.`, `Lei`, `Tema`, `Súmula`, `R$`.
- Nunca sublinhar. Ênfase é o negrito.
- Caixa alta só em rótulo curto, com entreletra positiva.
- Título que diz o argumento. Máximo de três níveis.

As regras completas, com o motivo de cada uma, estão em `tipografia.md`.
