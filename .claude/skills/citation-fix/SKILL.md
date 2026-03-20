---
name: citation-fix
description: >
  Fix evidence violations by reading the actual codebase and proposing real
  citations with file:line references. Not guesses — verified sources pulled
  from the repo.
license: MIT
metadata:
  domain: evidence-enforcement
  maturity: stable
  primary_use: remediation
allowed-tools: Read Glob Grep Bash Edit
---

# Citation Fix

Take evidence violations from a `/cite-audit` report and fix them by finding real sources in the codebase.

## Trigger

Activate this skill when:

- the user runs `/cite-fix` on a file with known violations
- the user asks to "fix citations" or "add sources" to AI-generated output
- a `/cite-audit` report returned NON_COMPLIANT and the user wants remediation

Do NOT activate this skill when:

- the output is pure code
- there are no violations to fix
- the user wants to audit (use evidence-audit instead)

## Arguments

- **TARGET** (required): File path with violations to fix
- `--audit-report path`: Path to a previous audit report (optional — will re-audit if not provided)
- `--auto`: Apply fixes automatically without confirmation (default: interactive)
- `--source-dirs paths`: Comma-separated directories to search for sources

## Workflow

### 1. Identify Violations

If `--audit-report` provided: load violations from the report.
Otherwise: run evidence-audit on TARGET first to discover violations.

### 2. For Each Violation, Find the Real Source

For each `UNCITED_INFERENCE` violation:
1. Extract the claim text
2. Identify the key assertion (what fact is being claimed?)
3. Search the codebase for evidence:
   - Grep for related terms, function names, variable names
   - Read candidate files that could contain the source
   - Check test files for assertions that confirm the claim
   - Check config files for values that match numbers
4. If found: propose citation in format `[source: file_path:line_number]`
5. If not found: flag as `UNVERIFIABLE` — the claim may be fabricated

For each `UNVERIFIED_NUMBER` violation:
1. Extract the number
2. Search for:
   - Config values that match
   - Benchmark results that match
   - Computed values in code that could produce the number
   - Test assertions with the same value
3. If found: propose derivation `[derived: file_path:line_number or computation]`
4. If not found: flag as `UNVERIFIABLE`

For each `UNSUPPORTED_ABSENCE` violation:
1. Extract the absence claim ("no X exists", "X was not found")
2. Perform the search the claim should have done:
   - Search for the thing claimed to be absent
   - Document what was searched and where
3. If truly absent: propose search evidence `[searched: paths checked]`
4. If actually present: flag as `FALSE_ABSENCE` — the claim is wrong

For each `BROKEN_CITATION` violation:
1. Check if the file was moved (search by filename)
2. Check if the path has a typo (fuzzy match)
3. If found at new location: propose updated citation
4. If truly gone: flag for removal or replacement

### 3. Present Proposed Fixes

```
## Citation Fix Proposals

### Target: [file path]

| # | Line | Violation | Proposed Fix | Confidence |
|---|------|-----------|-------------|------------|
| 1 | L42 | UNCITED_INFERENCE | Add: [source: src/config.py:15] | HIGH — exact match |
| 2 | L67 | UNVERIFIED_NUMBER | Add: [derived: tests/bench.py:23] | MEDIUM — similar value |
| 3 | L89 | UNSUPPORTED_ABSENCE | Add: [searched: src/, tests/, docs/] | HIGH — search performed |
| 4 | L12 | BROKEN_CITATION | Update: data/old.json → data/v2/old.json | HIGH — file moved |

### Unverifiable Claims (action required)
| # | Line | Content | Issue |
|---|------|---------|-------|
| 5 | L55 | "Latency improved by 40%" | No benchmark data found. Claim may be fabricated. |
```

### 4. Apply Fixes

If `--auto`: apply all HIGH confidence fixes directly.
If interactive (default):
- Present each fix and ask: "Apply this fix? [y/n/edit]"
- Allow the user to edit the proposed citation before applying
- Skip UNVERIFIABLE items — these need human decision

### 5. Re-Audit

After fixes are applied, run evidence-audit again on the TARGET.
Report the new verdict and any remaining violations.

## Usage Examples

```
/cite-fix @docs/report.md

/cite-fix @data/output.json --auto --source-dirs src/,tests/

/cite-fix @docs/analysis.md --audit-report .cite/last-audit.json
```
