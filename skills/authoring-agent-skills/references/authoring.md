## 3. Code in skills (deterministic coordination)
- Use a script for: sorting, copying between tools, transforms, parsing, validation, document assembly, anything that must repeat identically, or a helper the agent keeps rewriting in eval transcripts.
- Degrees of freedom, set per section: high (prose; many valid approaches, e.g. review), medium (pseudocode or parameterized script), low (exact command; fragile or order-sensitive, e.g. migrations).
- "Run X" = execute (only output costs tokens). "See X" = read as reference. Be explicit about which.
- Script contract: non-interactive (flags/env/stdin); `--help`; JSON on stdout, diagnostics on stderr; distinct exit codes; idempotent; `--dry-run` for destructive ops; reject ambiguous input; bounded output (harnesses truncate at 10–30k chars, Claude caps tool output at 25k tokens; support `--offset`/`--output`); actionable errors ("Field X not found. Available: …"); self-contained deps (PEP 723 + `uv run`, pinned `npx pkg@ver`/`uvx`); handle errors in the script; document every constant.
- Plan → validate → execute: write `plan.json` → validator checks it against the source of truth → apply → verify.
- Code execution with MCP: expose tools as a code API on the filesystem; filter in a sandbox; data flows tool-to-tool without entering the model (150k → 2k tokens). Cost: sandbox, limits, monitoring. Consolidate chained tools (`schedule_event` instead of 3 calls).
- Disagreement: Anthropic leans toward scripts; Codex: "prefer instructions unless you need determinism"; skills with scripts are 2.12× more likely vulnerable. → Use scripts where determinism matters; review and scan them.

## 5. Harness-agnostic
- Frontmatter: only `name` (1–64, lowercase-hyphen, = dir name), `description`, `license`, `compatibility` (≤500 chars), `metadata` (str→str), `allowed-tools` (experimental). claude.ai uploads reject extra keys; OpenCode ignores them.
- Host-only fields: `disable-model-invocation` (Claude, Cursor), `paths` (Cursor), `context: fork`/`model`/`effort`/`hooks`/`!cmd`/`$ARGUMENTS`/`${CLAUDE_SKILL_DIR}` (Claude only), `agents/openai.yaml` (Codex).
- Relative paths, forward slashes. Generic verbs ("read the file", "run `python scripts/x.py`"), not tool names. MCP tools as `Server:tool`.
- Discovery: `.agents/skills/` is read by Cursor, Codex, Gemini, Copilot, OpenCode. Claude Code reads only `.claude/skills` → symlink it to `.agents/skills`.
- `AGENTS.md` is canonical; `CLAUDE.md` = `@AGENTS.md`. Nested files: closest wins.
- Plugins: root `plugin.json` per Agent Plugins 1.0.0 (`$schema` required, closed schema, `extensions.<reverse-domain>`) + native manifests: `.claude-plugin/plugin.json` (`${CLAUDE_PLUGIN_ROOT}`), `.cursor-plugin/plugin.json` (`${CURSOR_PLUGIN_ROOT}`; Cursor doesn't expand `${PLUGIN_ROOT}`), `gemini-extension.json` (`${extensionPath}`). No CLAUDE.md in plugins (not loaded). `bin/` blocks claude.ai/Cowork installs.
- Fallback when scripts can't run: state needs in `compatibility` (hosts don't act on it); describe the algorithm or output schema in SKILL.md so the model can do it by hand. Claude API sandbox has no network; Deep Agents needs a sandbox backend; SEP-2640 needs approval.

## 11. Model-agnostic (frontier ~1T ↔ local 20–70B)
- Small models fail mainly from load. IFScale: best model ~68% at 500 instructions; small models decay exponentially to a 7–15% floor; all favor earlier instructions. Lost-in-the-middle: U-curve. Context Rot: focused prompts beat full on 18/18 models. Less-is-More: Llama-3.1-8B fails with 46 tools, succeeds with 19.
- Design for the smallest target: logic in scripts; numbered steps + copyable checklist; one default + escape hatch (not a menu); output template/example; few consolidated tools; JSON I/O (Ollama `format` = schema, also put the schema in the prompt); one term per concept; repeat key constraints at the step where they apply; Gotchas section in SKILL.md; core path in SKILL.md, advanced cases in triggered references.
- Local: set context explicitly (Ollama default 4k <24 GiB VRAM, 32k at 24–48 GiB; ≥64k recommended for agents); native tool template (Qwen3 → Hermes style; no stopword ReAct for reasoning models).
- No `model:` pin in portable skills. Test the matrix (Haiku/Sonnet/Opus + local), pinned in CI.
- BFCL V4 (aggregator snapshot): Opus 4.5 77.5, GLM-4.6 72.4, Qwen3-32B 48.7, Qwen3-8B 42.6, Mistral Small 3.2 37.2.
- Caveat: no study directly tests numbered steps on 20–70B models; this is inferred from the research above.

## 12. Token efficiency
- Budgets: metadata ~100 tokens; body <5k; references 0 until read. The body is a recurring cost on every later turn.
- Per paragraph: "would the agent get this wrong without it?" Skip what the model already knows.
- Execute, don't load; point to files, don't inline; filter in code; `response_format: concise|detailed` (concise ≈ ⅓ tokens); pagination; bounded script output.
- Cache: prefix order tools → system → messages; changing a tool definition invalidates everything; put timestamps and per-request data after the last breakpoint; 20-block lookback; minimum 512–4,096 tokens by model. Don't let hooks or skills mutate tool lists or system text mid-session.
- `disable-model-invocation: true` removes the description from context; `user-invocable: false` hides from the menu but keeps the description.
- Descriptions: pushy but ≲400 chars, use case first.
- Measure: `/skill-doctor`, skill-creator benchmarks, `cache_read_input_tokens`.

## 15. Triggering / description (added)
- Third-person what + "Use when…" + "Not for…" boundaries. Keywords, file types, synonyms. Trigger words first. No XML. Hyphenated names without `helper`/`utils`/`claude`/`anthropic`, and no `org:` prefixes (VS Code fails silently). Use host scoping (Cursor `paths`, Claude `when_to_use`).
- Validate with trigger evals (§8).

## 18. Composition between skills (added)
- Reference other skills by namespaced name (`/plugin:skill`); nested invocation is native (Claude logs `nested-skill`).
- Contract = file + schema: A writes `out/x.json`; B validates it with a bundled script and fails with an actionable error. No spec defines inter-skill contracts (recommendation).
- Router skills: thin, choose only, and name sub-skills explicitly. No host detects cycles → lint in CI + `skills-ref validate`.
- Plugin dependencies (Claude Code only): `dependencies` (string | `name@marketplace` | `{name, version:"~2.1.0", marketplace}`), resolved against `<plugin>--v<ver>` tags; conflicting ranges fail the install; cross-marketplace dependencies need `allowCrossMarketplaceDependenciesOn`. Bundle plugins (name + dependencies only) work as role kits. Agent Plugins 1.0.0, Cursor, and Codex have no plugin dependencies; Codex has skill→MCP `agents/openai.yaml` `dependencies.tools`.
- Skill + MCP: ship them in the same plugin so they version together; across plugins, declare a dependency so tool renames don't silently break.
- Subagents: Claude `skills:` frontmatter preloads full bodies (first 32; `disable-model-invocation` skills excluded). Inverse: skill `context: fork` + `agent:`.
- Name precedence differs (project>user is the convention; Gemini workspace>user>extension>built-in; Codex keeps duplicates) → unique names only.
```json
{"name":"deploy-kit","version":"3.1.0","dependencies":["audit-logger",{"name":"secrets-vault","version":"~2.1.0"},{"name":"db-migrate","version":"^3.0","marketplace":"acme-shared"}]}
```

## Reference layout
```text
AGENTS.md                         # CLAUDE.md = "@AGENTS.md"
.agents/skills/<name>/            # .claude/skills -> ../.agents/skills
.claude-plugin/marketplace.json   # internal marketplace (pinned refs, renames); Codex reads it too
.github/CODEOWNERS                # plugins/*/ owners
plugins/my-plugin/
├── plugin.json                   # Agent Plugins 1.0.0, strict semver
├── CHANGELOG.md                  # deprecations + removal dates
├── .claude-plugin/plugin.json    # userConfig, hooks
├── .cursor-plugin/plugin.json
├── gemini-extension.json
├── mcp.json
└── skills/doc-writer/
    ├── SKILL.md                  # <500 lines; checklist, gotchas, "read X if Y"
    ├── references/               # 1 level deep
    ├── scripts/                  # executed; JSON out; --dry-run; idempotent
    ├── assets/                   # templates
    ├── evals/{evals.json,trigger_evals.json}
    └── learnings/{proposed/,accepted.jsonl}
```
