---
name: cite-audit
description: Audit a file or text for evidence protocol compliance — every claim must cite a source, every number must have a derivation, zero uncited inference.
arguments:
  - name: target
    description: File path or inline text to audit
    required: false
  - name: --strict
    description: Fail on any warning, not just violations
    required: false
  - name: --source-dir
    description: Directory to verify cited sources exist
    required: false
---

Invoke the `evidence-audit` skill with the provided arguments.

If no target argument was given, ask the user: "What file or output would you like to audit for evidence compliance? Provide a file path or paste the content."

Pass all arguments through to the skill:
- The target file path or text as TARGET
- --strict flag if provided
- --source-dir path if provided

After the skill completes:
- If COMPLIANT: confirm evidence protocol compliance
- If NON_COMPLIANT: present violations with line numbers and suggested fixes, offer `/cite-fix @same_file` to remediate
