#!/usr/bin/env python3
"""
Consolida o log de aprendizado de uma sessão SavyCode em arquivo .docx.

Uso:
    python3 consolidate_to_docx.py \
        --log <caminho/do/log.md> \
        --project <caminho/do/projeto> \
        [--profile ~/.claude/savycode/knowledge-profile.json]

O arquivo gerado vai em: <projeto>/learning-journal/<basename-do-log>.docx

Dependência: python-docx (pip install python-docx). Se ausente, gera fallback .md formatado.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def load_profile(profile_path: Path) -> dict:
    if not profile_path.exists():
        return {"level": 1, "topics": {}, "weak_areas": []}
    return json.loads(profile_path.read_text(encoding="utf-8"))


def parse_log(log_path: Path) -> dict:
    """Extrai seções do log markdown.

    Estrutura esperada do log:
        # Sessão: <prompt original>
        ## Construção: <nome>
        - **O que é:** ...
        - **Por que aqui:** ...
        - **Vai aprender depois:** ...

        ## Código gerado
        ```<lang>
        <code>
        ```
    """
    text = log_path.read_text(encoding="utf-8")
    sections = {
        "title": "Sessão sem título",
        "prompt_original": "",
        "constructs": [],
        "code_blocks": [],
        "lessons": [],
    }

    title_match = re.search(r"^#\s+Sessão:\s+(.+)$", text, re.MULTILINE)
    if title_match:
        sections["title"] = title_match.group(1).strip()
        sections["prompt_original"] = title_match.group(1).strip()

    for m in re.finditer(
        r"^##\s+Construção:\s+`?([^`\n]+)`?\s*\n((?:- .+\n?)+)",
        text,
        re.MULTILINE,
    ):
        sections["constructs"].append({"name": m.group(1).strip(), "body": m.group(2).strip()})

    for m in re.finditer(r"```(\w*)\n(.*?)```", text, re.DOTALL):
        sections["code_blocks"].append({"lang": m.group(1) or "text", "code": m.group(2)})

    for m in re.finditer(r"^##\s+Lição:\s+(.+)$", text, re.MULTILINE):
        sections["lessons"].append(m.group(1).strip())

    return sections


def write_docx(out_path: Path, sections: dict, profile: dict) -> bool:
    try:
        from docx import Document  # type: ignore
        from docx.shared import Pt, RGBColor
    except ImportError:
        return False

    doc = Document()

    title = doc.add_heading(f"Aprendizado: {sections['title']}", level=0)

    meta = doc.add_paragraph()
    meta.add_run(f"Gerado em: {datetime.utcnow().isoformat()}Z").italic = True
    meta.add_run(f"\nNível atual: {profile.get('level', 1)}").italic = True

    doc.add_heading("1. Contexto / Prompt original", level=1)
    doc.add_paragraph(sections["prompt_original"] or "(prompt não capturado)")

    if sections["code_blocks"]:
        doc.add_heading("2. Código gerado", level=1)
        for blk in sections["code_blocks"]:
            doc.add_paragraph(f"Linguagem: {blk['lang']}").italic = True
            p = doc.add_paragraph()
            run = p.add_run(blk["code"])
            run.font.name = "Menlo"
            run.font.size = Pt(9)

    if sections["constructs"]:
        doc.add_heading("3. Significado de cada construção", level=1)
        for c in sections["constructs"]:
            doc.add_heading(c["name"], level=2)
            doc.add_paragraph(c["body"])

    if sections["lessons"]:
        doc.add_heading("4. Lições principais", level=1)
        for lesson in sections["lessons"]:
            doc.add_paragraph(lesson, style="List Bullet")

    doc.add_heading("5. Próximos estudos sugeridos", level=1)
    weak = profile.get("weak_areas", [])
    if weak:
        for area in weak:
            doc.add_paragraph(area, style="List Bullet")
    else:
        doc.add_paragraph("Nenhuma área fraca destacada no perfil atual.")

    doc.save(str(out_path))
    return True


def write_markdown_fallback(out_path: Path, sections: dict, profile: dict) -> None:
    md_path = out_path.with_suffix(".md")
    lines = [
        f"# Aprendizado: {sections['title']}",
        "",
        f"_Gerado em: {datetime.utcnow().isoformat()}Z_",
        f"_Nível atual: {profile.get('level', 1)}_",
        "",
        "## 1. Contexto / Prompt original",
        sections["prompt_original"] or "(prompt não capturado)",
        "",
    ]
    if sections["code_blocks"]:
        lines.append("## 2. Código gerado")
        for blk in sections["code_blocks"]:
            lines.append(f"```{blk['lang']}")
            lines.append(blk["code"])
            lines.append("```")
            lines.append("")
    if sections["constructs"]:
        lines.append("## 3. Significado de cada construção")
        for c in sections["constructs"]:
            lines.append(f"### {c['name']}")
            lines.append(c["body"])
            lines.append("")
    if sections["lessons"]:
        lines.append("## 4. Lições principais")
        for lesson in sections["lessons"]:
            lines.append(f"- {lesson}")
        lines.append("")
    lines.append("## 5. Próximos estudos sugeridos")
    for area in profile.get("weak_areas", []) or ["Nenhuma área fraca destacada."]:
        lines.append(f"- {area}")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"python-docx não instalado. Gerado fallback markdown: {md_path}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", required=True, type=Path, help="Caminho do log .md da sessão")
    parser.add_argument("--project", required=True, type=Path, help="Raiz do projeto (onde criar learning-journal/)")
    parser.add_argument(
        "--profile",
        type=Path,
        default=Path.home() / ".claude" / "savycode" / "knowledge-profile.json",
        help="Caminho do knowledge-profile.json",
    )
    args = parser.parse_args()

    if not args.log.exists():
        print(f"Log não encontrado: {args.log}", file=sys.stderr)
        return 1

    target_dir = args.project / "learning-journal"
    target_dir.mkdir(parents=True, exist_ok=True)
    out_path = target_dir / (args.log.stem + ".docx")

    sections = parse_log(args.log)
    profile = load_profile(args.profile)

    if write_docx(out_path, sections, profile):
        print(f"OK: {out_path}")
    else:
        write_markdown_fallback(out_path, sections, profile)

    return 0


if __name__ == "__main__":
    sys.exit(main())
