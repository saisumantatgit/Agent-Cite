# PIR-001: web_verify.py URL Encoding and Error Suppression

## Metadata

| Field | Value |
|-------|-------|
| **PIR ID** | PIR-001 |
| **Date** | 2026-03-20 |
| **Severity** | P2 |
| **Status** | Final |
| **Incident date** | 2026-03-18 |
| **Detection date** | 2026-03-19 |
| **Resolution date** | 2026-03-20 |

## Zone Check

| Dimension | Status | Notes |
|-----------|--------|-------|
| **Severity** | P2 | Reliability degradation, no data loss |
| **Containment** | Contained | All issues fixed in single remediation pass |
| **Blast Radius** | web_verify.py, SKILL.md, adapter docs | 3 code issues + 2 doc inconsistencies |

## 1. Summary

`web_verify.py` shipped with three defects: naive URL encoding (`.replace(" ", "+")` instead of `urllib.parse.quote_plus()`), a dead `--headless` flag, and three bare `except Exception: pass` blocks that silently swallowed all errors. Additionally, SKILL.md listed BROKEN_CITATION as WARNING severity while all other docs listed it as ERROR, and a stale `google-ai-mode-skill` reference persisted. All issues were caught by a dedicated code review agent and remediated in a single pass.

## 2. Timeline

| Time | Event | Actor |
|------|-------|-------|
| 2026-03-18 | v1 of `web_verify.py` merged with naive encoding and broad exception handlers | Developer |
| 2026-03-19 | Code review agent flagged URL encoding, dead flag, and silent exceptions | Code reviewer agent |
| 2026-03-19 | Doc audit found BROKEN_CITATION severity mismatch and stale skill reference | Code reviewer agent |
| 2026-03-20 | All five issues remediated and verified | Developer |

## 3. Five Whys

1. **Why?** -- Claims containing `&`, `=`, or `#` produced malformed URLs and silent verification failures.
2. **Why?** -- URL encoding used `.replace(" ", "+")` which only handles spaces, not URL-reserved characters.
3. **Why?** -- Quick v1 implementation prioritized shipping over correctness; broad `except Exception: pass` blocks were added for "stability."
4. **Why?** -- No code review gate existed for Python utility scripts; they shipped without scrutiny.
5. **Why?** --> **ROOT CAUSE:** Defensive coding patterns (catch-all exceptions) traded reliability for silence. The absence of a review process for utility scripts allowed known shortcuts to become permanent.

## 4. Blast Radius

| Radius | Affected | How |
|--------|----------|-----|
| Direct | `web_verify.py` | Malformed URLs for claims with special characters; headless flag always True; errors silently dropped |
| Adjacent | SKILL.md | BROKEN_CITATION severity listed as WARNING, contradicting all other docs (ERROR) |
| Downstream | Users running `/cite` | Failed verifications reported as passing due to suppressed exceptions; unreliable citation checks |
| Potential (if undetected) | All Cite consumers | Erosion of trust in verification results; undetected false negatives accumulating over time |

## 5. Prompt Forensics

### Triggering input
```
/cite --verify "Study shows 40% improvement (Smith & Jones, 2024)"
```

### Expected vs actual
- Expected: URL-encodes the full query string including `&`, sends well-formed request, reports verification result or explicit error.
- Actual: `&` splits the query parameter, producing a malformed URL. If the request fails, the bare `except` block swallows the error and returns no signal.

## 6. What Went Well

- Code review agent caught all three code defects and both doc inconsistencies in a single review pass.
- Issues were contained to a single file (`web_verify.py`) and two docs, limiting remediation scope.
- No user data was lost or corrupted.

## 7. What Went Wrong

- `except Exception: pass` made failures invisible -- the tool appeared to work when it was silently failing.
- `.replace(" ", "+")` was a known incomplete solution at write time but shipped anyway.
- `--headless` flag was dead code from the start (always `True` regardless of argument).
- SKILL.md severity for BROKEN_CITATION diverged from all other documentation with no review catching it.
- Stale `google-ai-mode-skill` reference was never cleaned up after rename.

## 8. Where We Got Lucky

- No downstream system consumed `web_verify.py` results for automated decisions yet. If Cite had been integrated into a CI gate, silent false negatives would have let bad citations pass undetected.
- The `&`/`=`/`#` encoding bug requires those characters in claims -- common in academic citations (`Smith & Jones`) but not in every query, so the bug was intermittent rather than total.

## 9. Remediation

### Immediate fix
- Replaced `.replace(" ", "+")` with `urllib.parse.quote_plus()` for correct URL encoding of all reserved characters.
- Removed dead `--headless` flag (Playwright headless is the default).
- Replaced all three `except Exception: pass` blocks with specific exception handling and `stderr` logging.

### Permanent fix
- Fixed BROKEN_CITATION severity to ERROR in SKILL.md, consistent with all other docs.
- Removed stale `google-ai-mode-skill` reference.
- Added input validation for URL construction.

### Detection improvement
- Code review agent now covers Python utility scripts, not just prompts and adapters.
- Bare `except` / `except Exception: pass` patterns flagged as a review gate blocker.

## 10. Action Items

| # | Action | Priority | Owner | Due | Status |
|---|--------|----------|-------|-----|--------|
| 1 | Replace `.replace(" ", "+")` with `quote_plus()` | P2 | Developer | 2026-03-20 | Done |
| 2 | Remove dead `--headless` flag | P3 | Developer | 2026-03-20 | Done |
| 3 | Replace bare `except` blocks with logged specific exceptions | P2 | Developer | 2026-03-20 | Done |
| 4 | Align BROKEN_CITATION severity to ERROR in SKILL.md | P3 | Developer | 2026-03-20 | Done |
| 5 | Remove stale `google-ai-mode-skill` reference | P3 | Developer | 2026-03-20 | Done |
| 6 | Add bare-except lint rule to code review checklist | P3 | Developer | 2026-03-27 | Open |

## 11. Lessons Learned

- **Silent failures are worse than loud failures.** `except Exception: pass` is never "defensive" -- it is actively harmful. A tool that reports nothing when it fails is less useful than one that crashes, because the crash at least signals a problem.
- **URL encoding is not string replacement.** Standard library functions (`urllib.parse.quote_plus`) exist for a reason. Rolling custom encoding for well-specified protocols introduces bugs that the standard library already solved.
- **Utility scripts need the same review rigor as core logic.** The distinction between "just a helper script" and "production code" is artificial when the script's output feeds user-facing results.
