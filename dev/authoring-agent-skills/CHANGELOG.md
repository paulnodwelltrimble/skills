# Changelog

## 1.0.2 (2026-11-21)
- Packaged for this repository: the skill is in `skills/authoring-agent-skills/`; evals, learnings, `selftest.py` and `sync_references.py` are in `dev/authoring-agent-skills/`.
- Commands use `python3`, which is the name present on Linux and macOS.
- The Interview step names `.agents/skills/` as the project location, not one host's folder.
- Removed `metadata.owner` and the "Maintaining this skill" section from SKILL.md; steps 6 and 9 now point at the learning-entry and redirect templates.
- Not re-run: task and trigger evals. The description is unchanged.

## 1.0.1 (2026-11-01)
- Description: add "SKILL.md" / "capturing a workflow as a reusable skill" triggers (lost 2/3 runs to built-in create-skill); shorten boundary clause.
- Eval 4: add enforcement expectation (was non-discriminating).
- Lint: skip --help check for test_*/selftest scripts.
- Iteration-1 results: task evals with skill 11/11 vs without 7/11; trigger 18/18 x3 after fix (was 17/18).

## 1.0.0 (2026-10-30)
- Initial version: 10-step workflow, generated phase references, lint/scaffold/trigger-score/sync scripts, self-evals.
