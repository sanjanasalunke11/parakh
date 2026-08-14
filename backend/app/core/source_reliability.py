"""Static reliability ranking for evidence sources.

This is deliberately NOT decided by the LLM — reliability is a fixed,
auditable lookup so a model can never talk its way into treating a
random blog as equivalent to PIB or WHO.
"""

from urllib.parse import urlparse

HIGH_RELIABILITY_DOMAINS = {
    # Government / official (India)
    "pib.gov.in", "india.gov.in", "mygov.in", "rbi.org.in", "eci.gov.in",
    "icmr.gov.in", "mohfw.gov.in", "prsindia.org", "nic.in",
    # International bodies / global health & science authorities
    "who.int", "un.org", "unicef.org", "ncbi.nlm.nih.gov", "pubmed.ncbi.nlm.nih.gov",
    "nih.gov", "cdc.gov", "fda.gov", "nasa.gov",
    "cancer.org", "cancerresearchuk.org", "wcrf.org", "mayoclinic.org", "nhs.uk",
    # Wire services / major broadcasters
    "reuters.com", "apnews.com", "bbc.com", "pti.in",
    # Dedicated fact-checkers
    "altnews.in", "boomlive.in", "factcheck.org", "snopes.com",
    "politifact.com", "vishvasnews.com", "factchecker.in",
}

MEDIUM_RELIABILITY_DOMAINS = {
    "thehindu.com", "ndtv.com", "indianexpress.com", "hindustantimes.com",
    "timesofindia.indiatimes.com", "livemint.com", "news18.com",
    "indiatoday.in", "theprint.in", "scroll.in",
}


def get_reliability_tier(url: str) -> str:
    """Returns 'HIGH' | 'MEDIUM' | 'LOW' for a given source URL."""
    try:
        domain = urlparse(url).netloc.lower()
    except Exception:
        return "LOW"

    if domain.startswith("www."):
        domain = domain[4:]

    if not domain:
        return "LOW"

    # Any government domain (India-specific TLDs, or the generic .gov / .gov.uk
    # used by the US, UK, and many other national governments) is treated as
    # HIGH — an official source is an official source regardless of country.
    if domain.endswith(".gov.in") or domain.endswith(".nic.in") or domain.endswith(".gov") or domain.endswith(".gov.uk"):
        return "HIGH"

    for d in HIGH_RELIABILITY_DOMAINS:
        if domain == d or domain.endswith("." + d):
            return "HIGH"

    for d in MEDIUM_RELIABILITY_DOMAINS:
        if domain == d or domain.endswith("." + d):
            return "MEDIUM"

    return "LOW"


RELIABILITY_SORT_ORDER = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
