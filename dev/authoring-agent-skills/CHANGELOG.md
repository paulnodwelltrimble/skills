# Changelog

## 1.1.0 (2026-11-21)
- Lint: a `references/`, `scripts/` or `assets/` path is checked wherever it appears, so a missing script named inside a command (`python3 scripts/x.py`) is now an error. Before, only a path directly after a backtick was checked.
- Lint: new `--evals-dir DIR` for repositories that keep evals outside the skill folder.
- Lint: a `trigger_evals.json` that is not an array of objects is reported as an error; it used to raise a traceback.
- Scaffold: the new skill gets `assets/learning-entry.md`, which its `learnings/README.md` names. The "files exist" error goes to stderr.
- References: `ship.md` now holds configuration, versioning and security. Telemetry, deprecation and distribution moved to the new `distribute.md`, which step 9 loads only when needed.
- References are edited by hand from now on. The page they were generated from is lost, so `sync_references.py` and the "generated, do not edit" headers are removed.
- SKILL.md: the 5k-token compaction limit is described as the behaviour of some hosts. Removed a dated claim from the distribution reference.
- Eval 3 reviews a fixture skill, `evals/files/fixture-skills/changelog-writer/`, with planted defects; `selftest.py` checks the linter finds each one.
- Trigger evals: three queries added (two positive, one negative) that the description was never tuned on. The 1.0.1 description fix added words close to a failed query, which the skill's own rule forbids, so the 18/18 figure below is not a held-out score.
- Not run: task evals and trigger evals. Re-run the trigger evals and record the train and test pass rates before changing the description again.

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
