# ADR-001: Three-Tier Citation Model with Built-In Web Verification

**Status:** Accepted
**Date:** 2026-03-20
**Context:** Designing how /cite-fix resolves violations — specifically, what happens when a claim has no local source.

## Decision

Implement a three-tier citation model with a built-in web verification script (`web_verify.py`), not a third-party dependency.

## The Three Tiers

| Tier | Source | Confidence | Format | When |
|------|--------|------------|--------|------|
| LOCAL | Codebase files | HIGH | `[source: file:line]` | Default — always searched first |
| EXTERNAL | Web (Google AI Mode) | MEDIUM | `[source: URL]` | `--web-verify` flag, local search failed |
| UNVERIFIABLE | Nothing found | NONE | No citation | Both local and web failed |

## Context

`/cite-fix` searches the codebase for sources to back uncited claims. But some claims reference external knowledge ("Redis handles 100K ops/sec") that exists on the web but not in the repo. Without web verification, these claims are marked UNVERIFIABLE — a dead end requiring human intervention.

## Alternatives Considered

### Option A: Depend on google-ai-mode-skill (third-party)
**Rejected.** 121-star repo by one person. If abandoned, renamed, or broken — our feature breaks. Coupling to an external dependency for a core feature violates the "compose but never couple" principle.

### Option B: Build our own web_verify.py
**Accepted.** ~300 lines of Python. Patchright (browser automation) → Google AI Mode → structured JSON. Full control. Graceful degradation (works without Patchright — falls to UNVERIFIABLE).

### Option C: No web verification
**Considered.** Simpler. But leaves a real dead end — claims about external knowledge (benchmarks, library capabilities, industry standards) can never be resolved without human research.

## Key Design Decisions Within This ADR

1. **Opt-in only (`--web-verify` flag).** Web verification is not the default. Local-first is the identity.
2. **EXTERNAL citations always require human confirmation.** Even with `--auto`, external citations are presented for approval. Web sources need human judgment.
3. **Graceful degradation.** No hard dependency on Patchright. If not installed, `--web-verify` is silently ignored.
4. **Persistent browser profile.** `~/.cite/browser-profile/` avoids CAPTCHA on repeat queries.
5. **Rate limiting.** 2-second delay between batch queries to avoid being blocked.

## Consequences

**Good:**
- Eliminates the UNVERIFIABLE dead end for web-knowable claims
- Zero external dependencies — ships with Agent-Cite
- Clear tier labeling — readers always know if a citation is LOCAL or EXTERNAL

**Bad:**
- Browser automation is inherently fragile (Google can change their DOM)
- Adds ~300 lines of Python to maintain
- Requires Patchright + Chromium for web verification (~150MB download)

**How to apply:** LOCAL citations are always preferred and proposed first. EXTERNAL is a fallback, not a replacement. If the user doesn't enable `--web-verify`, the product behaves exactly as before this ADR.
