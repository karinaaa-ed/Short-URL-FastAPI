import pytest
from src.utils.short_code import generate_short_code, validate_short_code

def test_generate_short_code():
    code = generate_short_code()
    assert len(code) == 6
    assert code.isalnum()

@pytest.mark.parametrize("code,valid", [
    ("abc123", True),
    ("ABCDEF", True),
    ("123456", True),
    ("abc-12", False),
    ("", False),
    ("a"*100, False),
    (None, False),
])
def test_validate_short_code(code, valid):
    assert validate_short_code(code) == valid