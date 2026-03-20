---
name: citation-fix
description: >
  Fix evidence violations by reading the actual codebase and proposing real
  citations with file:line references. Not guesses — verified sources pulled
  from the repo. Optional web verification fallback for claims that have no
  local source but may be verifiable externally.
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
- `--web-verify`: When local search fails, attempt web verification via Google AI Mode as a fallback (requires patchright -- run pip install patchright)

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
4. If found locally: propose citation in format `[source: file_path:line_number]` (tier: LOCAL, confidence: HIGH)
5. If not found locally AND `--web-verify` is enabled:
   - Query Google AI Mode with the claim text
   - If web source found: propose citation `[source: URL]` (tier: EXTERNAL, confidence: MEDIUM)
   - Tag as web-verified so the reader knows it's not from the repo
6. If not found anywhere: flag as `UNVERIFIABLE` — the claim may be fabricated

For each `UNVERIFIED_NUMBER` violation:
1. Extract the number
2. Search for:
   - Config values that match
   - Benchmark results that match
   - Computed values in code that could produce the number
   - Test assertions with the same value
3. If found locally: propose derivation `[derived: file_path:line_number or computation]` (tier: LOCAL)
4. If not found locally AND `--web-verify` is enabled:
   - Query Google AI Mode for the number (e.g., "Redis operations per second benchmark")
   - If authoritative source found: propose `[derived: URL]` (tier: EXTERNAL)
5. If not found anywhere: flag as `UNVERIFIABLE`

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

### 3. Citation Tiers

Every proposed citation is tagged with a tier indicating its source:

| Tier | Source | Confidence | Format | When |
|------|--------|------------|--------|------|
| **LOCAL** | Your codebase | HIGH | `[source: file_path:line]` | Found in repo files |
| **EXTERNAL** | Web-verified | MEDIUM | `[source: URL]` | Found via --web-verify (Google AI Mode) |
| **UNVERIFIABLE** | Nothing found | NONE | No citation proposed | Not in repo, not on web |

LOCAL citations are always preferred. EXTERNAL citations are only proposed when local search fails AND `--web-verify` is enabled. EXTERNAL citations are tagged so readers know the source is web-based, not from the repo.

### 4. Present Proposed Fixes

```
## Citation Fix Proposals

### Target: [file path]

| # | Line | Violation | Proposed Fix | Tier | Confidence |
|---|------|-----------|-------------|------|------------|
| 1 | L42 | UNCITED_INFERENCE | Add: [source: src/config.py:15] | LOCAL | HIGH — exact match |
| 2 | L67 | UNVERIFIED_NUMBER | Add: [derived: tests/bench.py:23] | LOCAL | MEDIUM — similar value |
| 3 | L89 | UNSUPPORTED_ABSENCE | Add: [searched: src/, tests/, docs/] | LOCAL | HIGH — search performed |
| 4 | L12 | BROKEN_CITATION | Update: data/old.json → data/v2/old.json | LOCAL | HIGH — file moved |
| 5 | L33 | UNCITED_INFERENCE | Add: [source: https://redis.io/docs/benchmarks] | EXTERNAL | MEDIUM — web-verified |

### Unverifiable Claims (action required)
| # | Line | Content | Issue |
|---|------|---------|-------|
| 6 | L55 | "Latency improved by 40%" | No local or web source found. Claim may be fabricated. |
```

### 5. Apply Fixes

If `--auto`: apply all HIGH confidence fixes directly.
If interactive (default):
- Present each fix and ask: "Apply this fix? [y/n/edit]"
- Allow the user to edit the proposed citation before applying
- Skip UNVERIFIABLE items — these need human decision

### 6. Re-Audit

After fixes are applied, run evidence-audit again on the TARGET.
Report the new verdict and any remaining violations.

## Usage Examples

```
/cite-fix @docs/report.md

/cite-fix @data/output.json --auto --source-dirs src/,tests/

/cite-fix @docs/analysis.md --audit-report .cite/last-audit.json

/cite-fix @docs/report.md --web-verify
# Falls back to Google AI Mode for claims not found in the codebase

/cite-fix @docs/report.md --web-verify --auto
# Auto-applies LOCAL fixes, presents EXTERNAL fixes for confirmation
```

## Web Verification (--web-verify)

When `--web-verify` is enabled and a claim has no local source:

1. Run `python scripts/web_verify.py --claim "<claim text>"`
2. The script queries Google AI Mode via browser automation (Patchright)
3. Google synthesizes 20+ web sources and returns citations
4. If a relevant source is found: proposed as an EXTERNAL tier citation
5. EXTERNAL citations are always presented for human confirmation (even with --auto)
6. Confidence is assessed by term overlap between claim and web response (HIGH/MEDIUM/LOW)

For batch verification: `python scripts/web_verify.py --claims-file violations.json`

**Setup (one-time):**
```bash
pip install patchright
python scripts/web_verify.py --install-browser
```

**Without setup:** `--web-verify` flag degrades gracefully — violations fall through to UNVERIFIABLE. Agent-Cite works identically without Patchright installed. Zero hard dependencies.
