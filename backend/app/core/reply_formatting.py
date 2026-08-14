"""Formats a ClaimResult as a plain-text WhatsApp reply.

Mirrors frontend/src/lib/share.ts's buildShareText — same idea, same
channel (WhatsApp), just generated server-side for an inbound message
instead of client-side for an outbound share.
"""

from ..schemas import ClaimResult

VERDICT_EMOJI = {
    "VERIFIED": "🟢",
    "FALSE": "🔴",
    "MISLEADING": "🟡",
    "UNVERIFIED": "⚪",
}

MAX_REPLY_CHARS = 1500  # comfortably under WhatsApp/Twilio's message size limits


def format_whatsapp_reply(result: ClaimResult) -> str:
    emoji = VERDICT_EMOJI.get(result.verdict.value, "⚪")
    lines = [
        f"{emoji} *{result.verdict.value}* (Evidence: {result.evidence_strength.value})",
        "",
        f'Claim: "{result.normalized_claim}"',
        "",
        result.explanation,
    ]

    if result.sources:
        lines.append("")
        lines.append("Sources:")
        for source in result.sources[:3]:
            lines.append(f"- {source.source_name}: {source.source_url}")

    if result.previously_verified:
        lines.append("")
        lines.append(f"(Checked {result.check_count}x before)")

    lines.append("")
    lines.append("— Parakh: Before you believe it. Verify it.")

    text = "\n".join(lines)
    if len(text) > MAX_REPLY_CHARS:
        text = text[: MAX_REPLY_CHARS - 1].rstrip() + "…"
    return text


def format_help_reply() -> str:
    return (
        "👋 I'm *Parakh*, an AI fact-checker.\n\n"
        "Send me a forwarded message, a claim, or a screenshot of one, "
        "and I'll check it against reliable sources and tell you if it's "
        "🟢 Verified, 🔴 False, 🟡 Misleading, or ⚪ Unverified."
    )


def format_error_reply() -> str:
    return (
        "Sorry, I couldn't check that claim right now — something went wrong "
        "on my end. Please try again in a moment."
    )
