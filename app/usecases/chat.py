from app.db.models import ChatMessage
from app.repositories.chat_messages import ChatMessagesRepository
from app.services.openrouter_client import OpenRouterClient


class ChatUseCase:
    def __init__(
        self,
        chat_messages_repo: ChatMessagesRepository,
        openrouter_client: OpenRouterClient,
    ) -> None:
        self._chat_messages_repo = chat_messages_repo
        self._openrouter_client = openrouter_client

    async def ask(
        self,
        *,
        user_id: int,
        prompt: str,
        system: str | None,
        max_history: int,
        temperature: float,
    ) -> str:
        history = await self._chat_messages_repo.get_recent_messages(
            user_id=user_id,
            limit=max_history,
        )

        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})

        messages.extend(
            {"role": item.role, "content": item.content}
            for item in history
        )
        messages.append({"role": "user", "content": prompt})

        await self._chat_messages_repo.add_message(
            user_id=user_id,
            role="user",
            content=prompt,
        )

        answer = await self._openrouter_client.create_chat_completion(
            messages=messages,
            temperature=temperature,
        )

        await self._chat_messages_repo.add_message(
            user_id=user_id,
            role="assistant",
            content=answer,
        )
        return answer

    async def get_history(self, *, user_id: int, limit: int = 50) -> list[ChatMessage]:
        return await self._chat_messages_repo.get_recent_messages(user_id=user_id, limit=limit)

    async def clear_history(self, *, user_id: int) -> int:
        return await self._chat_messages_repo.clear_history(user_id=user_id)
