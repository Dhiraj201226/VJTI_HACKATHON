import json
import os
import re

def check_terminology(text: str) -> list:
    """
    Checks the provided text for incorrect terminology (e.g., untranslated Marathi 
    legal terms or informal english) and returns a list of suggestions.
    """
    if not text:
        return []
        
    filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "glossary.json")
    
    if not os.path.exists(filepath):
        return []
        
    with open(filepath, "r", encoding="utf-8") as f:
        glossary_data = json.load(f)
        
    incorrect_terms = glossary_data.get("incorrect_terms", {})
    suggestions = []
    
    text_lower = text.lower()
    
    for wrong_term, correct_term in incorrect_terms.items():
        # Look for whole word matches
        pattern = r'\b' + re.escape(wrong_term) + r'\b'
        if re.search(pattern, text_lower):
            suggestions.append({
                "found": wrong_term,
                "suggestion": correct_term,
                "message": f"Replace informal or untranslated term '{wrong_term}' with standard legal term '{correct_term}'."
            })
            
    return suggestions
