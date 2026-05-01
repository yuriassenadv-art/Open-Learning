---
name: savycode-preprompt
description: Use quando o usuário escrever /preprompt seguido de pedido vago, ambíguo, abrangente demais ou propenso a gerar gambiarra arquitetural — refina o prompt, explicita escopo, contexto, restrições e critérios de aceitação, e mostra a iteração de reescrita no chat antes de executar qualquer código
---

# SavyCode — PrePrompt

Primeiro filtro de prompts. Recebe texto bruto após `/preprompt` e devolve uma versão estruturada e assertiva ANTES de qualquer execução.

## Quando usar

Sempre que o usuário escrever `/preprompt <texto>`.

Sintomas no texto bruto que justificam refinamento:
- Verbos vagos ("faz", "monta", "resolve", "ajeita")
- Falta escopo ("um app pra X", "uma feature de Y")
- Stack/restrições não explícitas
- Pede múltiplas coisas no mesmo pedido
- Ausência de critério de aceitação

## Quando NÃO usar

- Pedidos triviais já claros ("rode os testes", "mostre o git log")
- Perguntas conceituais → use `savycode-btw`
- Comando de execução simples ("instala lodash")

## Fluxo

1. Receba o texto bruto após `/preprompt`.
2. Aplique a rubrica de qualidade — ver `savycode/references/prompt-rubric.md`.
3. Identifique buracos: escopo, contexto, stack, restrições, critério de aceitação.
4. Leia `~/.claude/savycode/knowledge-profile.json` — se houver áreas fracas relevantes, sugira restrições protetivas.
5. Reescreva no formato:

```
**Objetivo:** <uma frase>
**Contexto:** <stack atual, arquivos relevantes>
**Restrições:** <não pode X, deve usar Y>
**Critério de aceitação:** <como saberei que está pronto>
**Stack/ferramentas:** <linguagens, libs, comandos>
```

6. Mostre no chat ANTES/DEPOIS:

```
### Prompt original
> <texto bruto>

### Prompt refinado
<texto reescrito>

### O que mudou
- Adicionei: …
- Tornei explícito: …
- Ainda preciso confirmar com você: …
```

7. Pergunte: **"Confirma este prompt? (s / n / edita)"**
8. Só execute quando o usuário responder `s` ou ajustar o texto.

## Red flags — pare e pergunte

| Sintoma | Reação |
|---------|--------|
| "Faça por mim" sem detalhes | Pergunte qual é o resultado esperado |
| Múltiplas tarefas em um prompt | Ofereça quebrar em prompts separados |
| Conflito interno ("rápido E robusto") | Peça para priorizar |
| Stack contradiz o repositório | Confirme antes de seguir |

## Exemplo

**ANTES:** "cria um login pro app"

**DEPOIS:**
```
**Objetivo:** Implementar autenticação por email/senha no app web.
**Contexto:** Next.js 14 (App Router), sem backend próprio (usa Supabase).
**Restrições:** Não usar bibliotecas pagas. Sessões via cookie HttpOnly. Sem JWT no localStorage.
**Critério de aceitação:** Usuário consegue registrar, logar, deslogar; rotas protegidas redirecionam para /login; sessão persiste entre reloads.
**Stack/ferramentas:** Next.js Server Actions, Supabase Auth, Tailwind para o form, Zod para validação.
```

## Anti-patterns

- ❌ Reescrever silenciosamente sem mostrar o diff
- ❌ Reescrever e executar sem aguardar confirmação
- ❌ Adicionar restrições que o usuário não pediu (ex.: TypeScript se ele estava em JS)
- ❌ Inferir stack que não está no repositório

## Cross-references

- **Skill mãe:** `savycode`
- **Rubrica detalhada:** `savycode/references/prompt-rubric.md`
- **Após confirmação, se modo learning ligado:** `savycode-learning-to-code` toma a vez durante a geração
