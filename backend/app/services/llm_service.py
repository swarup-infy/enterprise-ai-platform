"""
LLM Service.

Provides a centralized asynchronous interface to the configured LLM provider.

Current provider:
    Groq

Responsibilities:
    - Generate single-turn responses.
    - Generate multi-turn chat responses.
    - Validate LLM configuration.
    - Retry transient provider failures.
    - Perform lightweight health checks.
    - Centralize provider configuration.
"""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from typing import Any

from groq import AsyncGroq

from app.common.logging.logger import get_logger
from app.core.config import settings


logger = get_logger(__name__)


class LLMService:
    """
    Centralized asynchronous LLM service.

    The service currently uses Groq as the LLM provider.
    """

    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 1.0

    def __init__(self) -> None:
        """
        Initialize the Groq client.
        """

        api_key = settings.GROQ_API_KEY
        model = settings.GROQ_MODEL

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured."
            )

        if not model:
            raise RuntimeError(
                "GROQ_MODEL is not configured."
            )

        self.client = AsyncGroq(
            api_key=api_key,
        )

        self.model = model

    # ==========================================================================
    # Generate
    # ==========================================================================

    async def generate(
        self,
        prompt: str,
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
        system_prompt: str = (
            "You are an expert Enterprise AI assistant."
        ),
    ) -> str:
        """
        Generate a response from Groq.

        Args:
            prompt:
                User prompt.

            temperature:
                Optional generation temperature. Falls back to settings.

            max_tokens:
                Optional maximum completion tokens. Falls back to settings.

            system_prompt:
                System instruction.

        Returns:
            Generated response text.

        Raises:
            ValueError:
                If the prompt is empty.

            RuntimeError:
                If Groq returns an invalid response or generation fails.
        """

        if not isinstance(prompt, str):
            raise TypeError(
                "prompt must be a string."
            )

        prompt = prompt.strip()

        if not prompt:
            raise ValueError(
                "prompt cannot be empty."
            )

        system_prompt = system_prompt.strip()

        if not system_prompt:
            raise ValueError(
                "system_prompt cannot be empty."
            )

        effective_temperature = (
            temperature
            if temperature is not None
            else settings.GROQ_TEMPERATURE
        )

        effective_max_tokens = (
            max_tokens
            if max_tokens is not None
            else settings.GROQ_MAX_OUTPUT_TOKENS
        )

        response = await self._request(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=effective_temperature,
            max_tokens=effective_max_tokens,
        )

        return self._extract_response_text(
            response
        )

    # ==========================================================================
    # Chat
    # ==========================================================================

    async def chat(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate a response for a multi-turn conversation.

        Args:
            messages:
                Chat messages in OpenAI-compatible format.

            temperature:
                Optional generation temperature.

            max_tokens:
                Optional maximum completion tokens.

        Returns:
            Generated response text.
        """

        if not messages:
            raise ValueError(
                "messages cannot be empty."
            )

        normalized_messages: list[dict[str, Any]] = []

        for message in messages:
            if not isinstance(message, dict):
                raise TypeError(
                    "Each chat message must be a dictionary."
                )

            role = message.get("role")
            content = message.get("content")

            if not isinstance(role, str) or not role.strip():
                raise ValueError(
                    "Each chat message must contain a valid role."
                )

            if not isinstance(content, str) or not content.strip():
                raise ValueError(
                    "Each chat message must contain non-empty content."
                )

            normalized_messages.append(
                {
                    "role": role.strip(),
                    "content": content.strip(),
                }
            )

        effective_temperature = (
            temperature
            if temperature is not None
            else settings.GROQ_TEMPERATURE
        )

        effective_max_tokens = (
            max_tokens
            if max_tokens is not None
            else settings.GROQ_MAX_OUTPUT_TOKENS
        )

        response = await self._request(
            messages=normalized_messages,
            temperature=effective_temperature,
            max_tokens=effective_max_tokens,
        )

        return self._extract_response_text(
            response
        )

    # ==========================================================================
    # Request
    # ==========================================================================

    async def _request(
        self,
        *,
        messages: Sequence[dict[str, Any]],
        temperature: float,
        max_tokens: int,
    ) -> Any:
        """
        Execute a Groq request with retry handling.

        Retries are intended for transient provider/network failures.
        """

        last_exception: Exception | None = None

        for attempt in range(
            self.MAX_RETRIES + 1
        ):
            try:
                return await self.client.chat.completions.create(
                    model=self.model,
                    temperature=temperature,
                    max_completion_tokens=max_tokens,
                    messages=list(messages),
                )

            except Exception as exc:
                last_exception = exc

                if attempt >= self.MAX_RETRIES:
                    logger.exception(
                        "Groq LLM request failed after retries.",
                        model=self.model,
                        attempts=attempt + 1,
                    )
                    break

                delay = (
                    self.INITIAL_RETRY_DELAY
                    * (2**attempt)
                )

                logger.warning(
                    "Groq LLM request failed; retrying.",
                    model=self.model,
                    attempt=attempt + 1,
                    max_retries=self.MAX_RETRIES,
                    retry_delay=delay,
                    error=str(exc),
                )

                await asyncio.sleep(delay)

        raise RuntimeError(
            "LLM generation failed."
        ) from last_exception

    # ==========================================================================
    # Response Handling
    # ==========================================================================

    @staticmethod
    def _extract_response_text(
        response: Any,
    ) -> str:
        """
        Safely extract generated text from a Groq response.
        """

        choices = getattr(
            response,
            "choices",
            None,
        )

        if not choices:
            raise RuntimeError(
                "LLM returned no completion choices."
            )

        message = getattr(
            choices[0],
            "message",
            None,
        )

        if message is None:
            raise RuntimeError(
                "LLM response did not contain a message."
            )

        content = getattr(
            message,
            "content",
            None,
        )

        if not isinstance(content, str):
            raise RuntimeError(
                "LLM response contained no text content."
            )

        content = content.strip()

        if not content:
            raise RuntimeError(
                "LLM returned an empty response."
            )

        return content

    # ==========================================================================
    # Health Check
    # ==========================================================================

    async def health_check(self) -> bool:
        """
        Check whether the Groq service is reachable.

        Uses the models endpoint instead of consuming a normal
        LLM completion request.
        """

        try:
            await self.client.models.list()

            logger.info(
                "Groq health check succeeded.",
                model=self.model,
            )

            return True

        except Exception:
            logger.exception(
                "Groq health check failed.",
                model=self.model,
            )

            return False

    # ==========================================================================
    # Cleanup
    # ==========================================================================

    async def close(self) -> None:
        """
        Close the underlying Groq client.
        """

        await self.client.close()


__all__ = [
    "LLMService",
]