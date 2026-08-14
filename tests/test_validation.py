import pytest
from pydantic import ValidationError

from main import ChatRequest


def test_valid_question():
    request = ChatRequest(question="안녕하세요")
    assert request.question == "안녕하세요"


def test_whitespace_question_rejected():
    with pytest.raises(ValidationError):
        ChatRequest(question="     ")


def test_question_too_long_rejected():
    with pytest.raises(ValidationError):
        ChatRequest(question="a" * 501)