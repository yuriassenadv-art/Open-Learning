# Knowledge Profile Schema — SavyCode

Arquivo: `~/.claude/savycode/knowledge-profile.json`

Mantido por `savycode-btw` (escreve) e lido por `savycode-learning-to-code` (calibra profundidade) e `savycode-preprompt` (sugere restrições protetivas).

## Schema

```json
{
  "version": 1,
  "level": 2,
  "topics": {
    "javascript:async": 2.5,
    "javascript:closures": 1.0,
    "react:hooks": 3.0,
    "react:state": 2.0,
    "python:basics": 4.0,
    "python:generators": 1.5,
    "git:branching": 2.0,
    "css:flexbox": 3.5,
    "sql:joins": 2.0
  },
  "weak_areas": [
    "javascript:closures",
    "python:generators"
  ],
  "interactions": 47,
  "last_topic": "react:hooks",
  "last_btw_check_at": "2026-05-01T15:30:00Z",
  "updated_at": "2026-05-01T15:35:00Z"
}
```

## Campos

| Campo | Tipo | Origem | Uso |
|-------|------|--------|-----|
| `version` | int | fixo | versionamento do schema |
| `level` | int (1-5) | recalculado | profundidade global das explicações |
| `topics` | dict | atualizado em cada `/btw` e `/learning-to-code` BTW Check | confiança 0-5 por tópico |
| `weak_areas` | list | derivado: `topics` com score < 1.5 | usado pelo `preprompt` para sugerir restrições |
| `interactions` | int | incremento em `/btw` | contador para gatilhar calibração a cada N |
| `last_topic` | string | último `/btw` | continuidade entre sessões |
| `last_btw_check_at` | iso datetime | último BTW Check | gatilhar nova calibração após X dias |
| `updated_at` | iso datetime | qualquer mutação | freshness |

## Convenção de nomes de tópico

Formato: `<linguagem>:<conceito>` ou `<framework>:<conceito>` em snake_case.

Exemplos:
- `javascript:async`, `javascript:closures`, `javascript:prototypes`
- `python:basics`, `python:generators`, `python:async`
- `react:hooks`, `react:state`, `react:context`
- `git:branching`, `git:rebase`
- `sql:joins`, `sql:indexes`
- `css:flexbox`, `css:grid`

Ao detectar tópico novo, crie a entrada com score inicial `1.0`.

## Cálculo do `level`

```python
def recalc_level(topics: dict, max_confidence: float = 5.0) -> int:
    if not topics:
        return 1
    top5 = sorted(topics.values(), reverse=True)[:5]
    mean_top5 = sum(top5) / len(top5)
    return max(1, min(5, round(mean_top5 / max_confidence * 5)))
```

## Atualização de score

| Evento | Operação |
|--------|----------|
| Usuário pergunta sobre tópico T | `topics[T] += 0.5` |
| Usuário responde "sim" no mini-check | `topics[T] += 0.5` |
| Usuário responde "não" no mini-check | `topics[T] -= 0.3` |
| BTW Check explícito com auto-rating N (1-5) | `topics[T] = 0.7 * topics[T] + 0.3 * N` |

Score sempre clampado em `[0, 5]`.

## Inicialização

Se o arquivo não existe, crie com:

```json
{
  "version": 1,
  "level": 1,
  "topics": {},
  "weak_areas": [],
  "interactions": 0,
  "last_topic": null,
  "last_btw_check_at": null,
  "updated_at": "<now>"
}
```

E dispare uma calibração inicial via `/btw` (modo Claude pergunta) na primeira oportunidade.
