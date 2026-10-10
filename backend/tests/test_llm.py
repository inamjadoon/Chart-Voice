import os

import pytest

from app.llm import service
from app.llm.number_check import check_numbers

TABLE = {"columns": ["Month", "Sales"], "rows": [["Jan", 20], ["Feb", 25], ["May", 55]]}
FACTS = {"series": [{"name": "Sales", "max": {"label": "May", "value": 55}, "change_pct": 175.0, "total": 100}]}


def test_numbers_from_data_pass():
    assert check_numbers("Sales peaked at 55 in May, up 175% and 100 in total.", TABLE, FACTS) == []


def test_invented_numbers_are_caught():
    assert check_numbers("Sales peaked at 60.", TABLE, FACTS) == ["60"]


def test_hallucinated_percentage_is_caught():
    # Case from Muhammad Hasnain's original number-check tests.
    table = {"columns": ["Quarter", "Value"], "rows": [["Q1", 50], ["Q2", 80], ["Q3", 100], ["Q4", 150]]}
    assert check_numbers("The highest value was 150 in Q4.", table, {"series": []}) == []
    assert check_numbers("The projected growth is 500%.", table, {"series": []}) == ["500"]


def test_numbers_in_title_allowed():
    assert check_numbers("Sales in 2025 peaked at 55.", TABLE, FACTS, title="Monthly sales 2025") == []
    assert check_numbers("Sales in 2025 peaked at 55.", TABLE, FACTS) == ["2025"]


def test_small_counting_numbers_allowed():
    assert check_numbers("Over 3 months sales grew.", TABLE, FACTS) == []


def test_offline_mode(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    assert service.explain("t", "bar", TABLE, FACTS) == {"status": "unavailable"}
    answer = service.answer_question("What is the highest?", "t", "bar", TABLE, FACTS, [])
    assert answer["on_topic"] is True and "internet" in answer["answer"]
    with pytest.raises(service.LLMError):
        service.describe_image_generic(_png_bytes())


def _png_bytes() -> bytes:
    import io

    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (40, 30), "white").save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="needs GROQ_API_KEY")
def test_online_explain_and_off_topic():
    result = service.explain("Monthly sales", "bar", TABLE, FACTS)
    assert result["status"] in ("ok", "numbers_unverified")
    off = service.answer_question("What is the weather today?", "Monthly sales", "bar", TABLE, FACTS, [])
    assert off["on_topic"] is False
