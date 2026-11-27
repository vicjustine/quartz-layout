"""Validate a screen layout graph and report diagnostic the editor can parse.
Output format is file:line:column:severity:code:message, which the custom
problem matcher in .vscode/task.json turns into Problems-panel entries. 

"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SOURCE = Path("layout.json")
MAX_DEPTH = 3

def line_of(text: str, needle: str, start: int = 0) -> int: 
    index = text.find(needle, start)
    return text.count("\n", 0, index) + 1 if index >= 0 else 1


def report(line: int, severity: str, code: str, message: str) -> None: 
    print(f"{SOURCE}:{line}:1:{severity}:{code}:{message}")

def main() -> int: 
    raw = SOURCE.read_text(encoding="utf-8")
    data = json.loads(raw)
    screens = data["screens"]
    widgets = {w["id"] for w in data["widgets"]}

    errors = 0
    seen: dict[str, int] = {}

    for screen in screens: 
        sid = screen["id"]
        line = line_of(raw, f'"id": "{sid}"', 0 if sid not in seen else seen[sid])

        if sid in seen: 
            report(line, "error", "QL201", f"Duplicate screen id {sid!r}")
            errors += 1
        seen[sid] = line

        parent = screen["parent"]
        if parent is not None and parent not in {s["id"] for s in screens}: 
            report(line, "error", "QL202", f"Screen {sid!r} references unknown parent {parent!r}")
            errors += 1

        for widget in screen["widgets"]: 
            if widget not in widgets: 
                report(line, "warning", "QL101", f"Screen {sid!r} uses undeclated widget {widget!r}")

    for screen in screens: 
        depth, cursor, guard = 0, screen, 0
        index = {s["id"]: s for s in screens}
        while cursor ["parent"] is not None and guard < 20: 
            nxt = index.get(cursor["parent"])
            if nxt is None: 
                break
            cursor, depth, guard = nxt, depth + 1, guard + 1
        if depth > MAX_DEPTH:
            report(line_of(raw, f'"id": "{screen["id"]}"'), "warning", "QL102", 
                   f"Screen {screen['id']!r} nest {depth} level, limit {MAX_DEPTH}")

    print(f"checked {len(screens)} screens, {errors} error(s)")
    return 1 if errors else 0 

if __name__ == "__main__": 
    sys.exit(main())


                    
