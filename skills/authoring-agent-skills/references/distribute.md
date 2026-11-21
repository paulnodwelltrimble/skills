## 17. Observability / telemetry (added)
- Enable host telemetry from **managed** settings (dev settings can switch signals off).
- "Was it triggered?":
  - Claude Code: `claude_code.skill_activated` (`skill.name`, `invocation_trigger` = `user-slash`/`claude-proactive`/`nested-skill`, `skill.source`, `plugin.name`); `plugin_loaded`, `subagent_completed`, `tool_result`, `tool_decision`; `cost.usage`/`token.usage` attributed by skill, plugin, and agent.
  - Codex: `skill.injected{status,skill}`, `thread.skills.truncated` (the listing budget was cut), `codex.tool_result`.
  - Gemini CLI: no skill event; filter `gemini_cli.tool_call` on `function_name=activate_skill` (inferred).
  - Cursor: no documented skill telemetry (unverified).
- Claude redacts non-official names to `third-party`/`custom_skill` (your org marketplace included) → set `OTEL_LOG_TOOL_DETAILS=1` in managed env.
- Traces: Claude beta (`CLAUDE_CODE_ENHANCED_TELEMETRY_BETA=1`); Bash subprocesses inherit `TRACEPARENT` → skill scripts should emit child spans. Codex needs a separate `trace_exporter`.
- OTel GenAI (Development): on `execute_tool` spans use `gen_ai.skill.name`, `.description`, `.source.uri` (stable URI, not a temp path), `.resource.name`; span name `execute_tool {tool} {skill} {resource}`. There is **no `gen_ai.skill.version`** → add a custom `skill.version`.
- Backends: Langfuse `langfuse.trace.metadata.<k>` (filterable; plain attributes aren't); Braintrust `braintrust.metadata.*`/`braintrust.tags`; LangSmith `metadata`/`tags` + `LANGSMITH_REVISION_ID`.
- Script logs: data on stdout, diagnostics on stderr; optionally append a JSONL line `{skill, version, event, exit_code, ms}` to stderr or `${CLAUDE_PLUGIN_DATA}` (recommendation).
- Privacy defaults: Claude redacts prompts and tool details; Codex redacts prompts but **logs tool args and output** (drop them in the collector); Gemini **logs prompts** (`GEMINI_TELEMETRY_LOG_PROMPTS=false`).
- Close the loop: failing production trace → eval case (`evals.json` / `claude plugin eval` / Braintrust "add trace to dataset") → fix → regression suite.
- Pre-ship cost check: `claude plugin details <name>` (always-on vs per-invocation tokens); `/skill-doctor` (never-run skills).
```json
{"env":{"CLAUDE_CODE_ENABLE_TELEMETRY":"1","OTEL_METRICS_EXPORTER":"otlp","OTEL_LOGS_EXPORTER":"otlp","OTEL_EXPORTER_OTLP_ENDPOINT":"https://otel.corp:4318","OTEL_LOG_TOOL_DETAILS":"1","OTEL_RESOURCE_ATTRIBUTES":"department=platform"}}
```

## 19. Deprecation / end of life (added)
- No host has a "deprecated" plugin state. Per host:
  - Claude Code: marketplace `renames` (append-only; rewrites users' `enabledPlugins` + `pluginConfigs`; cycles rejected); `"old": null` + `forceRemoveDeletedPlugins: true` removes.
  - Gemini: `migratedTo` moves the install source.
  - Claude Enterprise: set "Hidden entirely".
  - Codex: `policy.installation: "NOT_AVAILABLE"`.
  - Cursor: drop from team marketplace or Required→Default Off (removing a linked MCP plugin can delete the Team MCP server).
  - MCP Registry: immutable versions, `active`/`deprecated`/`deleted` + `statusMessage`.
- Redirect skill (convention): keep the old name for 1–2 releases, `user-invocable: false`, description starts with `DEPRECATED (removal <date>). Use <new>`, body = "load and follow `<new>`; do not perform the task here".
- Deprecate in a minor release, remove in a major; announce the removal date in the description + CHANGELOG.
- State: keep it in `PLUGIN_DATA` and migrate on first run of the new version (uninstall deletes it unless `--keep-data`).
- Retire using data: `/plugin` "Not used recently" (14 days + 10 sessions), `/skill-doctor`, Enterprise Analytics API `GET /v1/organizations/analytics/plugins`, telemetry from §17.
```json
{"name":"acme","owner":{"name":"Platform"},"plugins":[{"name":"code-formatter","source":"./plugins/code-formatter"}],"renames":{"formatter":"code-formatter","legacy-linter":null},"forceRemoveDeletedPlugins":true}
```

## 20. Distribution & governance (added)
- Internal marketplace in a private repo:
  - Claude `.claude-plugin/marketplace.json` (`name`, `owner`, `plugins`); pin `ref`/`sha`, archives `sha256` (integrity failure refuses install).
  - Codex `.agents/plugins/marketplace.json` with `policy.installation` `AVAILABLE`/`INSTALLED_BY_DEFAULT`/`NOT_AVAILABLE`; Codex also reads the Claude file.
  - Cursor team marketplaces (Teams 1, Enterprise unlimited): Default Off/On/Required per SCIM group; auto refresh ≤10 min; "serve from Cursor" removes the need for GitHub access; Enterprise local plugin imports off by default.
- Channels: no host has them → two marketplaces (`stable`, `latest`) at different refs.
- Lockdown:
  - Claude managed settings: `strictKnownMarketplaces` allowlist (`[]` = block all; `blockedMarketplaces` checked first; keep `{source:"skills-dir"}`), `extraKnownMarketplaces` + `enabledPlugins` (force-install / `false` blocks), `disableSideloadFlags`, `strictPluginOnlyCustomization`, `allowManagedHooksOnly`, `pluginTrustMessage`.
  - Codex `requirements.toml` `[marketplaces] restrict_to_allowed_sources = true`.
- Org provisioning:
  - Claude Enterprise: Installed by default/Available/Hidden/Required with group overrides; GitHub sync only on merged PRs with a version bump (a failed sync keeps the last version).
  - Copilot: repo or personal scope only (no org skills dir found); `gh skill` (preview) supports `@TAG`/`@SHA` `--pin` and writes provenance into frontmatter.
- Review workflow: CODEOWNERS on `plugins/*/`, protected tags, and CI running `claude plugin validate` → `skills-ref validate` → skill-scanner → `claude plugin eval --threshold` → `claude plugin tag --push`. A human reads `hooks.json`, `.mcp.json`, `bin/` before approving.
- Ownership: manifest `owner`/`author`; SKILL.md `metadata: {owner, version, support-channel}` (hosts ignore it, so it's safe for your own tooling).
- Integrity: only Claude archive `sha256` and SEP-2640 digests verify content; others pin git refs only.
```json
{"strictKnownMarketplaces":[{"source":"github","repo":"acme/*"},{"source":"skills-dir"}],"extraKnownMarketplaces":{"acme-stable":{"source":{"source":"github","repo":"acme/plugins","ref":"stable"},"autoUpdate":true}},"enabledPlugins":{"backend-standard@acme-stable":true},"disableSideloadFlags":true}
```
