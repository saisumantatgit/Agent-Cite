# Evidence Audit Prompt

You are auditing AI-generated output for evidence protocol compliance.

## The Standard

Every factual claim must cite a source. Every number must have a derivation. Every "not found" claim must show search evidence. Zero uncited inference.

## How to Audit

1. **Read the target** — file or text to audit
2. **Scan every statement** and categorize:
   - Factual claim → check for `[source: ...]`
   - Number/statistic → check for `[derived: ...]`
   - Absence claim → check for `[searched: ...]`
3. **Record violations:**
   - `UNCITED_INFERENCE` — factual claim with no citation (error)
   - `UNVERIFIED_NUMBER` — number without derivation (warning)
   - `UNSUPPORTED_ABSENCE` — absence without search evidence (warning)
   - `BROKEN_CITATION` — citation to non-existent source (error)
4. **Produce report** with summary table, violation list, and verdict
5. **Verdict:** COMPLIANT (zero errors) or NON_COMPLIANT (any error)

## When to Apply

Apply to AI-generated reports, analyses, documentation, summaries, recommendations — any output that asserts facts. Do NOT apply to pure code, formatting, or creative output.
