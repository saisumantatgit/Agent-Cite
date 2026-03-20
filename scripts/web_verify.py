#!/usr/bin/env python3
"""Web verification for Agent-Cite.

Queries Google AI Mode to verify claims that have no local source.
Returns structured JSON with web-sourced citations.

Usage:
    python scripts/web_verify.py --claim "Redis handles 100K ops/sec"
    python scripts/web_verify.py --claims-file violations.json
    python scripts/web_verify.py --claim "React 19 uses a compiler" --headless

Requirements:
    pip install patchright  (Chromium browser automation)

First run downloads Chromium (~150MB). Subsequent runs reuse the browser profile.
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any


# Browser profile persists across runs (avoids CAPTCHA on repeat queries)
PROFILE_DIR = Path.home() / ".cite" / "browser-profile"
GOOGLE_AI_URL = "https://www.google.com/search?q={query}&udm=50"
MAX_WAIT_SECONDS = 30
RETRY_COUNT = 2


def check_dependencies() -> bool:
    """Check if patchright is installed."""
    try:
        import patchright  # noqa: F401
        return True
    except ImportError:
        return False


def install_browser_if_needed():
    """Install Chromium browser for patchright if not present."""
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "patchright", "install", "chromium"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Warning: Browser install issue: {result.stderr}", file=sys.stderr)


def build_verification_query(claim: str) -> str:
    """Build a search query optimized for fact verification."""
    # Strip citation markers if present
    clean = re.sub(r"\[(?:source|derived|searched):.*?\]", "", claim).strip()
    # Remove common filler
    clean = re.sub(r"^(the |a |an )", "", clean, flags=re.IGNORECASE)
    # Truncate if too long (Google has query limits)
    if len(clean) > 200:
        clean = clean[:200]
    return clean


def query_google_ai_mode(claim: str, headless: bool = True) -> dict:
    """Query Google AI Mode and extract the synthesized answer with citations.

    Returns:
        {
            "claim": str,
            "verified": bool,
            "answer": str,
            "citations": [{"index": int, "title": str, "url": str}],
            "confidence": str,  # "HIGH", "MEDIUM", "LOW"
            "error": str | None
        }
    """
    from patchright.sync_api import sync_playwright

    query = build_verification_query(claim)
    url = GOOGLE_AI_URL.format(query=query.replace(" ", "+"))

    result = {
        "claim": claim,
        "verified": False,
        "answer": "",
        "citations": [],
        "confidence": "LOW",
        "error": None,
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-first-run",
                    "--no-default-browser-check",
                ],
            )
            page = browser.pages[0] if browser.pages else browser.new_page()

            # Navigate to Google AI Mode
            page.goto(url, wait_until="domcontentloaded", timeout=15000)

            # Wait for AI Mode response to load
            ai_response = _wait_for_ai_response(page)

            if ai_response:
                result["answer"] = ai_response["text"]
                result["citations"] = ai_response["citations"]
                result["verified"] = len(ai_response["citations"]) > 0
                result["confidence"] = _assess_confidence(claim, ai_response)
            else:
                result["error"] = "No AI Mode response received"

            browser.close()

    except Exception as e:
        result["error"] = str(e)

    return result


def _wait_for_ai_response(page) -> dict | None:
    """Wait for Google AI Mode to render its synthesized response."""
    selectors = [
        "[data-ai-response]",
        ".ai-overview-card",
        "#ai-overview",
        "[class*='aiOverview']",
        "[class*='AI_']",
        ".wDYxhc",  # Common Google AI overview container
    ]

    for attempt in range(MAX_WAIT_SECONDS):
        for selector in selectors:
            try:
                element = page.query_selector(selector)
                if element:
                    text = element.inner_text()
                    if len(text) > 50:  # Got a real response
                        citations = _extract_citations(page)
                        return {"text": text, "citations": citations}
            except Exception:
                pass
        time.sleep(1)

    # Fallback: try to get any substantial text from the page
    try:
        body_text = page.inner_text("body")
        if len(body_text) > 200:
            citations = _extract_citations(page)
            # Try to extract just the AI overview portion
            ai_text = _extract_ai_section(body_text)
            if ai_text:
                return {"text": ai_text, "citations": citations}
    except Exception:
        pass

    return None


def _extract_ai_section(full_text: str) -> str | None:
    """Try to extract the AI overview section from full page text."""
    # Google AI Mode responses typically appear before regular results
    lines = full_text.split("\n")
    # Take first substantial block (skip navigation/header)
    content_lines = []
    started = False
    for line in lines:
        line = line.strip()
        if not started and len(line) > 80:
            started = True
        if started:
            if line and not line.startswith("http"):
                content_lines.append(line)
            # Stop at "More results" or search suggestions
            if any(marker in line.lower() for marker in ["more results", "people also ask", "related searches"]):
                break
    if content_lines:
        return "\n".join(content_lines[:30])  # Cap at ~30 lines
    return None


def _extract_citations(page) -> list[dict]:
    """Extract citation links from Google AI Mode response."""
    citations = []
    seen_urls = set()

    # Google AI Mode uses numbered citation markers linking to sources
    citation_selectors = [
        "a[data-citation]",
        ".ai-overview-card a[href]",
        "[data-ai-response] a[href]",
        ".wDYxhc a[href]",
    ]

    for selector in citation_selectors:
        try:
            links = page.query_selector_all(selector)
            for i, link in enumerate(links):
                href = link.get_attribute("href") or ""
                title = link.inner_text().strip()

                # Filter out Google internal links
                if not href or "google.com" in href or href.startswith("#"):
                    continue
                # Clean Google redirect URLs
                if "/url?q=" in href:
                    href = href.split("/url?q=")[1].split("&")[0]

                if href not in seen_urls and href.startswith("http"):
                    seen_urls.add(href)
                    citations.append({
                        "index": len(citations) + 1,
                        "title": title or f"Source {len(citations) + 1}",
                        "url": href,
                    })
        except Exception:
            continue

    return citations[:10]  # Cap at 10 citations


def _assess_confidence(claim: str, response: dict) -> str:
    """Assess confidence that the web result actually verifies the claim."""
    if not response["citations"]:
        return "LOW"

    answer_lower = response["text"].lower()
    claim_lower = claim.lower()

    # Extract key terms from claim
    # Remove stop words and check overlap
    claim_terms = set(re.findall(r"\b\w{4,}\b", claim_lower))
    answer_terms = set(re.findall(r"\b\w{4,}\b", answer_lower))

    if not claim_terms:
        return "LOW"

    overlap = len(claim_terms & answer_terms) / len(claim_terms)

    if overlap >= 0.6 and len(response["citations"]) >= 2:
        return "HIGH"
    elif overlap >= 0.3 and len(response["citations"]) >= 1:
        return "MEDIUM"
    else:
        return "LOW"


def verify_claim(claim: str, headless: bool = True) -> dict:
    """Verify a single claim via web search.

    Returns structured result ready for /cite-fix consumption.
    """
    if not check_dependencies():
        return {
            "claim": claim,
            "verified": False,
            "tier": "UNVERIFIABLE",
            "proposed_citation": None,
            "confidence": "NONE",
            "error": "patchright not installed. Run: pip install patchright",
        }

    result = query_google_ai_mode(claim, headless=headless)

    if result["verified"] and result["citations"]:
        best_citation = result["citations"][0]
        return {
            "claim": claim,
            "verified": True,
            "tier": "EXTERNAL",
            "proposed_citation": f"[source: {best_citation['url']}]",
            "citation_title": best_citation["title"],
            "citation_url": best_citation["url"],
            "all_citations": result["citations"],
            "confidence": result["confidence"],
            "ai_summary": result["answer"][:500],
            "error": None,
        }
    else:
        return {
            "claim": claim,
            "verified": False,
            "tier": "UNVERIFIABLE",
            "proposed_citation": None,
            "confidence": "NONE",
            "error": result.get("error", "No verifying source found on the web"),
        }


def verify_claims_batch(claims: list[str], headless: bool = True) -> list[dict]:
    """Verify multiple claims. Adds delay between queries to avoid rate limiting."""
    results = []
    for i, claim in enumerate(claims):
        if i > 0:
            time.sleep(2)  # Rate limit: 2 seconds between queries
        results.append(verify_claim(claim, headless=headless))
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Web verification for Agent-Cite — verify claims via Google AI Mode"
    )
    parser.add_argument("--claim", type=str, help="Single claim to verify")
    parser.add_argument("--claims-file", type=str,
                        help="JSON file with array of claim strings to verify")
    parser.add_argument("--headless", action="store_true", default=True,
                        help="Run browser in headless mode (default: true)")
    parser.add_argument("--no-headless", action="store_true",
                        help="Run browser with visible window (for debugging)")
    parser.add_argument("--install-browser", action="store_true",
                        help="Install Chromium browser and exit")
    args = parser.parse_args()

    headless = not args.no_headless

    if args.install_browser:
        if not check_dependencies():
            print("Error: patchright not installed. Run: pip install patchright",
                  file=sys.stderr)
            sys.exit(1)
        install_browser_if_needed()
        print("Browser installed.")
        sys.exit(0)

    if not args.claim and not args.claims_file:
        parser.print_help()
        sys.exit(1)

    if args.claim:
        result = verify_claim(args.claim, headless=headless)
        print(json.dumps(result, indent=2))

    elif args.claims_file:
        with open(args.claims_file) as f:
            claims = json.load(f)
        if not isinstance(claims, list):
            print("Error: claims file must contain a JSON array of strings",
                  file=sys.stderr)
            sys.exit(1)
        results = verify_claims_batch(claims, headless=headless)
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
