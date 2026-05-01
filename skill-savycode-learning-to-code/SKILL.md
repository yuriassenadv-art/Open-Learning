---
name: savycode-learning-to-code
description: Use quando o usuário invocar /learning-to-code (on/off) ou estiver gerando código junto com o Claude e quiser entender o significado de cada construção — apresenta explicação didática inline com profundidade calibrada pelo nível em ~/.claude/savycode/knowledge-profile.json, mantém log de aprendizado em learning-journal/ e consolida tudo em arquivo .docx ao iniciar novo prompt
---

# SavyCode — Learning to Code

Modo Mentor: cada vez que o Claude gera código, este skill explica didaticamente o que cada parte faz, com profundidade ajustada ao nível atual do usuário medido pelo `savycode-btw`.

## Quando usar

- Comando explícito: `/learning-to-code on` (liga) | `/learning-to-code off` (desliga) | `/learning-to-code status`
- Sempre ativo quando flag `learning_mode: true` em `~/.claude/savycode/state.json`

## Pré-requisito de ambiente — bloqueia ativação

A skill entrega código anotado e log didático **como arquivos** que o usuário precisa ver lado a lado com o chat. Antes de ligar o modo, detecte o ambiente:

**Detecção automática:** rode o script de detecção e use a saída JSON para decidir.

```bash
python3 ~/.claude/skills/savycode/scripts/detect_environment.py
# {"supported": true, "client": "Cursor", "reason": "TERM_PROGRAM=cursor"}  → exit 0
# {"supported": false, "client": "ssh-sem-tui", "reason": "..."}             → exit 1
```

Se `exit 0` → ative. Se `exit 1` → recuse com a mensagem padrão abaixo. Em caso de exit 2 (erro), trate como recusa conservadora.

**Sinais de cliente com painel (script retorna `supported: true`):**
- `CLAUDE_CODE_DESKTOP` / `CLAUDECODE_DESKTOP` setados → Claude Code Desktop
- `CLAUDE_AI_WEB` / `CLAUDECODE_WEB` setados → Web app
- `TERM_PROGRAM` em {`vscode`, `cursor`, `windsurf`, `zed`, `fleet`} → IDE
- `VSCODE_PID` / `CURSOR_TRACE_ID` / `IDEA_INITIAL_DIRECTORY` → IDE direta

**Sinais de terminal puro (script retorna `supported: false`):**
- `TERM=dumb`
- `SSH_CONNECTION` setado sem `TERM_PROGRAM`
- stdout não-TTY (ambiente não interativo)
- Inconclusivo (postura A — recusa conservadora)

**Resposta padrão de recusa em terminal puro:**

```
**[Learning Mode indisponível neste ambiente]**

O modo learning entrega código anotado e log de aprendizado como arquivos
para serem lidos no painel ao lado do chat. Em terminal puro (sem split
de arquivos) o conteúdo didático não renderiza propriamente, então a
ativação foi recusada.

Alternativas:
- Abra o Claude Code Desktop, Cursor ou VS Code para usar `/learning-to-code on`
- Para dúvidas pontuais aqui no terminal, use `/btw <pergunta>`
- Para refinar prompts antes de executar, use `/preprompt <texto>`
```

NÃO altere `learning_mode` em `state.json` quando recusar. Mantenha `false`.

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

2. **Gere o código de produção limpo** (sem comentários didáticos — só comentários técnicos genuínos sobre invariantes/workarounds, se houver):
   ```python
   def soma(a, b):
       return a + b
   ```

3. **Escreva o log de aprendizado** em `<projeto>/learning-journal/<YYYY-MM-DD>-<slug>.md` com referência de linha apontando ao arquivo real. É **este arquivo** que renderiza no painel lateral:
   ```markdown
   # Sessão: somador básico

   ## Construção: `def` (L1 em `soma.py`)
   - **O que é:** palavra-chave que declara uma função reutilizável.
   - **Por que aqui:** vamos chamar a soma em vários lugares.
   - **Vai aprender depois:** funções anônimas (lambdas), decoradores.

   ## Construção: `return` (L2 em `soma.py`)
   - **O que é:** devolve o valor calculado para quem chamou a função.
   - **Por que aqui:** sem `return`, a função executa mas não entrega o resultado.
   ```

   Anuncie no chat: `Lição escrita em learning-journal/<arquivo>.md — abra ao lado do código.`

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
     --profile ~/.claude/savycode/knowledge-profile.json \
     --context-lines 0
   ```
   O script lê cada `## Construção: `nome` (Lxx em `arquivo`)` do log, resolve o caminho relativo à raiz do projeto, e injeta o trecho real do código no `.docx` ao lado da explicação. `--context-lines N` adiciona N linhas antes/depois para enquadrar o trecho.
4. Confirme no chat:
   ```
   **Aprendizado consolidado** → `<projeto>/learning-journal/<arquivo>.docx`
   ```
5. Limpe o `current_session_log` no state e crie novo na próxima geração.

> O código de produção já é gerado limpo (passo 2 do fluxo), então não há comentários didáticos a remover na consolidação.

## Entrega no painel lateral

Premissa: a skill só ativa em ambientes com painel (ver "Pré-requisito de ambiente" acima). A entrega didática é sempre file-first:

- **Código de produção** fica limpo (só comentários técnicos genuínos sobre invariantes/workarounds).
- **Log de aprendizado** em `<projeto>/learning-journal/<YYYY-MM-DD>-<slug>.md` recebe a explicação por construção.
- **Referência cruzada por linha** no log: `// L42: `useState` cria estado local…` aponta de volta ao código real.
- O usuário arrasta o log para o split lateral; o painel passa a mostrar código + lição lado a lado.

Quando o ambiente é Claude Code Desktop ou web app, o painel direito já abre o arquivo escrito automaticamente — não é preciso pedir ao usuário para abrir nada.

Em terminal puro a skill **já recusou ativação**, então este caso não chega aqui.

## Anti-patterns

- ❌ Escrever comentários didáticos no código de produção — vai tudo no log
- ❌ Ativar o modo em terminal puro (precisa recusar com a mensagem padrão)
- ❌ Comentário óbvio no log (`# variável x`) — sem valor didático
- ❌ Usar mesmo nível para todos os usuários
- ❌ Esquecer de atualizar `current_session_log` no state
- ❌ Não rodar o script de consolidação ao novo prompt

## Cross-references

- **Skill mãe:** `savycode`
- **Schema do perfil:** `savycode/references/knowledge-profile-schema.md`
- **Protocolo socrático:** `savycode/references/mentor-protocol.md`
- **Detecção de ambiente:** `savycode/scripts/detect_environment.py`
- **Script de consolidação:** `savycode/scripts/consolidate_to_docx.py`
