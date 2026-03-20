---
name: cite-fix
description: Fix evidence violations by finding real sources in the codebase and proposing accurate citations with file:line references.
arguments:
  - name: target
    description: File path with violations to fix
    required: false
  - name: --auto
    description: Apply fixes automatically without confirmation
    required: false
  - name: --source-dirs
    description: Comma-separated directories to search for sources
    required: false
---

Invoke the `citation-fix` skill with the provided arguments.

If no target argument was given, ask the user: "Which file has violations to fix? Provide a file path."

Pass all arguments through to the skill:
- The target file path as TARGET
- --auto flag if provided
- --source-dirs paths if provided

After the skill completes:
- Present proposed fixes with confidence levels
- In interactive mode (default): ask for approval on each fix
- After fixes applied: run evidence-audit again to confirm improvement
- Flag any UNVERIFIABLE claims that need human decision
