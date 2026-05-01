---
name: savycode-learning-to-code
description: Use quando o usuário invocar /learning-to-code (on/off) ou estiver gerando código junto com o Claude e quiser entender o significado de cada construção — apresenta explicação didática inline com profundidade calibrada pelo nível em ~/.claude/savycode/knowledge-profile.json, mantém log de aprendizado em learning-journal/ e consolida tudo em arquivo .docx ao iniciar novo prompt
---

# SavyCode — Learning to Code

Modo Mentor: cada vez que o Claude gera código, este skill explica didaticamente o que cada parte faz, com profundidade ajustada ao nível atual do usuário medido pelo `savycode-btw`.

## Quando usar

- Comando explícito: `/learning-to-code on` (liga) | `/learning-to-code off` (desliga) | `/learning-to-code status`
- Sempre ativo quando flag `learning_mode: true` em `~/.claude/savycode/state.json`

## Estado de ativação

Lê em `~/.claude/savycode/state.json`:

```json
{
  "learning_mode": true,
  "current_session_log": "/Users/.../projeto/learning-journal/2026-05-01-build-login.md",
  "consolidate_on_new_prompt": true,
  "started_at": "2026-05-01T10:00:00Z"
}
```

Se `current_session_log` estiver vazio, crie um novo na primeira geração de código.

## Profundidade adaptativa

Lê o nível em `~/.claude/savycode/knowledge-profile.json`. Ver `savycode/references/knowledge-profile-schema.md`.

| Nível | Estilo | Exemplo para `const x = 5;` |
|-------|--------|------------------------------|
| 1 (iniciante) | Analogia + zero jargão | "É uma caixinha chamada `x` que guarda o número 5. `const` quer dizer que o conteúdo da caixinha não pode mudar depois." |
| 2-3 (intermediário) | Jargão controlado | "Declara `x` como constante imutável (binding). Em runtime, `x` referencia o literal numérico `5`." |
| 4-5 (avançado) | Técnico + edge cases | "Binding `const` no escopo léxico atual. TDZ aplicável até a linha de declaração. Não é deep-freeze (objeto referenciado continua mutável)." |

## Fluxo durante geração de código

1. **Anuncie** o modo no início da resposta:
   ```
   **[Learning Mode ON — nível N]** Vou comentar cada construção. Use `/btw` se algo não fizer sentido.
   ```

2. **Gere código com comentários inline didáticos** no nível atual. Exemplo nível 2:
   ```python
   # `def` declara uma função reutilizável. Tudo indentado abaixo é o corpo.
   def soma(a, b):
       # `return` devolve o valor para quem chamou.
       return a + b
   ```

3. **Anexe ao log de aprendizado** (`<projeto>/learning-journal/<YYYY-MM-DD>-<slug>.md`) em paralelo:
   ```markdown
   ## Construção: `def`
   - **O que é:** palavra-chave que declara uma função.
   - **Por que aqui:** precisamos reutilizar a soma em vários lugares.
   - **Vai aprender depois:** funções anônimas (lambdas), decoradores.
   ```

4. **Mensuração contínua:** a cada ~5 construções novas, faça pergunta de auto-avaliação:
   ```
   **[BTW Check]** Você ficou confortável com `async/await`? (1=não 5=domino)
   ```
   Salve no `knowledge-profile.json` em `topics`.

## Consolidação ao novo prompt

Quando o usuário envia um novo prompt (não `/btw`, não `/learning-to-code`):

1. Verifique se `consolidate_on_new_prompt: true` no state.
2. Leia o log de aprendizado da sessão (`current_session_log`).
3. Execute:
   ```bash
   python3 ~/.claude/skills/savycode/scripts/consolidate_to_docx.py \
     --log <log_path> \
     --project <projeto_path> \
     --profile ~/.claude/savycode/knowledge-profile.json
   ```
4. **Apague os comentários didáticos** do código atual (mantém só comentários técnicos genuínos sobre invariantes, workarounds, etc.).
5. Confirme no chat:
   ```
   **Aprendizado consolidado** → `<projeto>/learning-journal/<arquivo>.docx`
   Comentários didáticos removidos do código (mantive apenas comentários técnicos genuínos).
   ```
6. Limpe o `current_session_log` no state e crie novo na próxima geração.

## Indicação direta no terminal lateral

Quando o ambiente é uma IDE com painel lateral (Cursor, VS Code, Antigravity):
- Em vez de poluir o código com comentários, escreva os comentários didáticos no log markdown
- O log fica aberto lateral ao código (o usuário arrasta para o split)
- Use referências de linha: `// L42: `useState` cria estado local…`

Em CLI puro, use comentários inline normais.

## Anti-patterns

- ❌ Comentar `# variável x` (óbvio, sem valor didático)
- ❌ Manter comentários didáticos no código após consolidação
- ❌ Usar mesmo nível para todos os usuários
- ❌ Esquecer de atualizar `current_session_log` no state
- ❌ Não rodar o script de consolidação ao novo prompt

## Cross-references

- **Skill mãe:** `savycode`
- **Schema do perfil:** `savycode/references/knowledge-profile-schema.md`
- **Protocolo socrático:** `savycode/references/mentor-protocol.md`
- **Script de consolidação:** `savycode/scripts/consolidate_to_docx.py`
