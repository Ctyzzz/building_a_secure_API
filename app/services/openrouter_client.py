import httpx

from app.core.errors import ExternalServiceError


class OpenRouterClient:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        site_url: str,
        app_name: str,
        timeout: float = 30.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.site_url = site_url
        self.app_name = app_name
        self.timeout = timeout

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": self.site_url,
            "X-Title": self.app_name,
            "Content-Type": "application/json",
        }

    async def create_chat_completion(
        self,
        *,
        messages: list[dict[str, str]],
        temperature: float,
    ) -> str:
        if not self.api_key:
            raise ExternalServiceError("OPENROUTER_API_KEY is not configured")

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }
        url = f"{self.base_url}/chat/completions"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=self._headers)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text
            raise ExternalServiceError(
                f"OpenRouter returned {exc.response.status_code}: {detail}",
            ) from exc
        except httpx.HTTPError as exc:
            raise ExternalServiceError("Failed to call OpenRouter") from exc

        data = response.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ExternalServiceError("Invalid OpenRouter response format") from exc

        if not isinstance(content, str) or not content.strip():
            raise ExternalServiceError("OpenRouter returned an empty answer")

        return content
