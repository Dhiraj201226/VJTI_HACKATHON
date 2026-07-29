import requests
import json

url = "http://127.0.0.1:8000/api/draft/generate"

payload = {
    "objective": "Draft a Government Resolution to digitize all old shasan nirnay and paripatra for the education department. Reference GR 2018-XY in the preamble.",
    "officer_decisions": []
}

print(f"Sending request to {url}...")
try:
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    
    analysis = data.get("json_data", {}).get("phase2_analysis", {})
    
    print("\n" + "="*50)
    print("PHASE 2 ANALYSIS RESULTS")
    print("="*50)
    print("\n1. TEMPLATE WARNINGS:")
    for warning in analysis.get("template_warnings", []):
        print(f"  - {warning}")
        
    print("\n2. BILINGUAL TERMINOLOGY SUGGESTIONS:")
    for term in analysis.get("terminology", []):
        print(f"  - Found: '{term['found']}' -> Suggestion: '{term['suggestion']}'")
        
    print("\n3. REFERENCES PARSER:")
    refs = analysis.get("references", {})
    print(f"  - Extracted: {refs.get('extracted_references', [])}")
    print(f"  - Verified in DB: {refs.get('verified_references', [])}")
    print(f"  - Missing in DB: {refs.get('missing_references', [])}")
    
    print("="*50)
    
except Exception as e:
    print(f"Error testing API: {e}")
