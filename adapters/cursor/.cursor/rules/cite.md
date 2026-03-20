# Agent-Cite — Evidence Enforcement

## Rule: Cite Every Claim

When producing AI-generated reports, analyses, or documentation:

1. Every factual claim must cite: `[source: file_path:line]`
2. Every number must derive: `[derived: source or computation]`
3. Every absence claim must prove: `[searched: paths checked]`
4. Zero uncited inference — cite it or it's opinion

## Violation Types

- UNCITED_INFERENCE — factual claim without citation (error)
- UNVERIFIED_NUMBER — number without derivation (warning)
- UNSUPPORTED_ABSENCE — absence without search evidence (warning)
- BROKEN_CITATION — citation to non-existent source (error)
