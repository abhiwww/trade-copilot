from typing import AsyncGenerator, Dict, Any, List, Optional
import asyncio
import json
import httpx
from app.core.config import settings
from app.core.exceptions import global_exception_handler

class LLMService:
    """Model gateway supporting real-time token streaming and guardrails."""

    def __init__(self):
        self.provider = settings.ai_provider if hasattr(settings, "ai_provider") else "ollama"
        self.ollama_base_url = settings.ollama_base_url if hasattr(settings, "ollama_base_url") else "http://localhost:11434"
        self.ollama_model = settings.ollama_model if hasattr(settings, "ollama_model") else "qwen2.5-coder:7b"
        self.api_key = settings.api_key if hasattr(settings, "api_key") else "simulated-key"
        self.api_url = settings.api_url if hasattr(settings, "api_url") else "https://api.openai.com/v1/chat/completions"
        self.model = settings.model if hasattr(settings, "model") else "gpt-4o"

    def _apply_guardrails(self, content: str) -> bool:
        """Basic output guardrail to block forbidden content or hallucinations."""
        forbidden_patterns = ["I am a language model", "As an AI", "ignore previous instructions"]
        for pattern in forbidden_patterns:
            if pattern.lower() in content.lower():
                return False
        return True

    async def chat_completion_stream(self, system_prompt: str, user_prompt: str,
                                   temperature: float = 0.4, max_tokens: int = 1024) -> AsyncGenerator[str, None]:
        """Stream tokens from the LLM provider."""

        if self.provider == "ollama":
            payload = {
                "model": self.ollama_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": True,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            }
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream("POST", f"{self.ollama_base_url}/api/chat", json=payload) as response:
                    async for line in response.aiter_lines():
                        if not line: continue
                        try:
                            data = json.loads(line)
                            token = data.get("message", {}).get("content", "")
                            if token:
                                if self._apply_guardrails(token):
                                    yield token
                        except json.JSONDecodeError:
                            continue

        elif self.provider == "openai":
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": True,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", self.api_url, json=payload, headers=headers) as response:
                    async for line in response.aiter_lines():
                        if not line or not line.startswith("data: "): continue
                        data_str = line[6:].strip()
                        if data_str == "[DONE]": break
                        try:
                            data = json.loads(data_str)
                            token = data["choices"][0]["delta"].get("content", "")
                            if token:
                                if self._apply_guardrails(token):
                                    yield token
                        except (json.JSONDecodeError, KeyError):
                            continue
        else:
            # Simulated streaming for development
            full_text = "This is a simulated streaming response for Trade Copilot."
            for char in full_text:
                yield char
                await asyncio.sleep(0.02)

    async def chat_completion(self, system_prompt: str, user_prompt: str,
                              temperature: float = 0.4, max_tokens: int = 1024) -> str:
        """Non-streaming version (aggregates the stream)."""
        tokens = []
        async for token in self.chat_completion_stream(system_prompt, user_prompt, temperature, max_tokens):
            tokens.append(token)
        return "".join(tokens).strip()

    async def call_llm(self, system_prompt: str, user_prompt: str, json_mode: bool = True) -> Dict[str, Any]:
        """Structured output call (re-implemented to use the core logic)."""
        # For structured output, we usually don't stream, we just get the final JSON
        result = await self.chat_completion(system_prompt + "\nReturn JSON.", user_prompt)
        try:
            return json.loads(result)
        except:
            return {"text": result}

    async def health_check(self) -> Dict[str, Any]:
        """Check whether the configured AI provider is reachable."""
        if self.provider == "ollama":
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    resp = await client.get(f"{self.ollama_base_url}/api/tags")
                    models = [m.get("name", "") for m in resp.json().get("models", [])]
                    available = resp.status_code == 200 and any(self.ollama_model in m for m in models)
                    return {"provider": "ollama", "available": available, "model": self.ollama_model,
                            "detail": None if available else "model not installed"}
            except Exception as exc:
                return {"provider": "ollama", "available": False, "model": self.ollama_model,
                        "detail": f"Ollama unreachable: {exc}"}
        # Cloud provider: consider configured when an API key is present
        configured = bool(self.api_key) and self.api_key != "simulated-key"
        return {"provider": self.provider, "available": configured, "model": self.model,
                "detail": None if configured else "no API key configured"}

llm_service = LLMService()
