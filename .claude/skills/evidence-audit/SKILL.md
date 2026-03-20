---
name: evidence-audit
description: >
  Audit any AI-generated output for evidence protocol compliance. Every factual
  claim must cite a source, every number must have a derivation, zero uncited
  inference allowed. Returns COMPLIANT or NON_COMPLIANT with structured violations.
license: MIT
metadata:
  domain: evidence-enforcement
  maturity: stable
  primary_use: audit
allowed-tools: Read Glob Grep Bash
---

# Evidence Audit

Verify that AI-generated output meets the evidence protocol: every factual claim cites a source, every number has a derivation chain, and every "not found" claim has search evidence.

## Trigger

Activate this skill when:

- auditing AI-generated reports, analyses, summaries, or documentation
- reviewing output that makes factual claims, cites numbers, or asserts absence
- checking any text where "every claim must have evidence" is the standard

Do NOT activate this skill when:

- the output is pure code (functions, classes, modules)
- the output is formatting or structural changes
- the output is creative or generative with no factual claims

## Arguments

- **TARGET** (required): File path or inline text to audit
- `--strict`: Fail on ANY warning (not just violations)
- `--source-dir path`: Directory to verify that cited sources actually exist

## Workflow

### 1. Read Target

If TARGET is a file path: read the file and note the format (JSON, markdown, plain text).
If TARGET is inline text: use directly.
If no TARGET: ask "What file or output would you like to audit for evidence compliance?"

### 2. Load Protocol Rules

Check for `evidence-protocol.yaml` in the project root or `.cite/` directory.
If found, load custom rules (violation severities, citation patterns, excluded paths).
If not found, use defaults:
- UNCITED_INFERENCE → error (hard failure)
- UNVERIFIED_NUMBER → warning (error if --strict)
- UNSUPPORTED_ABSENCE → warning (error if --strict)
- BROKEN_CITATION → error (always fails)

### 3. Scan for Claims

Parse the TARGET and categorize every statement:

**Factual claims** — statements asserting something is true:
- Check: does it cite a source? (file_path:line, URL, section reference, data ID)
- If cited AND `--source-dir` provided: verify the source file exists
- Violations:
  - `UNCITED_INFERENCE` — factual claim with no citation
  - `BROKEN_CITATION` — citation to non-existent source (only with --source-dir)

**Numbers and statistics** — any quantitative value:
- Check: does it have a derivation? (formula, computation, or source reference)
- Violation:
  - `UNVERIFIED_NUMBER` — number without derivation chain

**Absence claims** — statements that something doesn't exist or wasn't found:
- Check: does it have search evidence? (what was searched, what paths were checked)
- Violation:
  - `UNSUPPORTED_ABSENCE` — "not found" without search evidence

### 4. Compile Report

```
## Evidence Audit Report

### Target: [file path or "inline text"]

### Verdict: COMPLIANT / NON_COMPLIANT

### Summary
| Category | Total | Cited | Violations |
|----------|-------|-------|------------|
| Factual claims | X | Y | Z |
| Numbers/stats | X | Y | Z |
| Absence claims | X | Y | Z |
| **Total** | **X** | **Y** | **Z** |

### Violations
| # | Line | Type | Content | Suggested Fix |
|---|------|------|---------|---------------|
| 1 | L42 | UNCITED_INFERENCE | "The system processes 500 items" | Add: [source: config.json:15] |
| 2 | L67 | UNVERIFIED_NUMBER | "Processing takes 3.2 seconds" | Add: [derived: benchmark run 2026-03-20] |

### Broken Citations (if --source-dir used)
| # | Line | Citation | Expected Path | Status |
|---|------|----------|---------------|--------|
| 1 | L23 | data/old.json | source-dir/data/old.json | NOT FOUND |
```

### 5. Determine Verdict

- **COMPLIANT**: Zero errors. Warnings are allowed (unless --strict).
- **NON_COMPLIANT**: Any error-level violation. Or if --strict: any violation of any type.

Default severities:
- `UNCITED_INFERENCE` → error (always fails)
- `UNVERIFIED_NUMBER` → warning (fails only with --strict)
- `UNSUPPORTED_ABSENCE` → warning (fails only with --strict)
- `BROKEN_CITATION` → error (always fails)

Custom severities can be set in `evidence-protocol.yaml`.

### 6. Present Results

If NON_COMPLIANT:
- List each violation with line number and suggested fix
- Offer: "Fix these violations with `/cite-fix @same_file`"

If COMPLIANT:
- "Evidence protocol: COMPLIANT. All claims cited, all numbers derived."

## Usage Examples

```
/cite-audit data/output.json

/cite-audit @docs/report.md --strict

/cite-audit @data/classification.json --source-dir data/taxonomy/

/cite-audit "The system processes 500 records, 320 are classified as high-priority"
```

## References

- [references/evidence-protocol-spec.md](../../references/evidence-protocol-spec.md)
- [references/violation-types.md](../../references/violation-types.md)
