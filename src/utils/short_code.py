import random
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


import string
from typing import Optional


def validate_short_code(code: str, expected_length: Optional[int] = None) -> bool:
    """Проверяет валидность короткого кода"""
    DEFAULT_LENGTH = 6

    if not isinstance(code, str):
        return False

    if expected_length is None:
        expected_length = DEFAULT_LENGTH

    # Проверка длины
    if len(code) != expected_length:
        return False

    # Проверка допустимых символов
    allowed_chars = string.ascii_letters + string.digits
    for char in code:
        if char not in allowed_chars:
            return False

    return True
