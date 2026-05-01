# Open-Learning

Família de skills para Claude Code que transforma o agente em um pair-programmer didático.
Lugar de desenvolvimento e aperfeiçoamento da skill global **SavyCode**.

## Visão geral

Três comandos cooperam:

| Comando | Quando | O que faz |
|---------|--------|-----------|
| `/preprompt <texto>` | Antes da execução, sob demanda | Filtra prompt — mostra ANTES/DEPOIS no chat e pede confirmação |
| `/learning-to-code on\|off` | Modo persistente | Comenta cada construção do código com profundidade calibrada e mantém log |
| `/btw <pergunta>` | Dúvida pontual | Responde no chat, atualiza perfil de conhecimento |

Inspiração: prompt socrático de "Engenheiro Sênior + Mentor Pessoal" para combater vibe-coding cego.

## Estrutura do repositório

```
Open-Learning/
├── README.md                              # este arquivo
├── skill-savycode/                        # skill mãe (orquestra)
│   ├── SKILL.md
│   ├── references/
│   │   ├── prompt-rubric.md               # rubrica usada por /preprompt
│   │   ├── mentor-protocol.md             # protocolo socrático (4 princípios)
│   │   └── knowledge-profile-schema.md    # schema do perfil JSON
│   └── scripts/
│       └── consolidate_to_docx.py         # gera .docx do log de aprendizado
├── skill-savycode-preprompt/SKILL.md      # comando /preprompt
├── skill-savycode-learning-to-code/SKILL.md # comando /learning-to-code
├── skill-savycode-btw/SKILL.md            # comando /btw
└── state-template/                        # template do estado persistente
    ├── state.json                         # flags: learning_mode, log atual
    └── knowledge-profile.json             # nível 1-5, score por tópico
```

## Instalação local (Claude Code)

```bash
# Linka cada skill para ~/.claude/skills/
ln -s "$(pwd)/skill-savycode" ~/.claude/skills/savycode
ln -s "$(pwd)/skill-savycode-preprompt" ~/.claude/skills/savycode-preprompt
ln -s "$(pwd)/skill-savycode-learning-to-code" ~/.claude/skills/savycode-learning-to-code
ln -s "$(pwd)/skill-savycode-btw" ~/.claude/skills/savycode-btw

# Copia template de estado para a pasta global
mkdir -p ~/.claude/savycode
cp state-template/*.json ~/.claude/savycode/
```

## Estado persistente

- `~/.claude/savycode/state.json` — flags do modo learning, log atual
- `~/.claude/savycode/knowledge-profile.json` — nível, score por tópico, áreas fracas

Schema completo: [skill-savycode/references/knowledge-profile-schema.md](skill-savycode/references/knowledge-profile-schema.md)

## Persistência do aprendizado

Quando o usuário envia novo prompt fora do trio, o log da sessão é consolidado em
`<projeto>/learning-journal/<YYYY-MM-DD>-<slug>.docx`.

```bash
python3 skill-savycode/scripts/consolidate_to_docx.py \
  --log <log.md> \
  --project <pasta-do-projeto>
```

Dependência opcional: `python-docx` (`pip install python-docx`). Se ausente, gera fallback `.md`.

## Roadmap

- [ ] Hook `UserPromptSubmit` para auto-roteamento (detecta verbo vago e sugere `/preprompt`)
- [ ] Integração com IDEs (Cursor, VS Code) para painel lateral de aprendizado
- [ ] Calibração mais fina via NLP — detectar nível pelas perguntas, não só auto-rating
- [ ] Versão multi-idioma (atualmente só PT-BR/EN)
- [ ] Exportar `.docx` com syntax highlight via Pygments

## Como contribuir

1. Edite as SKILL.md correspondentes
2. Teste com cenários reais de prompt fraco / forte
3. Atualize `references/` se mudar rubrica, schema ou protocolo
4. Bump da versão no schema do perfil quando quebrar compatibilidade

## Licença

MIT — uso pessoal e comercial liberado, atribuição apreciada.
