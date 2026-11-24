"""Formulation providers: deterministic reference and optional OpenAI-compatible API."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

SYSTEM_PROMPT = """You are an operations-research modelling assistant.
Translate the user's linear optimization problem into a JSON formulation.
Return JSON only, matching this schema:
{
 "name": string,
 "sense": "min" or "max",
 "variables": [{"name": string, "lower": number|null, "upper": number|null}],
 "objective": {"coefficients": {"variable_name": number}},
 "constraints": [{"name": string, "coefficients": {"variable_name": number},
                  "sense": "<="|">="|"==", "rhs": number}]
}
Use continuous variables. Do not invent constraints. Include all stated bounds.
If a detail is ambiguous, make the most conservative interpretation and explain nothing
outside the JSON. The benchmark will independently validate the formulation and solve it.
"""


class ReferenceProvider:
    """Returns ground-truth formulation; useful only to test the pipeline."""

    def formulate(self, case: dict[str, Any], model: str | None = None) -> str:
        return json.dumps(case["reference"])


class OpenAIProvider:
    """Calls an OpenAI-compatible Chat Completions endpoint."""

    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install optional dependency with: pip install -e '.[llm]'") from exc
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("Set OPENAI_API_KEY before using the OpenAI provider")
        self.client = OpenAI()
        self.model = model

    def formulate(self, case: dict[str, Any], model: str | None = None) -> str:
        response = self.client.chat.completions.create(
            model=model or self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": case["prompt"]},
            ],
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Provider returned an empty response")
        return content


class OllamaProvider:
    """Calls a locally running Ollama model."""

    def __init__(
        self,
        model: str = "qwen2.5:7b",
        host: str = "http://localhost:11434",
    ) -> None:
        self.model = model
        self.host = host.rstrip("/")

    def formulate(
        self,
        case: dict[str, Any],
        model: str | None = None,
    ) -> str:
        payload = {
            "model": model or self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": case["prompt"]},
            ],
            "format": "json",
            "stream": False,
            "options": {"temperature": 0},
        }

        request = urllib.request.Request(
            f"{self.host}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Ollama API error: {detail}") from exc

        content = result.get("message", {}).get("content")

        if not content:
            raise ValueError("Ollama returned an empty response")

        return content
