# Agent-Cite — Evidence Enforcement

## Evidence Protocol

When producing output that makes factual claims:

1. **Every factual claim** must cite a source: `[source: file_path:line]`
2. **Every number** must have a derivation: `[derived: source or computation]`
3. **Every "not found" claim** must show search evidence: `[searched: paths checked]`
4. **Zero uncited inference** — a claim without a citation is indistinguishable from a hallucination

## Violation Types

- `UNCITED_INFERENCE` — factual claim without citation (error)
- `UNVERIFIED_NUMBER` — number without derivation (warning)
- `UNSUPPORTED_ABSENCE` — absence claim without search evidence (warning)
- `BROKEN_CITATION` — citation to non-existent source (error)

## When to Apply

Apply to reports, analyses, documentation, recommendations — any output asserting facts.
Do NOT apply to pure code, formatting, or creative output.
