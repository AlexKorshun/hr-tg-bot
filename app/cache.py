import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple, List
from aiogram import Bot, Dispatcher, types
from app.repository.pg import update_user_last_use

class UserState:
    def __init__(
        self,
        pending_action: str,
        role: object,
        messages: Optional[List[types.Message]] = None,
        data: Optional[dict] = None
    ):
        self.pending_action = pending_action
        self.role = role
        self.messages = messages or []
        self.data = data or {}

class UserStateCache:
    def __init__(self, bot: Bot, ttl: timedelta, cleanup_interval: timedelta):
        self.bot = bot
        self.ttl = ttl
        self.cleanup_interval = cleanup_interval

        self._data: Dict[int, UserState] = {}
        self._expiration: Dict[int, datetime] = {}

        self._lock = asyncio.Lock()

        asyncio.create_task(self._cleanup_loop())

    async def _cleanup_loop(self):
        while True:
            await asyncio.sleep(self.cleanup_interval.total_seconds())
            await self._cleanup()

    async def _cleanup(self):
        now = datetime.utcnow()
        async with self._lock:
            expired_users = [
                user_id for user_id, exp in self._expiration.items()
                if exp < now
            ]
            for user_id in expired_users:
                state = self._data.get(user_id)
                if state:
                    for msg in state.messages:
                        try:
                            await self.bot.delete_message(
                                chat_id=msg.chat.id,
                                message_id=msg.message_id
                            )
                        except Exception:
                            logging.exception(
                                f"Не удалось удалить сообщение {msg.message_id}"
                                f" для пользователя {user_id}"
                            )
                await update_user_last_use(user_id)
                self._data.pop(user_id, None)
                self._expiration.pop(user_id, None)

    async def set(self, user_id: int, state: UserState):
        async with self._lock:
            self._data[user_id] = state
            self._expiration[user_id] = datetime.utcnow() + self.ttl

    async def get(self, user_id: int) -> Tuple[Optional[UserState], bool]:
        async with self._lock:
            state = self._data.get(user_id)
            return state, (state is not None)

    async def delete(self, user_id: int):
        async with self._lock:
            state = self._data.pop(user_id, None)
            self._expiration.pop(user_id, None)

        if state:
            for msg in state.messages:
                try:
                    await self.bot.delete_message(
                        chat_id=msg.chat.id,
                        message_id=msg.message_id
                    )
                except Exception:
                    logging.exception(
                        f"Не удалось удалить сообщение {msg.message_id}"
                        f" для пользователя {user_id}"
                    )

    # async def add_message(self, user_id: int, msg: types.Message):
    #     async with self._lock:
    #         state = self._data.get(user_id)
    #         if not state:
    #             state = UserState(pending_action="", role=None, messages=[])
    #         state.messages.append(msg)
    #         self._data[user_id] = state
    #         self._expiration[user_id] = datetime.utcnow() + self.ttl

    async def add_message(self, user_id: int, msg: types.Message):
        async with self._lock:
            state = self._data.get(user_id)
            if not state:
                state = UserState(pending_action="", role=None, messages=[]) # <-- Здесь тоже создается новый стейт
            state.messages.append(msg)
            self._data[user_id] = state
            self._expiration[user_id] = datetime.utcnow() + self.ttl

    # async def update_action(self, user_id: int, action: str):
    #     async with self._lock:
    #         state = self._data.get(user_id)
    #         if not state:
    #             state = UserState(pending_action=action, role=None, messages=[])
    #         else:
    #             state.pending_action = action
    #         self._data[user_id] = state
    #         self._expiration[user_id] = datetime.utcnow() + self.ttl

    async def update_action(self, user_id: int, action: str):
        async with self._lock:
            state = self._data.get(user_id)
            if not state:
                state = UserState(pending_action=action, role=None, messages=[])
            else:
                state.pending_action = action
            self._data[user_id] = state
            self._expiration[user_id] = datetime.utcnow() + self.ttl