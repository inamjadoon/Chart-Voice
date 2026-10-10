import pytest
from app.llm.number_check import verify_numbers_in_text, extract_numbers

def test_extract_numbers():
    text = "In 2023, revenue grew by 15.5% to 100 million."
    numbers = extract_numbers(text)
    assert numbers == {2023, 15.5, 100}

def test_verify_numbers_valid():
    response = "The highest value was 150 in Q4."
    source = ["Q1: 50", "Q2: 80", "Q3: 100", "Q4: 150"]
    is_valid, unverified = verify_numbers_in_text(response, source)
    assert is_valid is True
    assert len(unverified) == 0

def test_verify_numbers_invalid_hallucination():
    response = "The projected growth is 500%."
    source = ["Q1: 50", "Q2: 80", "Q3: 100", "Q4: 150"]
    is_valid, unverified = verify_numbers_in_text(response, source)
    assert is_valid is False
    assert 500 in unverified