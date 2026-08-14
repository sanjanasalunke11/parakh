import json
import time
from typing import Any, Dict, List

import httpx

from ...config import settings
from .base import LLMProvider

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = 2.0

EXTRACT_TOOL = {
    "type": "function",
    "function": {
        "name": "submit_claim_extraction",
        "description": "Submit the extracted factual claim and category from a raw forwarded message.",
        "parameters": {
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
    },
}

VERIFY_TOOL = {
    "type": "function",
    "function": {
        "name": "submit_verification",
        "description": "Submit a verdict for a claim based strictly on the provided evidence snippets.",
        "parameters": {
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
    },
}

VERIFY_SYSTEM_PROMPT = (
    "You are a rigorous fact-checking assistant for Parakh, an anti-misinformation tool. "
    "You must judge the CLAIM using ONLY the EVIDENCE snippets provided in the user message. "
    "Do not use outside knowledge, do not assume anything not stated in the evidence, and never "
    "invent sources or facts. If the evidence is insufficient, absent, or does not clearly address "
    "the claim, you MUST respond UNVERIFIED. Use MISLEADING when the claim has a true kernel but is "
    "exaggerated, out of context, or implies something false. Use FALSE only when evidence directly "
    "contradicts the claim. Use VERIFIED only when evidence directly corroborates the claim's key facts. "
    "You must always respond by calling the submit_verification tool."
)


class GroqLLMProvider(LLMProvider):
    """Groq's OpenAI-compatible chat completions API, used for fast, low-cost
    claim extraction and verification reasoning. Same contract as the other
    LLM providers — the pipeline doesn't know or care which one is active.
    """

    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is not set")
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL

    def extract_claim(self, raw_text: str) -> Dict[str, Any]:
        return self._call_tool(
            tool=EXTRACT_TOOL,
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

    def verify_claim(self, claim: str, evidence: List[Dict[str, Any]]) -> Dict[str, Any]:
        evidence_block = "\n".join(
            f"[{i + 1}] ({e.get('reliability', 'LOW')} reliability) {e.get('source_name', 'Unknown source')}: "
            f"{e.get('snippet', '')} (source: {e.get('url', '')})"
            for i, e in enumerate(evidence)
        )
        return self._call_tool(
            tool=VERIFY_TOOL,
            messages=[
                {"role": "system", "content": VERIFY_SYSTEM_PROMPT},
                {"role": "user", "content": f"CLAIM: {claim}\n\nEVIDENCE:\n{evidence_block}"},
            ],
        )

    def _call_tool(self, tool: Dict[str, Any], messages: List[Dict[str, str]]) -> Dict[str, Any]:
        function_name = tool["function"]["name"]
        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                response = httpx.post(
                    GROQ_URL,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": self.model,
                        "messages": messages,
                        "tools": [tool],
                        "tool_choice": {"type": "function", "function": {"name": function_name}},
                        "temperature": 0.1,
                        "max_tokens": 768,
                    },
                    timeout=30,
                )
                # Groq's free tier has a fairly low requests-per-minute cap —
                # a 429 here is routine, not exceptional, so back off and retry
                # a couple of times before giving up.
                if response.status_code == 429 and attempt < MAX_RETRIES:
                    retry_after = float(response.headers.get("retry-after", RETRY_BACKOFF_SECONDS))
                    time.sleep(min(retry_after, 10.0))
                    continue
                response.raise_for_status()
                data = response.json()
                break
            except Exception as exc:
                last_error = exc
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_SECONDS)
                    continue
                raise RuntimeError(f"Groq LLM call failed: {exc}") from exc
        else:
            raise RuntimeError(f"Groq LLM call failed: {last_error}")

        try:
            tool_calls = data["choices"][0]["message"]["tool_calls"]
            arguments = tool_calls[0]["function"]["arguments"]
            return json.loads(arguments)
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Groq did not return a valid structured tool response: {exc}") from exc
