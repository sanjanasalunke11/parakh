from typing import Any, Dict, List

import anthropic

from ...config import settings
from .base import LLMProvider

EXTRACT_TOOL = {
    "name": "submit_claim_extraction",
    "description": "Submit the extracted factual claim and category from a raw forwarded message.",
    "input_schema": {
        "type": "object",
        "properties": {
            "normalized_claim": {
                "type": "string",
                "description": (
                    "A short, neutral, factual restatement of the core checkable claim in the "
                    "message. Strip greetings, emotional language, forwarding instructions "
                    "('please share'), and emojis. Preserve numbers, names, dates and specifics."
                ),
            },
            "category": {
                "type": "string",
                "enum": [
                    "Health", "Government Scheme", "Politics", "Finance",
                    "Science & Technology", "Communal/Social", "Crime & Safety",
                    "Entertainment", "Other",
                ],
            },
        },
        "required": ["normalized_claim", "category"],
    },
}

VERIFY_TOOL = {
    "name": "submit_verification",
    "description": "Submit a verdict for a claim based strictly on the provided evidence snippets.",
    "input_schema": {
        "type": "object",
        "properties": {
            "verdict": {
                "type": "string",
                "enum": ["VERIFIED", "FALSE", "MISLEADING", "UNVERIFIED"],
            },
            "evidence_strength": {
                "type": "string",
                "enum": ["LOW", "MEDIUM", "HIGH"],
            },
            "explanation": {
                "type": "string",
                "description": "2-4 sentence plain-language explanation referencing which evidence supports the verdict.",
            },
        },
        "required": ["verdict", "evidence_strength", "explanation"],
    },
}

VERIFY_SYSTEM_PROMPT = (
    "You are a rigorous fact-checking assistant for Parakh, an anti-misinformation tool. "
    "You must judge the CLAIM using ONLY the EVIDENCE snippets provided in the user message. "
    "Do not use outside knowledge, do not assume anything not stated in the evidence, and never "
    "invent sources or facts. If the evidence is insufficient, absent, or does not clearly address "
    "the claim, you MUST respond UNVERIFIED. Use MISLEADING when the claim has a true kernel but is "
    "exaggerated, out of context, or implies something false. Use FALSE only when evidence directly "
    "contradicts the claim. Use VERIFIED only when evidence directly corroborates the claim's key facts."
)


class AnthropicLLMProvider(LLMProvider):
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL

    def extract_claim(self, raw_text: str) -> Dict[str, Any]:
        message = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            tools=[EXTRACT_TOOL],
            tool_choice={"type": "tool", "name": "submit_claim_extraction"},
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Extract the core factual, checkable claim from this forwarded message.\n\n"
                        f"MESSAGE:\n{raw_text}"
                    ),
                }
            ],
        )
        return self._extract_tool_input(message)

    def verify_claim(self, claim: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        evidence_block = "\n".join(
            f"[{i + 1}] ({e.get('reliability', 'LOW')} reliability) {e.get('source_name', 'Unknown source')}: "
            f"{e.get('snippet', '')} (source: {e.get('url', '')})"
            for i, e in enumerate(evidence)
        )
        message = self.client.messages.create(
            model=self.model,
            max_tokens=768,
            system=VERIFY_SYSTEM_PROMPT,
            tools=[VERIFY_TOOL],
            tool_choice={"type": "tool", "name": "submit_verification"},
            messages=[
                {
                    "role": "user",
                    "content": f"CLAIM: {claim}\n\nEVIDENCE:\n{evidence_block}",
                }
            ],
        )
        return self._extract_tool_input(message)

    @staticmethod
    def _extract_tool_input(message) -> Dict[str, Any]:
        for block in message.content:
            if block.type == "tool_use":
                return block.input
        raise RuntimeError("LLM did not return a structured tool response.")
