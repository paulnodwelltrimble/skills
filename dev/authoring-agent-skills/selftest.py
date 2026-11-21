#!/usr/bin/env python3
"""Self-check for the authoring-agent-skills scripts. Usage: python3 dev/authoring-agent-skills/selftest.py  (exit 0 = all pass)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parents[2] / "skills" / "authoring-agent-skills"
HERE = SKILL / "scripts"


def run(script: str, *args: str) -> tuple[int, dict]:
    p = subprocess.run([sys.executable, str(HERE / script), *args], capture_output=True, text=True)
    return p.returncode, json.loads(p.stdout) if p.stdout.strip() else {}


with tempfile.TemporaryDirectory() as tmp:
    t = Path(tmp)

    code, out = run("lint_skill.py", str(SKILL))
    assert code == 0, f"this skill must lint clean: {out}"

    code, out = run("scaffold.py", "--name", "demo-skill", "--dest", tmp, "--description", "Does X. Use when Y. Not for Z.", "--plugin")
    sk = t / "demo-skill" / "skills" / "demo-skill"
    assert code == 0 and (sk / "SKILL.md").is_file() and (t / "demo-skill" / ".claude-plugin" / "plugin.json").is_file(), out
    assert run("scaffold.py", "--name", "demo-skill", "--dest", tmp, "--description", "x", "--plugin")[0] == 1, "must refuse overwrite"
    code, out = run("lint_skill.py", str(sk))
    assert code == 1 and any("TODO" in e for e in out["errors"]), "unfilled template TODO paths must fail lint"

    bad = t / "bad-skill"
    (bad / "scripts").mkdir(parents=True)
    (bad / "SKILL.md").write_text("---\nname: wrong-name\ndescription: I can help you.\nfoo: 1\n---\n" + "line\n" * 600)
    (bad / "scripts" / "go.py").write_text("x = inp" + 'ut("continue? ")\n')  # split so this file doesn't trip the linter
    code, out = run("lint_skill.py", str(bad), "--portable")
    errs = " ".join(out["errors"])
    assert code == 1 and all(s in errs for s in ("must match directory", "lines", "'foo'", "interactive")), out

    runs = t / "runs.jsonl"
    runs.write_text("\n".join(json.dumps({"query": f"q{i}", "should_trigger": i % 2 == 0, "triggered": i % 2 == 0 or i == 1})
                              for i in range(20) for _ in range(3)))
    code, out = run("score_trigger_evals.py", str(runs))
    assert code == 0 and [f["query"] for f in out["failures"]] == ["q1"], out

print("selftest: all checks passed")
