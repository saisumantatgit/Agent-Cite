# Citation Fix Prompt

You are fixing evidence violations by finding real sources in the codebase.

## How to Fix

For each violation from an evidence audit:

1. **UNCITED_INFERENCE** — Search the codebase for the source of the claim:
   - Grep for key terms, function names, config values
   - Read candidate source files
   - Check test assertions
   - Propose: `[source: file_path:line_number]` with confidence

2. **UNVERIFIED_NUMBER** — Search for the origin of the number:
   - Config values, benchmark results, test output, constants
   - Propose: `[derived: file_path:line_number]` or `[derived: computation]`

3. **UNSUPPORTED_ABSENCE** — Actually perform the search:
   - Search for the thing claimed to be absent
   - Document every path searched
   - Propose: `[searched: paths checked]`
   - If the thing actually EXISTS: flag as FALSE_ABSENCE

4. **BROKEN_CITATION** — Find the correct path:
   - Check for file moves, renames, typos
   - Propose updated path

## Rules

- Every proposed citation must reference a REAL file you actually read
- Report confidence honestly: HIGH, MEDIUM, LOW
- Flag UNVERIFIABLE claims — do not invent sources
- Flag FALSE_ABSENCE claims prominently — these are factual errors
