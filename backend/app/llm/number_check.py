import re

def extract_numbers(text: str) -> set:
    """
    Extracts all numbers (integers and decimals) from a given text string.
    """
    if not text:
        return set()
    found = re.findall(r'-?\b\d+(?:\.\d+)?\b', str(text))
    return {float(n) if '.' in n else int(n) for n in found}

def verify_numbers_in_text(response_text: str, source_texts: list) -> tuple[bool, list]:
    """
    Verifies that every number mentioned in the LLM response text 
    exists somewhere in the provided source texts (table data, facts, title).
    Returns (is_valid, list_of_unverified_numbers).
    """
    response_numbers = extract_numbers(response_text)
    
    # Collect all valid numbers from the source data
    allowed_numbers = set()
    for text in source_texts:
        allowed_numbers.update(extract_numbers(str(text)))
    
    # Find any numbers in the response that are NOT in the allowed source numbers
    unverified = [num for num in response_numbers if num not in allowed_numbers]
    
    # If there are unverified numbers, validation fails
    is_valid = len(unverified) == 0
    return is_valid, unverified