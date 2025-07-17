from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, NewType

# ——— кастомные примитивы ———
UserID       = NewType("UserID", int)
TelegramID   = NewType("TelegramID", int)

class Role(Enum):
    CANDIDATE = "candidate"
    # при необходимости добавьте: ADMIN = "admin", MODERATOR = "moderator" и т.д.

# ——— доменный класс ———
@dataclass
class User:
    """
    Доменная модель для таблицы users.
    """
    id: UserID
    telegram_id: TelegramID
    username: Optional[str]   = None
    full_name: Optional[str]  = None
    role: Role                = Role.CANDIDATE
    created_at: datetime      = field(default_factory=datetime.utcnow)
