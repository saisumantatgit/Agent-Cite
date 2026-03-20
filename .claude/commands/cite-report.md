---
name: cite-report
description: Generate a project-wide evidence health report — batch audit, coverage score, worst offenders, improvement tracking.
arguments:
  - name: scope
    description: Glob pattern or directory to audit (default all docs)
    required: false
  - name: --strict
    description: Fail on any warning, not just violations
    required: false
  - name: --format
    description: "Output format: summary (default), detailed, json"
    required: false
  - name: --baseline
    description: Path to previous report for improvement comparison
    required: false
---

Invoke the `evidence-report` skill with the provided arguments.

If no scope argument was given, audit all markdown and JSON documentation files.

Pass all arguments through to the skill:
- The scope glob pattern or directory
- --strict flag if provided
- --format preference if provided
- --baseline path if provided

After the skill completes:
- Present the evidence health report with coverage score
- Highlight worst offenders (lowest coverage files)
- If --baseline provided: show improvement or regression
- Suggest next action: "/cite-fix on the worst offender to raise project score"
