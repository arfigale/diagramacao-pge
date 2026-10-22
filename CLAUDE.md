# Instruções para o Claude ao receber o link deste repositório

Quando o usuário colar o link deste repositório (https://github.com/arfigale/diagramacao-pge) e pedir para instalar, atualizar ou configurar a skill, faça tudo sem perguntar nada, na ordem abaixo. Fale com o usuário em linguagem simples e não peça que ele rode comandos.

## Se você tem acesso a terminal (Claude Code, aba Code do aplicativo, Cowork)

1. Baixe o repositório. Se a pasta `~/.claude/skills/diagramacao-pge` já existir como repositório git, vá direto ao passo 2 (o instalador faz o `git pull`).
   - Com Git: `git clone https://github.com/arfigale/diagramacao-pge <pasta-temporária>`
   - Sem Git: baixe `https://github.com/arfigale/diagramacao-pge/archive/refs/heads/main.zip` e extraia.
2. Rode o instalador de dentro da pasta baixada:
   - Mac e Linux: `python3 scripts/instalar.py`
   - Windows: `py -3 scripts\instalar.py` (ou `python scripts\instalar.py`)

   Ele coloca a skill em `~/.claude/skills/diagramacao-pge`, prepara o ambiente, instala a fonte Source Sans 3 para o usuário (sem administrador) e gera `diagramacao-pge.zip` na pasta Downloads. Leva alguns minutos na primeira vez.
3. Leia o final da saída. Se o `doctor` apontou `FALTA` ou `AVISO`, resolva o que for possível (quase sempre falta Python 3.10 ou mais novo, ou a internet) e rode de novo. Não instale pacotes à mão.
4. Se o PowerShell estiver bloqueado, use `cmd`: o instalador é Python e não usa PowerShell.

## Se o usuário usa o Claude no site ou no aplicativo e você tem a extensão Claude in Chrome

Depois do passo 2, abra `https://claude.ai/customize/skills`, escolha Adicionar > Fazer upload de Skill e envie o `diagramacao-pge.zip`. Confira antes se já existe uma skill `diagramacao-pge` na lista "Meus": se existir, avise o usuário para apagá-la ou desligá-la, para não ficarem duas. Só clique em "Fazer upload" com o pedido do usuário para instalar.

Sem a extensão, entregue o zip e diga o único passo que falta: Customize > Skills > Adicionar > Fazer upload de Skill.

## Ao terminar

Diga em poucas linhas: onde a skill ficou, se a fonte foi instalada, o que falta (se faltar) e que o Word deve ser fechado e aberto de novo para enxergar a fonte. Uma conversa nova carrega a versão atualizada.

## Para usar a skill

Leia `SKILL.md`. Os comandos ficam em `scripts/dpge.py` (`dpge.cmd` no Windows).
