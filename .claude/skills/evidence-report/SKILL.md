---
name: evidence-report
description: >
  Generate a project-wide evidence health report. Batch-audits multiple files,
  computes an evidence coverage score, identifies the worst offenders, and
  tracks improvement over time.
license: MIT
metadata:
  domain: evidence-enforcement
  maturity: stable
  primary_use: reporting
allowed-tools: Read Glob Grep Bash
---

# Evidence Report

Audit an entire project (or set of files) for evidence protocol compliance. Produces a coverage score, identifies patterns, and highlights the files most in need of citation work.

## Trigger

Activate this skill when:

- the user wants a project-wide evidence health check
- the user asks "how cited is our documentation?" or "where are we missing evidence?"
- after a major AI-assisted work session to assess overall evidence quality

Do NOT activate this skill when:

- auditing a single file (use evidence-audit instead)
- fixing violations (use citation-fix instead)

## Arguments

- **SCOPE** (optional): Glob pattern or directory to audit (default: all markdown and JSON files)
- `--strict`: Fail on any warning, not just violations
- `--source-dir path`: Directory for source verification
- `--format`: Output format — `summary` (default), `detailed`, `json`
- `--baseline path`: Previous report for comparison (shows improvement/regression)

## Workflow

### 1. Discover Files

If SCOPE provided: use the glob pattern or directory.
If not provided: scan for files likely to contain AI-generated claims:
- `docs/**/*.md`
- `*.md` in project root (excluding CHANGELOG, LICENSE)
- `data/**/*.json` (output files, reports)
- Any file matching patterns in `evidence-protocol.yaml` include list

Exclude:
- Pure code files (.py, .js, .ts, etc.) — unless they contain substantial docstrings
- Generated files (node_modules, dist, build)
- Files listed in `evidence-protocol.yaml` exclude list

### 2. Batch Audit

For each discovered file, run the evidence-audit workflow:
- Scan for claims, numbers, absence statements
- Categorize violations
- Record per-file verdict

### 3. Compute Metrics

```
Evidence Coverage Score = (cited_claims / total_claims) × 100

Per-file scores:
- file_score = (cited / total) × 100 for each file
- 100% = fully cited
- 0% = no citations at all
```

### 4. Compile Report

```
## Evidence Health Report

### Project: [repo name]
### Date: [ISO 8601]
### Scope: [glob pattern or "all docs"]

### Overall Score: XX% evidence coverage

### Summary
| Metric | Count |
|--------|-------|
| Files audited | X |
| Total claims found | X |
| Claims with citations | X |
| Violations (errors) | X |
| Violations (warnings) | X |
| Evidence coverage | XX% |

### Verdict: HEALTHY / NEEDS_WORK / CRITICAL

- HEALTHY: ≥90% coverage, zero UNCITED_INFERENCE errors
- NEEDS_WORK: 60-89% coverage, or ≤3 UNCITED_INFERENCE errors
- CRITICAL: <60% coverage, or >3 UNCITED_INFERENCE errors

### Worst Offenders (files with lowest coverage)
| File | Claims | Cited | Coverage | Errors |
|------|--------|-------|----------|--------|
| docs/report.md | 45 | 12 | 27% | 18 |
| data/analysis.json | 30 | 20 | 67% | 5 |

### Violation Patterns
| Violation Type | Count | % of Total |
|---------------|-------|-----------|
| UNCITED_INFERENCE | X | XX% |
| UNVERIFIED_NUMBER | X | XX% |
| UNSUPPORTED_ABSENCE | X | XX% |
| BROKEN_CITATION | X | XX% |

### Improvement (if --baseline provided)
| Metric | Previous | Current | Change |
|--------|----------|---------|--------|
| Evidence coverage | 45% | 72% | +27% ↑ |
| UNCITED_INFERENCE | 34 | 8 | -26 ↓ |

### Recommendations
1. [Most impactful fix — e.g., "Fix 18 uncited claims in docs/report.md to raise project score to 75%"]
2. [Second priority]
3. [Third priority]
```

### 5. Save Report (if requested)

If `--format json`: output machine-readable JSON for CI integration.
Save to `.cite/reports/YYYY-MM-DD.json` for baseline tracking.

## Usage Examples

```
/cite-report

/cite-report docs/

/cite-report "docs/**/*.md" --strict --format json

/cite-report --baseline .cite/reports/2026-03-19.json
```
