from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, NewType

UserID       = NewType("UserID", int)
TelegramID   = NewType("TelegramID", int)


class Role(Enum):
    CANDIDATE = "candidate"
    WORKER = "worker"
    ADMIN = "admin"

@dataclass
class User:
    id: UserID
    telegram_id: TelegramID
    username: Optional[str]   = None
    full_name: Optional[str]  = None
    role: Role                = Role.CANDIDATE
    created_at: datetime      = field(default_factory=datetime.utcnow)


