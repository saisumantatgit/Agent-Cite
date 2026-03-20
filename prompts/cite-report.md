# Evidence Report Prompt

You are generating a project-wide evidence health report.

## How to Report

1. **Discover files** — scan for markdown, JSON, and documentation files
2. **Batch audit** — run evidence audit on each file
3. **Compute metrics:**
   - Evidence Coverage Score = (cited claims / total claims) × 100
   - Per-file scores
4. **Produce report:**
   - Overall score and verdict (HEALTHY ≥90%, NEEDS_WORK 60-89%, CRITICAL <60%)
   - Worst offenders (lowest coverage files)
   - Violation pattern breakdown
   - If baseline provided: improvement/regression comparison
   - Top 3 recommendations for improving the score
5. **Save report** as JSON if requested (for CI integration and baseline tracking)
