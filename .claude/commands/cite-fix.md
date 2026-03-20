---
name: cite-fix
description: Fix evidence violations by finding real sources in the codebase and proposing accurate citations with file:line references. Optional web verification fallback for claims with no local source.
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
  - name: --web-verify
    description: Fall back to Google AI Mode for claims not found locally (requires google-ai-mode-skill)
    required: false
---

Invoke the `citation-fix` skill with the provided arguments.

If no target argument was given, ask the user: "Which file has violations to fix? Provide a file path."

Pass all arguments through to the skill:
- The target file path as TARGET
- --auto flag if provided
- --source-dirs paths if provided
- --web-verify flag if provided

After the skill completes:
- Present proposed fixes with tier labels (LOCAL, EXTERNAL, UNVERIFIABLE)
- LOCAL fixes: apply in --auto mode or ask in interactive mode
- EXTERNAL fixes: always ask for confirmation (even with --auto)
- After fixes applied: run evidence-audit again to confirm improvement
- Flag any UNVERIFIABLE claims that need human decision
