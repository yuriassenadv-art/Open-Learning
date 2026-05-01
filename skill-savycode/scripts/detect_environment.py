#!/usr/bin/env python3
"""
Detecta se o ambiente atual suporta a entrega file-first do SavyCode.

Saída no stdout (JSON):
    {"supported": true|false, "client": "<nome>", "reason": "<motivo>"}

Exit code:
    0 — ambiente suportado (cliente com painel detectado)
    1 — ambiente NÃO suportado (terminal puro / inconclusivo conservador)
    2 — erro interno

Heurística (em ordem de prioridade):
    1. Variáveis explícitas de cliente Anthropic (CLAUDE_CODE_DESKTOP, CLAUDECODE)
    2. Variáveis de IDE (TERM_PROGRAM=vscode, CURSOR_*, JETBRAINS_IDE, INTELLIJ_*)
    3. Web app (CLAUDE_AI_WEB ou similares — quando expostas)
    4. TERM=dumb ou ausência de TERM em sessão SSH não-interativa → recusa
    5. Inconclusivo → recusa conservadora (postura A definida pelo projeto)
"""
from __future__ import annotations

import json
import os
import sys


SUPPORTED_TERM_PROGRAMS = {
    "vscode": "VS Code",
    "cursor": "Cursor",
    "windsurf": "Windsurf",
    "zed": "Zed",
    "fleet": "JetBrains Fleet",
}

JETBRAINS_HINT_VARS = ("IDEA_INITIAL_DIRECTORY", "INTELLIJ_PROJECT_ROOT", "TERMINAL_EMULATOR")


def detect() -> dict:
    env = os.environ

    if env.get("CLAUDE_CODE_DESKTOP") or env.get("CLAUDECODE_DESKTOP"):
        return {"supported": True, "client": "claude-code-desktop", "reason": "CLAUDE_CODE_DESKTOP env detected"}

    if env.get("CLAUDE_AI_WEB") or env.get("CLAUDECODE_WEB"):
        return {"supported": True, "client": "claude-web", "reason": "web app env detected"}

    term_program = (env.get("TERM_PROGRAM") or "").lower()
    if term_program in SUPPORTED_TERM_PROGRAMS:
        return {
            "supported": True,
            "client": SUPPORTED_TERM_PROGRAMS[term_program],
            "reason": f"TERM_PROGRAM={term_program}",
        }

    if env.get("CURSOR_TRACE_ID") or env.get("CURSOR_AGENT") or env.get("CURSOR_PROCESS_ID"):
        return {"supported": True, "client": "Cursor", "reason": "CURSOR_* env detected"}

    if env.get("VSCODE_PID") or env.get("VSCODE_IPC_HOOK") or env.get("VSCODE_INJECTION"):
        return {"supported": True, "client": "VS Code", "reason": "VSCODE_* env detected"}

    if any(env.get(var) for var in JETBRAINS_HINT_VARS):
        emulator = env.get("TERMINAL_EMULATOR", "")
        if "JetBrains" in emulator or env.get("IDEA_INITIAL_DIRECTORY"):
            return {"supported": True, "client": "JetBrains IDE", "reason": "JetBrains terminal emulator"}

    term = env.get("TERM", "")
    if term == "dumb":
        return {"supported": False, "client": "terminal-puro", "reason": "TERM=dumb"}

    if env.get("SSH_CONNECTION") and not term_program:
        return {
            "supported": False,
            "client": "ssh-sem-tui",
            "reason": "SSH_CONNECTION sem TERM_PROGRAM — provavelmente terminal puro",
        }

    if not sys.stdout.isatty():
        return {
            "supported": False,
            "client": "non-tty",
            "reason": "stdout não é TTY — ambiente não interativo",
        }

    return {
        "supported": False,
        "client": "inconclusivo",
        "reason": "Nenhum sinal positivo de cliente com painel — recusa conservadora (postura A)",
    }


def main() -> int:
    try:
        result = detect()
    except Exception as exc:
        print(json.dumps({"supported": False, "client": "erro", "reason": str(exc)}))
        return 2

    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["supported"] else 1


if __name__ == "__main__":
    sys.exit(main())
