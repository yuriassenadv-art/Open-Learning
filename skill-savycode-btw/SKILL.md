---
name: savycode-btw
description: Use quando o usuário escrever /btw seguido de pergunta sobre código, conceito, biblioteca, padrão ou erro — responde diretamente no chat com profundidade calibrada pelo nível em ~/.claude/savycode/knowledge-profile.json, atualiza o perfil com base na pergunta e pode contra-perguntar para mensurar conhecimento
---

# SavyCode — BTW

Canal direto de dúvidas. O usuário escreve `/btw <pergunta>` e o Claude responde **no próprio chat** — não em arquivo, não em comentário no código.

## Quando usar

- Comando explícito: `/btw <pergunta>` — usuário pergunta
- Comando explícito: `/btw` (sem texto) — Claude faz pergunta diagnóstica para calibrar nível
- Pergunta sobre conceito, sintaxe, "por que isso?", "tem outra forma?", "esse erro significa o quê?"

## Quando NÃO usar

- Pedido para gerar código → use `savycode-preprompt`
- Comando de execução ("rode", "instala") → execute direto
- Pergunta filosófica/política/fora de escopo

## Fluxo — usuário pergunta

1. Receba `/btw <pergunta>`.
2. Leia `~/.claude/savycode/knowledge-profile.json` para `level`, `topics`, `weak_areas`.
3. Identifique o tópico da pergunta — mapeie para a chave em `topics` (ex.: "promises" → `javascript:async`).
4. Responda **no chat** com a profundidade do nível atual. Estilo varia por nível conforme `savycode-learning-to-code`.
5. Atualize o perfil:
   - `topics[tópico] += 0.5` (sinal de que o usuário está estudando)
   - `interactions += 1`
   - `last_topic = <tópico>`
   - `updated_at = now`
6. Termine com mini-check:
   ```
   Faz sentido? (sim / não / explica diferente)
   ```
   Se "não" → reformule com analogia mais concreta. Decremente `topics[tópico] -= 0.3`.

## Fluxo — Claude pergunta (calibração)

Após N=5 interações OU quando o nível precisa de calibração inicial OU quando `/btw` é chamado sem texto:

```
**[BTW — calibração]** Antes de continuar, me responde rápido:
1. Sabe a diferença entre `let` e `const`? (sim / não / mais ou menos)
2. Já usou `try/catch` na vida real? (sim / não)
3. Sabe o que é uma Promise? (sim / não / já ouvi falar)
```

Depois das respostas, recalcule `level` (ver fórmula em `references/knowledge-profile-schema.md`) e atualize `topics`.

## Calibração de nível

```python
# Pseudocode — implementação real no script de consolidação
top5 = sorted(topics.values(), reverse=True)[:5]
mean_top5 = sum(top5) / len(top5)
level = max(1, min(5, round(mean_top5 / max_confidence * 5)))
```

Salve em `knowledge-profile.json`. `savycode-learning-to-code` lê esse `level` para calibrar profundidade nas próximas explicações.

## Exemplos

**Usuário:** `/btw o que é useEffect?`

**Resposta (nível 2):**
> `useEffect` é a forma do React rodar código com efeito colateral (chamar API, mexer no DOM, configurar timer) DEPOIS que o componente renderiza. Tem dois argumentos: a função que roda, e um array de dependências que decide *quando* roda. Faz sentido? (sim / não / explica diferente)

**Resposta (nível 4):**
> `useEffect(fn, deps)` agenda `fn` para após o commit phase. `deps` define igualdade referencial (Object.is) para skip — `[]` roda só após mount, omitido roda toda render. A cleanup function permite teardown antes do próximo effect ou unmount. Cuidados: closure stale com `deps` defasado, dependências não-primitivas (objetos/arrays) recriadas a cada render disparam infinite loop, race conditions com fetch.

## Anti-patterns

- ❌ Responder em arquivo `.md` em vez do chat
- ❌ Usar mesmo nível para todo usuário
- ❌ Não atualizar o perfil após responder
- ❌ Responder pergunta de execução (não é o papel do `/btw`)
- ❌ Pular o mini-check final (é o sinal mais barato pra calibrar)

## Cross-references

- **Skill mãe:** `savycode`
- **Schema do perfil:** `savycode/references/knowledge-profile-schema.md`
- **Calibra:** `savycode-learning-to-code` (lê `level` deste perfil)
