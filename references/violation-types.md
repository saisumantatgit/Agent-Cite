# Violation Types Reference

## UNCITED_INFERENCE

**Severity:** error (always fails audit)
**Meaning:** A factual claim with no citation.
**Example:** "The system processes 500 items per second" with no `[source: ...]`
**Fix:** Add a citation to the source: `[source: file_path:line_number]`
**Why it matters:** Uncited claims are indistinguishable from hallucinations. If the agent can't point to where it learned this, it may have made it up.

## UNVERIFIED_NUMBER

**Severity:** warning (error with --strict)
**Meaning:** A quantitative value with no derivation chain.
**Example:** "Response time improved by 40%" with no `[derived: ...]`
**Fix:** Add a derivation: `[derived: benchmark_results.json:12]` or `[derived: before=5.0s, after=3.0s, improvement=(5-3)/5=40%]`
**Why it matters:** Numbers without derivation chains are the most common form of AI fabrication. They sound precise but may be invented.

## UNSUPPORTED_ABSENCE

**Severity:** warning (error with --strict)
**Meaning:** A claim that something doesn't exist, without evidence of having searched for it.
**Example:** "No tests exist for this module" with no `[searched: ...]`
**Fix:** Add search evidence: `[searched: tests/, src/tests/, **/test_*.py]`
**Why it matters:** "Not found" is only trustworthy if you know what was searched. An agent that says "no tests exist" without proving it looked may have simply not searched thoroughly enough.

## BROKEN_CITATION

**Severity:** error (always fails audit)
**Meaning:** A citation pointing to a file or line that doesn't exist.
**Example:** `[source: data/old.json:3]` where `data/old.json` has been deleted
**Fix:** Update the citation to the correct path, or remove the claim if the source is truly gone
**Why it matters:** Broken citations are worse than no citations — they create false confidence. The reader trusts the claim because it has a citation, but the citation leads nowhere.

## FALSE_ABSENCE (discovered during /cite-fix)

**Severity:** critical (not a citation issue — a factual error)
**Meaning:** The agent claimed something doesn't exist, but it does.
**Example:** "No tests exist for this module" — but `tests/test_module.py` has 12 tests
**Fix:** Remove or correct the false claim
**Why it matters:** This is not a missing citation — this is a wrong claim. The agent hallucinated the absence of something that exists.

## UNVERIFIABLE (discovered during /cite-fix)

**Severity:** requires human decision
**Meaning:** The citation-fixer searched the codebase and could not find any source for this claim.
**Example:** "Latency improved by 40%" — no benchmark data found anywhere in the repo
**Action:** The claim may be fabricated. A human must decide whether to remove it, find an external source, or accept it with a disclaimer.
