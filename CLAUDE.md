# Agent-Cite

Agent-Cite is a Claude Code plugin that enforces evidence protocol on AI-generated output. Every factual claim must cite a source, every number must have a derivation, zero uncited inference.

## Architecture

Three command journeys, each with a skill and supporting agent:

| Command | Skill | Agent | Purpose |
|---------|-------|-------|---------|
| `/cite-audit` | evidence-audit | citation-scanner | Detect uncited claims |
| `/cite-fix` | citation-fix | citation-fixer | Fix violations with real citations |
| `/cite-report` | evidence-report | source-verifier | Project-wide evidence health |

## Violation Types

| Type | Default Severity | Meaning |
|------|-----------------|---------|
| `UNCITED_INFERENCE` | error | Factual claim without citation |
| `UNVERIFIED_NUMBER` | warning | Number without derivation |
| `UNSUPPORTED_ABSENCE` | warning | Absence claim without search evidence |
| `BROKEN_CITATION` | error | Citation to non-existent source |

## Verdicts

- **COMPLIANT**: Zero error-level violations
- **NON_COMPLIANT**: Any error-level violation

## When to Apply

Apply to AI-generated reports, analyses, documentation, recommendations — any output that asserts facts. Do NOT apply to pure code, formatting, or creative output.

## Configuration

`evidence-protocol.yaml` in project root or `.cite/` directory:
- Custom violation severities
- Citation pattern formats
- Include/exclude file patterns
- Source directories for /cite-fix
- Health thresholds for /cite-report

## Relationship to Agent-PROVE

Agent-PROVE includes evidence auditing as one of its capabilities (`/audit` command). Agent-Cite is the standalone version focused exclusively on evidence enforcement with additional capabilities (citation fix, project-wide reporting, configurable protocol). If you use Agent-PROVE, you already have basic evidence auditing — Agent-Cite goes deeper.
