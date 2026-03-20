# Evidence Protocol Specification

## Core Principle

Every AI-generated statement that asserts a fact must cite its source. No exceptions.

## Claim Categories

### Factual Claims
Statements asserting something is true about the codebase, system, or world.

Examples:
- "The system uses Redis for caching"
- "This function is thread-safe"
- "The API returns JSON"

Required citation: `[source: file_path:line_number]` or `[source: URL]`

### Numbers and Statistics
Any quantitative value in AI-generated output.

Examples:
- "500 requests per second"
- "3.2 seconds response time"
- "40% improvement"

Required citation: `[derived: file_path:line_number]` or `[derived: computation description]`

### Absence Claims
Statements asserting something doesn't exist or wasn't found.

Examples:
- "No tests exist for this module"
- "This endpoint has no authentication"
- "The config file was not found"

Required citation: `[searched: list of paths and patterns checked]`

## Violation Types

| Type | Severity (default) | Meaning |
|------|-------------------|---------|
| `UNCITED_INFERENCE` | error | Factual claim with no citation |
| `UNVERIFIED_NUMBER` | warning | Number without derivation chain |
| `UNSUPPORTED_ABSENCE` | warning | Absence claim without search evidence |
| `BROKEN_CITATION` | error | Citation pointing to non-existent source |

## Verdicts

| Verdict | Condition |
|---------|-----------|
| `COMPLIANT` | Zero error-level violations |
| `NON_COMPLIANT` | Any error-level violation |

With `--strict`: any violation of any severity level triggers NON_COMPLIANT.

## Citation Formats

Standard formats recognized by Agent-Cite:

```
[source: src/config.py:15]           — file and line
[source: src/config.py]              — file only
[source: https://docs.example.com]   — URL
[derived: tests/bench.py:23]         — number derivation from file
[derived: 500 * 0.8 = 400]           — number derivation from computation
[searched: src/, tests/, docs/]       — search evidence for absence claims
```

Custom formats can be defined in `evidence-protocol.yaml`.
