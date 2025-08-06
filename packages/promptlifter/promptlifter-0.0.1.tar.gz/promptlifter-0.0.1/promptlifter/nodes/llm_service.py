import asyncio
import time
from typing import Optional

import httpx

from ..config import (
    ANTHROPIC_API_KEY,
    CUSTOM_LLM_API_KEY,
    CUSTOM_LLM_ENDPOINT,
    CUSTOM_LLM_MODEL,
    GOOGLE_API_KEY,
    LLM_PROVIDER,
    OPENAI_API_KEY,
)


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_calls: int = 10, time_window: float = 60.0) -> None:
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: list[float] = []

    async def acquire(self) -> None:
        """Acquire permission to make an API call."""
        now = time.time()
        # Remove old calls outside the time window
        self.calls = [
            call_time for call_time in self.calls if now - call_time < self.time_window
        ]

        if len(self.calls) >= self.max_calls:
            # Wait until we can make another call
            wait_time = self.time_window - (now - self.calls[0])
            if wait_time > 0:
                await asyncio.sleep(wait_time)

        self.calls.append(time.time())


class CustomLLMService:
    def __init__(self) -> None:
        self.custom_endpoint = CUSTOM_LLM_ENDPOINT
        self.custom_model = CUSTOM_LLM_MODEL
        self.custom_api_key = CUSTOM_LLM_API_KEY
        self.llm_provider = LLM_PROVIDER
        self.rate_limiter = RateLimiter(
            max_calls=20, time_window=60.0
        )  # 20 calls per minute

    async def _try_custom_llm(
        self, messages: list, max_tokens: int = 1000
    ) -> Optional[str]:
        """Try to use custom LLM endpoint (Ollama, Lambda Labs, etc.)."""
        try:
            await self.rate_limiter.acquire()

            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {}
                if self.custom_api_key:
                    headers["Authorization"] = f"Bearer {self.custom_api_key}"

                print(f"🔍 Trying custom LLM: {self.custom_endpoint}")
                print(f"📋 Model: {self.custom_model}")
                # Removed API key logging for security

                # Check if this is an OpenAI-compatible endpoint
                is_openai_compatible = any(
                    domain in self.custom_endpoint.lower()
                    for domain in [
                        "api.openai.com",
                        "api.lambda.ai",
                        "api.together.xyz",
                        "api.perplexity.ai",
                    ]
                )

                if is_openai_compatible:
                    print("🔧 Using OpenAI-compatible API format")
                    payload = {
                        "model": self.custom_model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": 0.3,
                        "stream": False,
                    }
                    response = await client.post(
                        f"{self.custom_endpoint}/chat/completions",
                        json=payload,
                        headers=headers,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        result = (
                            data.get("choices", [{}])[0]
                            .get("message", {})
                            .get("content", "")
                        )
                        return str(result) if result is not None else None
                    else:
                        print(
                            f"❌ OpenAI-compatible API failed: {response.status_code}"
                        )
                        return None
                else:  # Ollama-style API
                    print("🔧 Using Ollama-style API format")
                    chat_payload = {
                        "model": self.custom_model,
                        "messages": messages,
                        "stream": False,
                        "options": {"temperature": 0.3, "num_predict": max_tokens},
                    }
                    try:
                        response = await client.post(
                            f"{self.custom_endpoint}/api/chat",
                            json=chat_payload,
                            headers=headers,
                        )
                        if response.status_code == 200:
                            data = response.json()
                            result = data.get("message", {}).get("content", "")
                            return str(result) if result is not None else None
                        else:
                            print(
                                f"⚠️  Chat API failed ({response.status_code}), "
                                f"trying generate API..."
                            )
                    except Exception as chat_error:
                        print(
                            f"⚠️  Chat API error: {chat_error}, "
                            f"trying generate API..."
                        )

                    # Convert messages to single prompt for generate API
                    prompt = ""
                    for msg in messages:
                        if msg["role"] == "system":
                            prompt += f"System: {msg['content']}\n\n"
                        elif msg["role"] == "user":
                            prompt += f"User: {msg['content']}\n\n"
                        elif msg["role"] == "assistant":
                            prompt += f"Assistant: {msg['content']}\n\n"

                    generate_payload = {
                        "model": self.custom_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.3, "num_predict": max_tokens},
                    }
                    response = await client.post(
                        f"{self.custom_endpoint}/api/generate",
                        json=generate_payload,
                        headers=headers,
                    )
                    if response.status_code == 200:
                        data = response.json()
                        result = data.get("response", "")
                        return str(result) if result is not None else None
                    else:
                        print(f"❌ Generate API also failed: {response.status_code}")
                        return None
        except Exception as e:
            print(f"❌ Custom LLM failed: {e}")
            return None

    async def _try_openai(
        self, messages: list, max_tokens: int = 1000
    ) -> Optional[str]:
        """Try OpenAI API as fallback."""
        if not OPENAI_API_KEY:
            return None

        try:
            await self.rate_limiter.acquire()

            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
                payload = {
                    "model": "gpt-3.5-turbo",
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.3,
                }
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=payload,
                    headers=headers,
                )
                if response.status_code == 200:
                    data = response.json()
                    result = (
                        data.get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )
                    return str(result) if result is not None else None
                else:
                    print(f"❌ OpenAI API failed: {response.status_code}")
                    return None
        except Exception as e:
            print(f"❌ OpenAI failed: {e}")
            return None

    async def _try_anthropic(
        self, messages: list, max_tokens: int = 1000
    ) -> Optional[str]:
        """Try Anthropic API as fallback."""
        if not ANTHROPIC_API_KEY:
            return None

        try:
            await self.rate_limiter.acquire()

            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                }

                # Convert messages to Anthropic format
                system_message = ""
                user_messages = []
                for msg in messages:
                    if msg["role"] == "system":
                        system_message = msg["content"]
                    elif msg["role"] == "user":
                        user_messages.append(msg["content"])

                payload = {
                    "model": "claude-3-sonnet-20240229",
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": "\n".join(user_messages)}],
                }

                if system_message:
                    payload["system"] = system_message

                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    json=payload,
                    headers=headers,
                )
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("content", [{}])[0].get("text", "")
                    return str(result) if result is not None else None
                else:
                    print(f"❌ Anthropic API failed: {response.status_code}")
                    return None
        except Exception as e:
            print(f"❌ Anthropic failed: {e}")
            return None

    async def _try_google(
        self, messages: list, max_tokens: int = 1000
    ) -> Optional[str]:
        """Try Google API as fallback."""
        if not GOOGLE_API_KEY:
            return None

        try:
            await self.rate_limiter.acquire()

            async with httpx.AsyncClient(timeout=30.0) as client:
                # Convert messages to Google format
                prompt = ""
                for msg in messages:
                    if msg["role"] == "system":
                        prompt += f"System: {msg['content']}\n\n"
                    elif msg["role"] == "user":
                        prompt += f"User: {msg['content']}\n\n"
                    elif msg["role"] == "assistant":
                        prompt += f"Assistant: {msg['content']}\n\n"

                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "maxOutputTokens": max_tokens,
                        "temperature": 0.3,
                    },
                }

                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/"
                    f"gemini-pro:generateContent?key={GOOGLE_API_KEY}",
                    json=payload,
                )
                if response.status_code == 200:
                    data = response.json()
                    result = (
                        data.get("candidates", [{}])[0]
                        .get("content", {})
                        .get("parts", [{}])[0]
                        .get("text", "")
                    )
                    return str(result) if result is not None else None
                else:
                    print(f"❌ Google API failed: {response.status_code}")
                    return None
        except Exception as e:
            print(f"❌ Google failed: {e}")
            return None

    async def generate(self, messages: list, max_tokens: int = 1000) -> str:
        """Generate response using configured LLM provider."""
        result = None

        if self.llm_provider == "custom":
            result = await self._try_custom_llm(messages, max_tokens)
        elif self.llm_provider == "openai":
            result = await self._try_openai(messages, max_tokens)
        elif self.llm_provider == "anthropic":
            result = await self._try_anthropic(messages, max_tokens)
        elif self.llm_provider == "google":
            result = await self._try_google(messages, max_tokens)
        else:
            raise Exception(f"Unknown LLM provider: {self.llm_provider}")

        if result:
            print(f"✅ Using {self.llm_provider} LLM")
            return result

        raise Exception(
            f"{self.llm_provider} LLM provider failed. Please check your configuration."
        )


# Global instance
llm_service = CustomLLMService()
