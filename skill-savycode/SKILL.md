---
name: savycode
description: Use quando o usuário invocar /preprompt, /learning-to-code ou /btw, ou pedir para refinar prompts, aprender código de forma didática enquanto programa, ou medir o próprio nível de programação — família de três skills que filtra prompts antes da execução, ensina cada construção do código gerado e mensura o conhecimento via perguntas no chat
---

# SavyCode

Família de skills que transforma o Claude Code em um Mentor de Programação Pessoal. O modelo deixa de ser "caixa preta" e passa a ser pair-programmer didático.

Três comandos cooperam:

| Comando | Quando | O que faz |
|---------|--------|-----------|
| `/preprompt <texto>` | Antes de execução, sob demanda | Filtra e refina o prompt — mostra ANTES/DEPOIS no chat e pede confirmação |
| `/learning-to-code on\|off` | Modo persistente | Comenta cada construção do código com profundidade calibrada e mantém log de aprendizado |
| `/btw <pergunta>` | Dúvida pontual | Responde no chat e atualiza o perfil de conhecimento |

## Estado persistente

Dois arquivos vivem em `~/.claude/savycode/` e não vão para o repositório do projeto:

- `state.json` — flags da skill (modo learning ligado/desligado, log atual)
- `knowledge-profile.json` — nível do usuário, score por tópico, áreas fracas

Ver `references/knowledge-profile-schema.md` para o schema completo.

## Cooperação entre os comandos

```
/preprompt → refina pedido → executa código com /learning-to-code → /btw resolve dúvidas → ajusta nível → próximo /preprompt já vem mais maduro
```

`/btw` alimenta o perfil. `/learning-to-code` lê o perfil para calibrar profundidade. `/preprompt` lê áreas fracas para sugerir restrições que protejam o usuário (ex.: "não use Promises se ainda não dominou async").

## Persistência do aprendizado

Quando o usuário envia um novo prompt (não `/btw`, não `/learning-to-code`), o conteúdo do log de aprendizado da sessão é consolidado em:

```
<projeto>/learning-journal/<YYYY-MM-DD>-<slug>.docx
```

O arquivo contém:
1. **Contexto** — qual era o prompt original
2. **Código gerado** — versão final, com syntax highlight
3. **Significado de cada construção** — extraído dos comentários inline
4. **Lições principais** — resumo dos conceitos novos
5. **Conclusões / próximos estudos** — sugeridos pelo perfil

Use `scripts/consolidate_to_docx.py` para gerar.

## Sub-skills

- **REQUIRED SUB-SKILL:** Use `savycode-preprompt` para refinamento de prompts.
- **REQUIRED SUB-SKILL:** Use `savycode-learning-to-code` para explicação inline durante geração de código.
- **REQUIRED SUB-SKILL:** Use `savycode-btw` para perguntas pontuais e calibração do nível.

## Anti-patterns globais

- Não execute código sem rodar `/preprompt` quando o pedido for vago
- Não mantenha comentários didáticos no código após consolidação para `.docx`
- Não use o mesmo nível didático para todos os usuários — leia o perfil
