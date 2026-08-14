"""Offline fallback evidence provider.

Every entry is drawn from widely-documented, non-partisan fact-checks
(WHO/PIB/RBI style myths that have been public knowledge for years) so the
demo never puts words in a real fact-checker's mouth. Source names are
prefixed with "[Demo]" so the UI is honest about this being illustrative,
offline sample data rather than a live retrieval.
"""

import re
from typing import Any, Dict, List

from .base import SearchProvider

_DEMO_EVIDENCE: List[Dict[str, Any]] = [
    {
        "keywords": ["5g", "tower", "coronavirus", "covid", "radiation"],
        "source_name": "[Demo] World Health Organization",
        "url": "https://www.who.int/news-room/feature-stories/detail/5g-mobile-networks-and-health",
        "snippet": "WHO states there is no evidence linking 5G mobile networks to COVID-19. This claim has been repeatedly debunked as a hoax by health authorities worldwide.",
        "reliability": "HIGH",
    },
    {
        "keywords": ["cow urine", "gaumutra", "cures covid", "cure corona"],
        "source_name": "[Demo] PIB Fact Check",
        "url": "https://pib.gov.in/factcheck",
        "snippet": "PIB Fact Check clarifies there is no scientific evidence that cow urine cures or prevents COVID-19; this is a false claim circulating on social media.",
        "reliability": "HIGH",
    },
    {
        "keywords": ["2000 rupee", "2000 note", "worthless", "banned currency"],
        "source_name": "[Demo] Reserve Bank of India",
        "url": "https://rbi.org.in/press-releases",
        "snippet": "RBI clarified that Rs 2000 notes withdrawn from circulation remain legal tender and can still be exchanged at bank branches; they are not worthless as some viral messages claim.",
        "reliability": "HIGH",
    },
    {
        "keywords": ["whatsapp", "charging fee", "paid subscription", "whatsapp will start charging"],
        "source_name": "[Demo] Reuters Fact Check",
        "url": "https://www.reuters.com/fact-check",
        "snippet": "This recurring hoax about WhatsApp charging a subscription fee has circulated since 2013 and has never come true; WhatsApp has officially denied any such plan.",
        "reliability": "HIGH",
    },
    {
        "keywords": ["free laptop", "government link", "click link", "register for laptop"],
        "source_name": "[Demo] PIB Fact Check",
        "url": "https://pib.gov.in/factcheck",
        "snippet": "PIB has flagged this 'free laptop' link as a phishing scam impersonating the government; no such official scheme exists at the link being circulated.",
        "reliability": "HIGH",
    },
    {
        "keywords": ["pm kisan", "kisan yojana", "6000 per year", "farmers scheme"],
        "source_name": "[Demo] PIB / Ministry of Agriculture",
        "url": "https://pmkisan.gov.in/",
        "snippet": "The PM-KISAN scheme officially provides Rs 6,000 per year to eligible farmer families in three equal installments, confirmed on the official government portal.",
        "reliability": "HIGH",
    },
    {
        "keywords": ["garlic", "turmeric", "prevents cancer", "cures cancer"],
        "source_name": "[Demo] ICMR",
        "url": "https://www.icmr.gov.in/",
        "snippet": "ICMR notes that while turmeric and garlic have some health benefits, there is no clinical evidence they prevent or cure cancer; such absolute claims are misleading.",
        "reliability": "HIGH",
    },
    {
        "keywords": ["nasa", "six days of darkness", "planetary alignment", "blackout"],
        "source_name": "[Demo] NASA / Snopes",
        "url": "https://www.snopes.com/fact-check/",
        "snippet": "NASA has never announced any 'six days of darkness' event. This is a recurring hoax debunked multiple times since 2015.",
        "reliability": "HIGH",
    },
    {
        "keywords": ["50000", "50,000", "engineering students", "government will give"],
        "source_name": "[Demo] National Scholarship Portal",
        "url": "https://scholarships.gov.in/",
        "snippet": "No official scheme on the National Scholarship Portal or any government ministry site matches this claim of a flat Rs 50,000 payout to all engineering students; the claim could not be corroborated.",
        "reliability": "MEDIUM",
    },
]


class MockSearchProvider(SearchProvider):
    def search(self, query: str, max_results: int = 6) -> List[Dict[str, Any]]:
        query_words = set(re.findall(r"[a-zA-Z0-9₹]+", query.lower()))
        if not query_words:
            return []

        scored = []
        for entry in _DEMO_EVIDENCE:
            keyword_hits = sum(1 for kw in entry["keywords"] if kw in query.lower())
            if keyword_hits == 0:
                continue
            scored.append((keyword_hits, entry))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        results = []
        for _, entry in scored[:max_results]:
            results.append(
                {
                    "source_name": entry["source_name"],
                    "url": entry["url"],
                    "snippet": entry["snippet"],
                    "reliability": entry["reliability"],
                }
            )
        return results
