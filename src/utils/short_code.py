import random
import string
from typing import Optional


def generate_short_code(length: Optional[int] = None) -> str:
    """Генерирует случайный код с гарантированной валидацией"""
    DEFAULT_LENGTH = 6

    # Если длина не указана, используем дефолтную
    if length is None:
        length = DEFAULT_LENGTH

    # Явная проверка типа и значения
    if not isinstance(length, int) or length <= 0:
        raise ValueError(
            f"Invalid length: {length}. Must be positive integer, got {type(length)}"
        )

    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))