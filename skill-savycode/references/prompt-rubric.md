# Rubrica de Qualidade de Prompt — SavyCode PrePrompt

Aplicada por `savycode-preprompt`. Cada item gera uma pergunta interna; se algum não for respondido pelo texto bruto do usuário, o refinamento deve explicitar.

## Os 5 pilares

### 1. Objetivo (uma frase)

- ✅ "Implementar login por email/senha"
- ❌ "Mexer no auth"

Pergunta: **"Qual é o resultado em UMA frase?"**

### 2. Contexto

- Stack atual (Next.js 14, Python 3.12, etc.)
- Arquivos/módulos envolvidos
- Estado atual ("não tem nada", "tem JWT, quero trocar pra cookie")

Pergunta: **"O que já existe e onde a mudança encaixa?"**

### 3. Restrições

- O que NÃO pode ser usado (libs proibidas, padrões a evitar)
- O que DEVE ser usado (libs já no projeto, padrões da casa)
- Limites de performance / segurança / orçamento

Pergunta: **"O que não pode aparecer no resultado?"**

### 4. Critério de aceitação

- Como o usuário vai validar que está pronto
- Casos de teste mentais ("se eu fizer X, deve acontecer Y")

Pergunta: **"Como vou saber que ficou pronto?"**

### 5. Stack / ferramentas

- Linguagens, libs, frameworks específicos
- Comandos a usar (npm, uv, cargo)
- Versões

Pergunta: **"Com o quê?"**

## Sintomas de prompt fraco

| Sintoma | Reformulação sugerida |
|---------|------------------------|
| Verbo vago ("faz", "ajeita") | Substituir por verbo específico (implementa, refatora, testa, documenta) |
| "Pra todo mundo" | Especificar persona (admin, usuário logado, anônimo) |
| "Rápido" | Definir SLA específico (ms, requests/s) |
| "Bonito" | Apontar referência visual ou critério (Tailwind, design system X) |
| "Tipo o do site Y" | Descrever o que do site Y especificamente |

## Conflitos comuns

- "Rápido **e** robusto" → escolher prioridade
- "Simples **e** flexível" → escolher prioridade
- "Já pra produção **e** sem testes" → recusar e explicar trade-off

## Estrutura final do refinamento

```
**Objetivo:** <uma frase>
**Contexto:** <stack + estado atual>
**Restrições:** <bullet list>
**Critério de aceitação:** <bullet list verificável>
**Stack/ferramentas:** <comma-separated>
```

## Quando NÃO refinar

- Pedido já claro nos 5 pilares
- Comando one-liner ("git status", "npm test")
- Pergunta conceitual (rota para `/btw`)
