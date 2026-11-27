""" Render the validated layout graph to a summary artifact."""

from __future__ import annotations

import json
from pathlib import Path

data = json.loads(Path("layout.json").read_text(encoding="utf-8"))
screens = data["screens"]
index = {s["id"]: s for s in screens}

def depth_of(screen: dict) -> int: 
    depth, cursor = 0, screen
    while cursor ["parent"] is not None and depth < 20: 
        cursor = index.get(cursor["parent"])
        if cursor is None: 
            break
        depth += 1
    return depth

lines = ["screen,parent,depth,widgets"]
for screen in sorted(screens, key=lambda s: (depth_of(s), s["id"])):
    lines.append(
        f"{screen['id']},{screen['parent'] or '-'},{depth_of(screen)},"
        f"{' '.join(screen['widgets'])}"
    )

Path("layout-summary.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote layout-summary.csv with {len(screens)} screens")

""" layout-summary.csv should not create. This proves that validation gate works """