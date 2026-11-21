---
name: authoring-agent-skills
description: "Designs, scaffolds, lints and evaluates agent skills and plugins to cross-harness best practice (scripts, evals, versioning, security). Use when creating a skill, SKILL.md or plugin (including capturing a workflow as a reusable skill), splitting or restructuring one, choosing skill vs MCP vs plugin vs hook, or reviewing a skill before release. Not for ordinary code or docs."
metadata:
  version: 1.0.2
---
# Authoring agent skills

Copy this checklist and tick it off. Read each reference only at its step. `scripts/` paths are relative to this skill's folder; use `python` where `python3` is not on the PATH.

- [ ] 1. Interview
- [ ] 2. Decide the mechanism → `references/decide.md`
- [ ] 3. Write evals first → `references/evals.md`
- [ ] 4. Scaffold
- [ ] 5. Author SKILL.md + scripts → `references/authoring.md`
- [ ] 6. Runtime behavior (only if multi-step, long or stateful) → `references/runtime.md`
- [ ] 7. Lint loop
- [ ] 8. Evaluate and tune the description
- [ ] 9. Ship → `references/ship.md`
- [ ] 10. Report

Improving an existing skill? Run step 7 on it first, then start at step 3.

## 1. Interview
Ask (use a structured question tool if the harness has one) only what you cannot infer:
- The task, plus 2-3 real examples or past failures.
- Trigger phrases users would say, and near-miss requests that must NOT trigger it.
- Side effects (deploy, send, delete, publish, write outside the workspace).
- Target hosts (Cursor, Claude Code, Codex, Gemini, custom) and target models (frontier and/or local 20-70B).
- User-configurable values and secrets.
- Location: project `.agents/skills/` (or the target host's own skills folder), personal, or a plugin.

## 2. Decide
Read `references/decide.md`. Write down one line each:
- Mechanism: always-on rule / skill / MCP server / hook / subagent / plugin. If it is not a skill, say so, recommend the right mechanism, and stop.
- Split or not: separate skills only for distinct triggers, distinct side effects or distinct runtimes. Mutually exclusive variants become `references/<variant>.md`.
- Subagents: only for read-only fan-out or independent review; writes stay in one agent.

## 3. Evals first
Read `references/evals.md`. Before writing instructions:
- `evals/evals.json`: at least 3 cases from real examples, each with checkable expectations (files or state, not wording).
- `evals/trigger_evals.json`: 8-10 should-trigger queries (explicit and implicit) and 8-10 near-miss negatives.
- Run the task cases once WITHOUT the skill and record what goes wrong. Only those gaps go into the skill.

## 4. Scaffold
Run: `python3 scripts/scaffold.py --name <name> --dest <dir> --description "<what>. Use when <triggers>. Not for <near-misses>."`
Add `--plugin` to wrap the skill in portable + Claude + Cursor plugin manifests. Use `--dry-run` first if the target directory already exists.

## 5. Author
Read `references/authoring.md`. Hard rules:
- Body < 500 lines and ~5k tokens; critical rules first (only the top ~5k tokens survive compaction).
- Numbered steps + a copyable checklist; one default plus one escape hatch, never a menu.
- Only add what the model gets wrong without it (the gaps from step 3).
- Fragile, bulk or must-be-identical work goes in `scripts/`: non-interactive, `--help`, JSON on stdout, errors on stderr, distinct exit codes, idempotent, `--dry-run` if destructive. Say "Run X", never "See X".
- Destructive or batch work: plan → validate script → apply → verify.
- References one level deep, each with its load condition ("read X if Y").
- Generic verbs ("read the file", "run `python3 scripts/x.py`"), relative forward-slash paths, no harness tool names.
- Frontmatter: only `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`, unless the target host needs more (e.g. `disable-model-invocation: true` for side-effecting skills).
- No secrets in the skill; scripts read them from env or the host's secret store.

## 6. Runtime
If the skill is multi-step, long-running or stateful, read `references/runtime.md` and add:
- A progress/state file the skill re-reads on resume (survives compaction).
- One structured error format (`ERROR [code] … resolves: … next: …`), retry cap (3), and stop-and-ask conditions.
- A `learnings/` flow: agent proposes in `learnings/proposed/` using `assets/learning-entry.md`, a human accepts. Never rewrite learnings wholesale.

## 7. Lint loop
Run: `python3 scripts/lint_skill.py <skill-dir>` (add `--portable` for skills shipped to claude.ai or other hosts).
Fix every error; fix or consciously accept each warning. Re-run until exit code 0. Max 3 rounds, then report the remaining issues.

## 8. Evaluate
- Task evals: run each case with the skill and without it (or vs the previous version), ideally in clean, separate runs (one subagent each if available). Grade expectations; compare pass rate, tokens and time.
- Trigger evals: run each query 3 times in a fresh session that only sees skill names + descriptions, and record `{"query", "should_trigger", "triggered"}` per run as JSONL. Score with `python3 scripts/score_trigger_evals.py runs.jsonl`.
- Tune the description using train failures only; keep the version with the best TEST pass rate. Never paste failed queries into the description.
- If you cannot run evals in this harness, say so and leave the eval files for the user.

## 9. Ship
Read `references/ship.md`. Then:
- Side-effecting skill → user-invoked only on every target host.
- Version: SemVer in `metadata.version` (and plugin manifests); entry in `CHANGELOG.md`. Renamed skill → leave a redirect from `assets/redirect-skill.md` under the old name.
- User config via the host's plugin settings; state in the plugin data directory, never the install directory.
- Third-party or shared skill → security scan and a human review of scripts, hooks and MCP config.

## 10. Report
State: mechanism chosen and why, files created, lint result, eval results (with vs without, trigger train/test), and anything skipped with the reason.

## Gotchas
- Do not paste the best-practices material into the new skill; link only what its task needs.
- A description that names everything triggers on nothing. Lead with the user's trigger words.
- Do not reuse a name an installed built-in already has (e.g. Cursor's `create-skill`); precedence differs by host.
- Strong "MUST" wording is for invariants that evals show being broken; otherwise explain why.
- Templates in `assets/` end in `.tmpl` so they are never discovered as nested skills.
