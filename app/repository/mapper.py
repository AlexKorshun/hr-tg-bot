from app.models.user import User, UserID, TelegramID, Role

def map_user_row(row: dict) -> User:

    return User(
        id=UserID(row["id"]),
        telegram_id=TelegramID(row["telegram_id"]),
        username=row.get("username"),
        full_name=row.get("full_name"),
        role=Role(row["role"]),
        created_at=row["created_at"],
    )
