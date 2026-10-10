import os
from .groq_client import get_groq_client
from .prompts import SUMMARY_EXPLANATION_PROMPT, ASK_QUESTION_PROMPT
from .number_check import verify_numbers_in_text
from .image_utils import image_bytes_to_base64

# Updated active Groq model
DEFAULT_MODEL = "openai/gpt-oss-20b"

def generate_chart_summary(title: str, chart_type: str, table_data: str, facts_data: str) -> dict:
    """
    Generates a plain-language summary and explanation for the chart, 
    ensuring all numbers are verified against source data.
    """
    client = get_groq_client()
    
    prompt = SUMMARY_EXPLANATION_PROMPT.format(
        title=title,
        chart_type=chart_type,
        table_data=table_data,
        facts_data=facts_data
    )
    
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )
    
    answer_text = response.choices[0].message.content
    
    # Verify numbers to prevent hallucination
    source_texts = [title, chart_type, str(table_data), str(facts_data)]
    is_valid, unverified = verify_numbers_in_text(answer_text, source_texts)
    
    return {
        "response": answer_text,
        "verified": is_valid,
        "unverified_numbers": unverified
    }

def answer_chart_question(title: str, chart_type: str, table_data: str, facts_data: str, question: str) -> dict:
    """
    Answers a specific user question about the chart using extracted data and facts.
    """
    client = get_groq_client()
    
    prompt = ASK_QUESTION_PROMPT.format(
        title=title,
        chart_type=chart_type,
        table_data=table_data,
        facts_data=facts_data,
        question=question
    )
    
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=400
    )
    
    answer_text = response.choices[0].message.content
    
    source_texts = [title, chart_type, str(table_data), str(facts_data)]
    is_valid, unverified = verify_numbers_in_text(answer_text, source_texts)
    
    return {
        "response": answer_text,
        "verified": is_valid,
        "unverified_numbers": unverified
    }