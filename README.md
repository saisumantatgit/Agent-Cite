# Agent-Cite

> **Cite it or it's opinion.**
> Evidence enforcement for AI agent workflows — every claim, every source, zero uncited inference.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Commands](https://img.shields.io/badge/Commands-3-orange.svg)](#commands)
[![Platforms](https://img.shields.io/badge/Platforms-5-purple.svg)](#platform-support)

---

## The Problem

AI agents hallucinate. They state facts that don't exist, cite numbers they invented, and claim "not found" without actually searching. The output looks confident. The citations look real. But when you check — the file doesn't exist, the number has no source, and the "unfound" thing is sitting right there.

**You can't distinguish a real claim from a hallucinated one unless every claim cites its source.**

Agent-Cite enforces that standard. Not as a suggestion — as a requirement.

---

## Without vs. With Agent-Cite

### What Claude/Codex Does WITHOUT Agent-Cite

| Behavior | Result |
|----------|--------|
| "I'll try to cite sources" | Best effort — cites some, silently skips others |
| No systematic scan | Misses violations without knowing it missed them |
| Can't verify its own citations | Citations may point to files that don't exist |
| No structured report | Just prose with maybe some references |
| No pass/fail verdict | No gate — just a suggestion |
| Next session, forgets the standard | Back to zero |

### What Claude/Codex Does WITH Agent-Cite

| Behavior | Result |
|----------|--------|
| **Systematic scan** of every statement | Categorized as factual claim, number, or absence claim |
| **Named violations** for every miss | UNCITED_INFERENCE, UNVERIFIED_NUMBER, UNSUPPORTED_ABSENCE |
| **Source verification** | Checks cited file paths actually exist on disk |
| **Structured report** | Summary table, violation list, line numbers, suggested fixes |
| **COMPLIANT / NON_COMPLIANT** | Binary verdict — not a suggestion |
| **`/cite-fix` reads the actual codebase** | Proposes real `file:line` citations, not guesses |
| **Configurable protocol** | `evidence-protocol.yaml` persists rules across sessions |
| **Project-wide scoring** | `/cite-report` gives evidence coverage like test coverage |

### The Analogy

| Domain | Without Tool | With Tool |
|--------|-------------|-----------|
| Testing | "Please write tests" | **Jest/Pytest** — runs them, reports coverage, blocks on failure |
| Linting | "Please format nicely" | **ESLint/Prettier** — enforces rules, auto-fixes, CI gate |
| Security | "Please write secure code" | **Snyk/Semgrep** — scans, names vulnerabilities, blocks merge |
| **Evidence** | **"Please cite sources"** | **Agent-Cite** — scans, names violations, blocks on uncited inference |

**Without Agent-Cite, citation is a request. With it, citation is a requirement.**

---

## Commands

| Command | When | What It Does |
|---------|------|-------------|
| **`/cite-audit`** | After AI generates output | Scan for uncited claims, return COMPLIANT or NON_COMPLIANT |
| **`/cite-fix`** | After violations found | Search codebase for real sources, propose accurate citations |
| **`/cite-report`** | Periodic health check | Project-wide evidence coverage score and worst offenders |

### Example

```bash
/cite-audit @docs/report.md --strict
```

Output:
```
## Evidence Audit Report
### Verdict: NON_COMPLIANT

| Category | Total | Cited | Violations |
|----------|-------|-------|------------|
| Factual claims | 23 | 15 | 8 |
| Numbers/stats | 7 | 2 | 5 |
| Absence claims | 3 | 0 | 3 |

Fix with: /cite-fix @docs/report.md
```

```bash
/cite-fix @docs/report.md
```

Output:
```
| # | Line | Violation | Proposed Fix | Confidence |
|---|------|-----------|-------------|------------|
| 1 | L42 | UNCITED_INFERENCE | [source: src/config.py:15] | HIGH |
| 2 | L67 | UNVERIFIED_NUMBER | [derived: tests/bench.py:23] | MEDIUM |
| 3 | L89 | FALSE_ABSENCE | tests/test_module.py EXISTS (12 tests) | CRITICAL |
```

---

## Violation Types

| Type | Severity | What It Catches |
|------|----------|----------------|
| `UNCITED_INFERENCE` | error | "The system uses Redis" — WHERE does it say that? |
| `UNVERIFIED_NUMBER` | warning | "500 req/sec" — WHERE is that number from? |
| `UNSUPPORTED_ABSENCE` | warning | "No tests exist" — DID you actually look? |
| `BROKEN_CITATION` | error | `[source: data/old.json]` — that file doesn't exist |
| `FALSE_ABSENCE` | critical | "No tests exist" — but `tests/test_module.py` has 12 tests |
| `UNVERIFIABLE` | human decision | No source found anywhere — the claim may be fabricated |

---

## When to Use / When NOT to Use

### Use Agent-Cite on:

- AI-generated reports and analyses
- AI-generated documentation and READMEs
- AI-generated recommendations and summaries
- Data classification outputs
- PR descriptions with factual claims
- Any AI output that says "X is true"

### Do NOT use Agent-Cite on:

- Pure code (functions, classes, modules)
- Formatting or refactoring changes
- Boilerplate and scaffolding
- Creative writing

**The rule:** If the output **asserts facts**, cite it. If it just **does something**, don't.

---

## Installation

```bash
# Clone
git clone https://github.com/saisumantatgit/Agent-Cite.git

# Install into your project (auto-detects your CLI)
cd your-project/
bash /path/to/Agent-Cite/install.sh
```

Or for Claude Code, install as a plugin:

```bash
cp -r Agent-Cite/ ~/.claude/plugins/agent-cite/
```

### What Gets Installed

| CLI Tool | What Gets Installed |
|----------|-------------------|
| **Claude Code** | `.claude/commands/*.md` + agents + skills + hook |
| **Codex** | Appends to `AGENTS.md` |
| **Cursor** | `.cursor/rules/cite.md` |
| **Aider** | Appends to `.aider.conf.yml` |
| **Generic** | Raw prompt files |

Plus: `evidence-protocol.yaml` (configurable rules) and reference docs.

---

## Configuration

Create `evidence-protocol.yaml` in your project root (a template is installed automatically):

```yaml
severities:
  UNCITED_INFERENCE: error      # Always fails
  UNVERIFIED_NUMBER: warning    # Fails only with --strict
  UNSUPPORTED_ABSENCE: warning
  BROKEN_CITATION: error

include:
  - "docs/**/*.md"
  - "data/**/*.json"

exclude:
  - "CHANGELOG.md"
  - "node_modules/**"

thresholds:
  healthy: 90      # ≥90% = HEALTHY
  needs_work: 60   # 60-89% = NEEDS_WORK
  critical: 0      # <60% = CRITICAL
```

---

## Platform Support

| Platform | Config | Notes |
|----------|--------|-------|
| Claude Code | `.claude-plugin/plugin.json` | Full support (agents + commands + skills) |
| Codex | `AGENTS.md` | Prompt-based |
| Cursor | `.cursor/rules/cite.md` | Rules-based |
| Aider | `.aider.conf.yml` | Config-based |
| Generic | `prompts/*.md` | Paste into any LLM |

---

## Part of the Agent Suite

| Tool | What It Does | Tagline |
|------|-------------|---------|
| [**Agent-PROVE**](https://github.com/saisumantatgit/Agent-PROVE) | Makes agents think before they act | "Prove it or it fails." |
| [**Agent-Trace**](https://github.com/saisumantatgit/Agent-Trace) | Makes agents see before they edit | "See the ripple effect before it happens." |
| [**Agent-Scribe**](https://github.com/saisumantatgit/Agent-Scribe) | Makes agents remember what they learned | "Nothing is lost." |
| **Agent-Cite** | Makes agents prove what they claim | "Cite it or it's opinion." |

PROVE validates your thinking. Trace maps your blast radius. Scribe records your decisions. **Cite enforces your evidence.** Together: think rigorously, edit safely, remember everything, prove every claim.

**Note:** Agent-PROVE includes basic evidence auditing (`/audit` command). Agent-Cite is the standalone deep dive — citation fix, project-wide reporting, configurable protocol. If you already use PROVE, Agent-Cite adds the remediation and reporting PROVE doesn't have.

---

## Origin

Built from the evidence protocol methodology that powered the Agent-PROVE project — where zero uncited inference was enforced across 1,086 regulatory data points. The protocol caught fabricated numbers, false absence claims, and citations to files that no longer existed. Agent-Cite generalizes that discipline for any codebase.

The standard is simple: **if an AI says it, the AI must show where it learned it.**

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Adding citation patterns
- Adding CLI adapters
- Extending violation types
- Modifying the report

---

## License

[MIT](LICENSE)
