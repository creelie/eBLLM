"""Proposers: where candidate steps come from.

A proposer turns a prompt into text.  The package contains no model and no weights; the hosted
connectors call each provider's public interface with the user's own key (read from the
environment), and `local` talks to any server with an OpenAI-compatible interface (Ollama,
vLLM, llama.cpp, LM Studio), so open-weight models run on the user's machine.  Nothing a
proposer returns is trusted: every candidate goes through the checks.

    provider    endpoint                                                key variable
    anthropic   https://api.anthropic.com/v1/messages                   ANTHROPIC_API_KEY
    openai      https://api.openai.com/v1/chat/completions              OPENAI_API_KEY
    gemini      https://generativelanguage.googleapis.com/v1beta/...    GEMINI_API_KEY
    mistral     https://api.mistral.ai/v1/chat/completions              MISTRAL_API_KEY
    xai         https://api.x.ai/v1/chat/completions                    XAI_API_KEY
    deepseek    https://api.deepseek.com/chat/completions               DEEPSEEK_API_KEY
    openrouter  https://openrouter.ai/api/v1/chat/completions           OPENROUTER_API_KEY
    local       $EBLLM_LOCAL_URL (default http://localhost:11434/v1)    none

The model is chosen with `model=` or the variable EBLLM_MODEL_<PROVIDER> (for example
EBLLM_MODEL_OPENAI); model names change often, so the package does not fix them, except that
`anthropic` defaults to claude-opus-5-5.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

PROVIDERS: Dict[str, Dict[str, str]] = {
    "anthropic": {"url": "https://api.anthropic.com/v1/messages", "key": "ANTHROPIC_API_KEY",
                  "style": "anthropic", "default_model": "claude-opus-5-5"},
    "openai": {"url": "https://api.openai.com/v1/chat/completions", "key": "OPENAI_API_KEY", "style": "chat"},
    "gemini": {"url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
               "key": "GEMINI_API_KEY", "style": "gemini"},
    "mistral": {"url": "https://api.mistral.ai/v1/chat/completions", "key": "MISTRAL_API_KEY", "style": "chat"},
    "xai": {"url": "https://api.x.ai/v1/chat/completions", "key": "XAI_API_KEY", "style": "chat"},
    "deepseek": {"url": "https://api.deepseek.com/chat/completions", "key": "DEEPSEEK_API_KEY", "style": "chat"},
    "openrouter": {"url": "https://openrouter.ai/api/v1/chat/completions", "key": "OPENROUTER_API_KEY",
                   "style": "chat"},
    "local": {"url": "{local}/chat/completions", "key": "", "style": "chat"},
}

Opener = Callable[[urllib.request.Request, float], bytes]


def _default_opener(req: urllib.request.Request, timeout: float) -> bytes:
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


class Proposer:
    name = "proposer"

    def complete(self, prompt: str) -> str:
        raise NotImplementedError


@dataclass
class ModelProposer(Proposer):
    """A hosted or local language model behind one of the interfaces of PROVIDERS."""
    provider: str
    model: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: float = 600.0
    opener: Opener = field(default=_default_opener, repr=False)

    def __post_init__(self):
        if self.provider not in PROVIDERS:
            raise ValueError(f"unknown provider {self.provider!r}; known: {', '.join(PROVIDERS)}")
        spec = PROVIDERS[self.provider]
        self.model = (self.model or os.environ.get(f"EBLLM_MODEL_{self.provider.upper()}")
                      or spec.get("default_model"))
        if not self.model:
            raise ValueError(f"choose a model: model=... or EBLLM_MODEL_{self.provider.upper()}")
        self.name = f"{self.provider}:{self.model}"

    def request(self, prompt: str) -> urllib.request.Request:
        spec = PROVIDERS[self.provider]
        key = os.environ.get(spec["key"], "") if spec["key"] else ""
        if spec["key"] and not key:
            raise RuntimeError(f"set {spec['key']} to use {self.provider}")
        headers = {"content-type": "application/json"}
        if spec["style"] == "anthropic":
            body = {"model": self.model, "max_tokens": self.max_tokens, "temperature": self.temperature,
                    "messages": [{"role": "user", "content": prompt}]}
            headers.update({"x-api-key": key, "anthropic-version": "2023-06-01"})
            url = spec["url"]
        elif spec["style"] == "gemini":
            body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": self.temperature, "maxOutputTokens": self.max_tokens}}
            headers["x-goog-api-key"] = key
            url = spec["url"].format(model=self.model)
        else:
            body = {"model": self.model, "max_tokens": self.max_tokens, "temperature": self.temperature,
                    "messages": [{"role": "user", "content": prompt}]}
            if key:
                headers["authorization"] = f"Bearer {key}"
            url = spec["url"].format(local=os.environ.get("EBLLM_LOCAL_URL", "http://localhost:11434/v1").rstrip("/"))
        return urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")

    def parse(self, raw: bytes) -> str:
        data = json.loads(raw)
        style = PROVIDERS[self.provider]["style"]
        if style == "anthropic":
            return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
        if style == "gemini":
            parts = data["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts)
        return data["choices"][0]["message"]["content"]

    def complete(self, prompt: str) -> str:
        return self.parse(self.opener(self.request(prompt), self.timeout))


@dataclass
class ScriptedProposer(Proposer):
    """Returns fixed answers in turn: reproducible runs and tests."""
    answers: List[str]
    name: str = "scripted"
    i: int = 0

    def complete(self, prompt: str) -> str:
        a = self.answers[self.i % len(self.answers)]
        self.i += 1
        return a


def extract_json_list(text: str) -> List[dict]:
    """The candidates in a model reply: the first JSON list in the text, or JSON objects one per line."""
    m = re.search(r"\[.*\]", text, re.S)
    if m:
        try:
            v = json.loads(m.group(0))
            if isinstance(v, list):
                return [x for x in v if isinstance(x, dict)]
        except json.JSONDecodeError:
            pass
    out = []
    for line in text.splitlines():
        line = line.strip().rstrip(",")
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def available() -> List[str]:
    """Providers whose key is set (and `local`, which needs none)."""
    return [p for p, s in PROVIDERS.items() if not s["key"] or os.environ.get(s["key"])]
