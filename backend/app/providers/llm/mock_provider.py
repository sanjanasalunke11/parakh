"""Deterministic, fully-offline fallback for when no ANTHROPIC_API_KEY is set.

Not a stub: extract_claim() does real regex-based noise stripping and
verify_claim() does real keyword-overlap scoring against the evidence
it's given, so the demo remains meaningfully functional with zero API keys.
"""

import re
from typing import Any, Dict, List

from .base import LLMProvider

EMOJI_PATTERN = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]+"
)

NOISE_PATTERNS = [
    r"good\s*(morning|afternoon|evening|night)[!.,]*",
    r"jai\s*hind[!.,]*",
    r"forward(ed)?\s*(this\s*)?(message\s*)?(to\s*(all|everyone|as many people)?)?(as many times as possible)?",
    r"please\s*(forward|share|circulate|spread)\s*(this)?(\s*(to|with)\s*(all|everyone|your contacts))?",
    r"\*+",
    r"_{2,}",
    r"~+",
    r"https?://\S+",
    r"\bplease\b",
]

CATEGORY_RULES = [
    (["vaccine", "covid", "corona", "cure", "disease", "health", "medicine", "hospital", "cancer", "virus"], "Health"),
    (["scholarship", "scheme", "yojana", "subsidy", "government will", "sarkar", "pension", "free laptop"], "Government Scheme"),
    (["election", "minister", "party", "vote", "parliament", "mp ", "mla "], "Politics"),
    (["bank", "rbi", "currency", "note", "loan", "atm", "upi", "rupee", "₹"], "Finance"),
    (["5g", "phone", "app", "software", "ai ", "robot", "satellite", "internet"], "Science & Technology"),
    (["riot", "community", "religion", "temple", "mosque", "caste"], "Communal/Social"),
    (["kidnap", "police", "crime", "murder", "theft", "abduct"], "Crime & Safety"),
    (["actor", "movie", "celebrity", "film", "cricket", "match"], "Entertainment"),
]

UNCERTAIN_SIGNALS = {
    "could not be corroborated", "could not be verified", "not corroborated",
    "no official scheme", "no such scheme", "does not match", "no scheme",
}
FALSE_SIGNALS = {
    "false", "hoax", "debunked", "fake", "myth", "no evidence", "misinformation",
    "denied", "not true", "rumour", "rumor", "clarified that it is not", "does not exist",
    "no such", "never announced", "not a real",
}
TRUE_SIGNALS = {
    "confirmed", "officially confirmed", "officially announced", "true", "announced",
    "verified", "approved", "launched", "notified",
}


class MockLLMProvider(LLMProvider):
    def extract_claim(self, raw_text: str) -> Dict[str, Any]:
        text = EMOJI_PATTERN.sub(" ", raw_text)
        for pattern in NOISE_PATTERNS:
            text = re.sub(pattern, " ", text, flags=re.IGNORECASE)

        lines = [line.strip(" -•\t*") for line in text.splitlines() if line.strip()]
        # Join rather than pick a single "longest" line: screenshots and OCR
        # output routinely wrap one claim across several lines, and dropping
        # the tail (e.g. "...subscription fee from next month") would silently
        # truncate the claim being checked.
        candidate_lines = [line for line in lines if len(line.split()) >= 3]
        normalized = " ".join(candidate_lines) if candidate_lines else text.strip()
        normalized = re.sub(r"\s+", " ", normalized).strip()

        if not normalized:
            normalized = re.sub(r"\s+", " ", raw_text).strip()[:500]

        return {
            "normalized_claim": normalized[:500],
            "category": self._guess_category(normalized),
        }

    def _guess_category(self, text: str) -> str:
        lowered = text.lower()
        for keywords, category in CATEGORY_RULES:
            if any(keyword in lowered for keyword in keywords):
                return category
        return "Other"

    def verify_claim(self, claim: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        claim_words = set(re.findall(r"[a-zA-Z0-9₹]+", claim.lower()))
        if not evidence or not claim_words:
            return self._unverified()

        best_overlap = 0
        strong_sources = 0
        signal = None

        for item in evidence:
            snippet_lower = (item.get("snippet") or "").lower()
            snippet_words = set(re.findall(r"[a-zA-Z0-9₹]+", snippet_lower))
            overlap = len(claim_words & snippet_words)
            best_overlap = max(best_overlap, overlap)

            if item.get("reliability") == "HIGH":
                strong_sources += 1

            # Checked in priority order: an explicit "insufficient evidence" phrase
            # always wins, even if a generic positive/negative word also appears.
            if any(s in snippet_lower for s in UNCERTAIN_SIGNALS):
                signal = "UNCERTAIN"
            elif signal in (None, "UNCERTAIN") and any(s in snippet_lower for s in FALSE_SIGNALS):
                signal = "FALSE"
            elif signal is None and any(s in snippet_lower for s in TRUE_SIGNALS):
                signal = "VERIFIED"

        # An explicit signal phrase (debunk / confirm / "could not be corroborated")
        # is stronger evidence of intent than raw word overlap, so it wins even
        # when overlap is thin. With no such phrase, fall back to the overlap
        # threshold to avoid verdicts on barely-related evidence.
        if signal is None and best_overlap < 2:
            return self._unverified()

        strength = "HIGH" if strong_sources >= 2 else "MEDIUM" if strong_sources >= 1 else "LOW"

        if signal == "UNCERTAIN":
            return self._unverified()

        if signal == "FALSE":
            verdict = "FALSE"
            explanation = (
                "One or more credible sources directly contradict this claim. "
                "It does not hold up against the retrieved evidence."
            )
        elif signal == "VERIFIED":
            verdict = "VERIFIED"
            explanation = (
                "The retrieved evidence corroborates the key details of this claim from credible sources."
            )
        else:
            verdict = "MISLEADING"
            explanation = (
                "The retrieved evidence is related to this claim but does not fully confirm it as stated — "
                "it may be exaggerated, out of context, or only partially accurate."
            )

        return {
            "verdict": verdict,
            "evidence_strength": strength,
            "explanation": explanation,
            "category": self._guess_category(claim),
        }

    def _unverified(self) -> Dict[str, Any]:
        return {
            "verdict": "UNVERIFIED",
            "evidence_strength": "LOW",
            "explanation": (
                "No sufficiently relevant, reliable evidence was found to confirm or deny this claim. "
                "Treat it with caution until it is confirmed by an official source."
            ),
            "category": "Other",
        }
