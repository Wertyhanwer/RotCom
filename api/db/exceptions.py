

class DatabaseError(Exception):
    ...


class UniqueViolationError(DatabaseError):
    """Запись нарушает уникальный индекс (например, логин или email уже заняты)."""
