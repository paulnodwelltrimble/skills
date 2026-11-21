## 10. User configuration
- Not in SKILL.md frontmatter (no host reads it as config).
- Claude `userConfig`: `type`, `title`, `description` (required), `default`, `required`, `options`, `min`/`max`, `sensitive`. Non-sensitive values → `settings.json` `pluginConfigs`; sensitive → OS keychain. `${user_config.KEY}` substituted into bodies (non-sensitive only); hooks get `CLAUDE_PLUGIN_OPTION_<KEY>`.
- Gemini: `settings[]` with `envVar` + `sensitive` → extension `.env` / keychain; `gemini extensions config --scope`; restart needed. Agent Plugins: no core config field (use `extensions.*`).
- Secrets never pass through the model: scripts or MCP servers read them. MCP: never request secrets via form-mode elicitation; use URL mode.
- Assume no inherited env (Gemini allowlists; Claude doesn't pass plugin vars to Bash).
- State and config go in `${CLAUDE_PLUGIN_DATA}` (survives updates) or XDG, never in `${CLAUDE_PLUGIN_ROOT}` (changes on every update).
- Scripts read config at run time (SKILL.md is loaded once per session).
- Ask once, persist: script fails fast naming the missing value → agent asks → writes config → re-runs.
- Precedence (highest first): CLI flag > env > project.local (gitignored) > project > user > default. Lists merge, scalars override.
```jsonc
// ${CLAUDE_PLUGIN_DATA}/config.json | .tool.json (committed) + .tool.local.json (gitignored); no secrets
{ "schema_version": 2, "severity_floor": "medium", "output_format": "markdown" }
```

## 13. Versioning
- Version at the plugin level. The skill spec has no `version`; no client reads `metadata.version`.
- Strict SemVer. Major: rename, trigger-scope change, removed script or flag, config schema break. Minor: new optional config or reference, deprecation. Patch: wording fixes that pass evals. Never mutate a release; deprecate in a minor, remove in a major.
- Hosts differ: Codex rejects non-semver; Claude doesn't check, pins users until the string changes (commits without a bump ship nothing), and omitting `version` tracks the SHA. Don't set it in both `plugin.json` and the marketplace (plugin.json wins silently). `claude plugin validate --strict` fails on a missing version. → Always set strict semver and bump every release.
- Pin via ref/SHA or `sha256`. Tag `<plugin>--v<ver>` (`claude plugin tag --push`); ranges like `~2.1.0`; pre-releases need `^2.0.0-0`. Channels = two marketplaces (stable, latest).
- Deprecate: Gemini `migratedTo`; an "Old patterns" `<details>` section; `defaultEnabled` changes don't reach existing users.
- Config and lessons carry `schema_version`, with an idempotent `scripts/migrate_config.py` on first use after upgrade (synthesis, unsourced).
- Release gate: `claude plugin validate --strict && claude plugin eval --model <pinned> --threshold 0.9 --trust-plugin && claude plugin tag --push`.

## 14. Security & trust (added)
- Data: Snyk ToxicSkills (3,984 skills): 36.8% flawed, 13.4% critical, 76 malicious (91% also used prompt injection). Skill-Inject: up to 80% attack success on frontier models. Wild study (31k skills): 26.1% vulnerable; skills with scripts 2.12× more. Context Matters: raw scanner rates are upper bounds (46.8% flagged → 0.52% suspicious with repo context).
- `allowed-tools` pre-approves tools for the turn only; it does NOT restrict which tools are available. Restrict with `disallowed-tools` / deny rules. Scope narrowly: `Bash(${CLAUDE_SKILL_DIR}/scripts/x.sh *)`, never `Bash(*)`.
- Plugin hooks, monitors, and MCP/LSP servers run outside the sandbox with full user permissions; `bin/` joins PATH; auto-update can change reviewed code. Review `hooks.json`, `.mcp.json`, `bin/`.
- Side-effecting skills (deploy, send, commit): `disable-model-invocation: true` / Codex `allow_implicit_invocation: false`. Gemini ignores self-approve policies; `excludeTools` blocks commands.
- Gate project skills on folder trust. Pin SHAs. Watch for repo hijacking, ASCII smuggling, and fake "prerequisite installer" lures.
- CI scan: Cisco `skill-scanner` with `use_llm` on (rules alone catch ~8%); `low-noise` policy, fail at HIGH for own skills. No findings ≠ no risk.
- OWASP LLM01 (injection), LLM03 (supply chain), LLM06 (excessive agency). MCP tool annotations (`readOnlyHint`, `destructiveHint`, …) are untrusted unless the server is trusted.
