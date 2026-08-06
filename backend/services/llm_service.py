import json
from datetime import date
from groq import Groq
from core.config import settings
from models.schemas import LLMDraftResponse

client = Groq(api_key=settings.GROQ_API_KEY)

def build_prompt(objective: str, context: str, decisions: str, language: str) -> str:
    return f"""
You are an expert Government Resolution (GR) drafting AI for the Government of Maharashtra.

CRITICAL REQUIREMENT: YOU MUST WRITE ALL CONTENT EXCLUSIVELY IN {language.upper()}! 
If the language is Marathi, every single string inside `template_fields` (subject, body, clauses, references, financial_implications, implementation, signature, designation, footer) MUST be written in pure Marathi (Devanagari script). Do NOT output English text for these fields. 

OBJECTIVE:
{objective}

RETRIEVED CONTEXT (Past GRs and policies):
{context}

OFFICER CONFLICT DECISIONS:
{decisions}

DRAFTING RULES:
1. Maintain formal government writing style in {language.upper()}.
2. The document engine will place your outputs into an official template.
3. YOU MUST STRICTLY FOLLOW the objective requested by the user and the OFFICER CONFLICT DECISIONS. If the officer provides a custom justification/decision (like a different financial amount), YOU MUST OVERRIDE the old policy and use the officer's custom decision. Do not hallucinate numbers.
4. Do NOT include placeholder tags in your text.
5. Return ONLY a JSON object that perfectly matches the structure below. 
   CRITICAL: DO NOT copy the placeholder descriptions. You MUST REPLACE all placeholder text with the ACTUAL generated content based on the user's objective!
6. AUTO-GENERATED REFERENCES: You MUST automatically extract the GR Numbers, Departments, and Dates from the RETRIEVED CONTEXT and construct the 'references' array in `template_fields` formatting them as standard official references. If no references can be extracted from the RETRIEVED CONTEXT because the data is not found, you MUST explicitly output ["No references found in context"] for the references array. Do NOT hallucinate or hardcode fake references.
7. TRANSLATE everything to {language.upper()} before outputting the JSON.

EXAMPLE OF CORRECT OUTPUT (Content must be your actual generated text, this is just an example of the structure filled with real data):
{{
    "references": [
        {{"gr_number": "GR-2023-112", "department": "Finance Department", "date": "10 January 2023", "title": "Budget Allocation for Rural Roads"}}
    ],
    "conflicts": [],
    "template_fields": {{
        "department": "सार्वजनिक बांधकाम विभाग",
        "gr_number": "GR-2026-456",
        "date": "Must be exactly '{date.today().strftime('%d %B %Y')}'",
        "subject": "ग्रामीण भागातील रस्ते विकासासाठी निधी मंजूर करण्याबाबत.",
        "references": ["१. शासन निर्णय क्र. GR-2023-112, वित्त विभाग, दिनांक १० जानेवारी २०२३"],
        "body": ["राज्यातील ग्रामीण भागातील रस्त्यांची दुरवस्था लक्षात घेता, त्यांच्या दुरुस्तीसाठी विशेष निधीची आवश्यकता होती.", "त्यानुसार शासनाने खालीलप्रमाणे निर्णय घेतला आहे."],
        "clauses": ["१. ग्रामीण रस्त्यांच्या दुरुस्तीसाठी रुपये ५० कोटी निधी मंजूर करण्यात येत आहे.", "२. सदर कामे ३ महिन्यांत पूर्ण करावीत."],
        "financial_implications": "रुपये ५० कोटी",
        "implementation": "जिल्हा परिषदेच्या मुख्य कार्यकारी अधिकाऱ्यांनी या निर्णयाची अंमलबजावणी करावी.",
        "signature": "अ. ब. क.",
        "designation": "सचिव, महाराष्ट्र शासन",
        "footer": "हे परिपत्रक महाराष्ट्र शासनाच्या अधिकृत वेबसाईटवर उपलब्ध आहे.",
        "copy_to": ["१. मुख्य सचिव, महाराष्ट्र शासन", "२. सर्व विभागीय आयुक्त"]
    }}
}}

EXPECTED JSON STRUCTURE (Replace placeholders with actual generated text):
{{
    "references": [
        {{"gr_number": "...", "department": "...", "date": "...", "title": "..."}}
    ],
    "conflicts": [
        {{
            "conflict_id": "...",
            "old_policy": "...",
            "latest_policy": "...",
            "reason": "...",
            "recommendation": "..."
        }}
    ],
    "template_fields": {{
        "department": "[Generate the actual department name here]",
        "gr_number": "[Generate the GR number here]",
        "date": "Must be exactly '{date.today().strftime('%d %B %Y')}'",
        "subject": "[Write the actual subject of the GR here]",
        "references": ["[Write the actual formatted reference 1 here]", "[Write formatted reference 2 here]"],
        "body": ["[Write actual paragraph 1 of the preamble here]", "[Write actual paragraph 2 here]"],
        "clauses": ["[Write actual clause 1 here]", "[Write actual clause 2 here]"],
        "financial_implications": "[Write the actual budget details here, or 'Nil']",
        "implementation": "[Write the actual implementation instructions here]",
        "signature": "[Write the actual name of signing authority here]",
        "designation": "[Write the actual designation of signing authority here]",
        "footer": "[Write the actual official footer text here]",
        "copy_to": ["[Write actual recipient 1 here]", "[Write actual recipient 2 here]"]
    }}
}}
"""

def generate_gr_json(objective: str, retrieved_chunks: dict, officer_decisions: list = None, language: str = "English", provider: str = "groq", model: str = None) -> LLMDraftResponse:
    if officer_decisions is None:
        officer_decisions = []
    
    # Pre-process inputs
    docs = retrieved_chunks.get('documents', [[]])[0]
    context_str = "\n".join([f"- {doc}" for doc in docs])
    
    # Format decisions
    decisions_str = "\n".join([f"Conflict: {d.conflict_id}, Selected: {d.selected_policy}, Justification: {d.justification}" for d in officer_decisions])
    if not decisions_str:
        decisions_str = "None"
        
    prompt = build_prompt(objective, context_str, decisions_str, language)
    
    messages = [
        {
            "role": "system",
            "content": "You are a specialized AI that outputs ONLY valid JSON."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    if provider == "ollama":
        import requests
        try:
            target_model = model if model else "qwen2:1.5b"
            res = requests.post("http://localhost:11434/api/chat", json={
                "model": target_model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.2, "num_ctx": 4096, "num_predict": 2000}
            }, timeout=3000)
            res.raise_for_status()
            content = res.json()["message"]["content"]
        except Exception as e:
            print(f"Ollama error: {e}")
            raise RuntimeError(f"Failed to connect to local Ollama instance or request timed out: {e}")
    else:
        # We use Groq's JSON mode if supported, or just prompt engineering
        target_model = model if model else settings.LLM_MODEL
        response = client.chat.completions.create(
            messages=messages,
            model=target_model,
            response_format={"type": "json_object"},
            temperature=0.2
        )
        content = response.choices[0].message.content

    if not content or not content.strip():
        raise ValueError(f"The selected model ({model or 'default'}) returned an empty response. Please try selecting a different model (like llama3) or use Groq.")

    # Robust JSON extraction
    import re
    content = content.strip()
    # Try to find JSON block if it's wrapped in markdown
    match = re.search(r'```(?:json)?(.*?)```', content, re.DOTALL)
    if match:
        content = match.group(1).strip()
    else:
        # Fallback: try to find the first { and last }
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            content = content[start:end+1]

    try:
        parsed_json = json.loads(content)
        
        # Sanitize for small local models that don't perfectly follow the schema
        if "references" in parsed_json and isinstance(parsed_json["references"], list):
            for ref in parsed_json["references"]:
                if isinstance(ref, dict) and "title" not in ref:
                    ref["title"] = ref.get("gr_number", "Reference Document")
                    
        if "template_fields" in parsed_json and isinstance(parsed_json["template_fields"], dict):
            tf = parsed_json["template_fields"]
            if "references" in tf and isinstance(tf["references"], list):
                tf["references"] = [r.get("gr_number", str(r)) if isinstance(r, dict) else str(r) for r in tf["references"]]
            if "body" in tf and isinstance(tf["body"], str):
                tf["body"] = [tf["body"]]
            if "clauses" in tf and isinstance(tf["clauses"], str):
                tf["clauses"] = [tf["clauses"]]
                
        return LLMDraftResponse(**parsed_json)
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error. Raw content: {content}")
        raise ValueError(f"The LLM model ({model or 'default'}) did not return valid JSON. It returned: {content[:100]}...")

def answer_faq(question: str, provider: str = "groq", model: str = None) -> str:
    messages = [
        {"role": "system", "content": "You are a highly strict AI assistant for the Maharashtra Government Resolution database. \n"
                                      "CRITICAL RULES:\n"
                                      "1. If the context or your knowledge does not contain the specific GR information asked, you MUST explicitly say: 'I do not have information on this GR.'\n"
                                      "2. DO NOT hallucinate or guess GR numbers or policies.\n"
                                      "3. Return responses in plain, good text format. DO NOT return markdown dropdowns, complex UI elements, or random code blocks.\n"
                                      "4. Respond in Marathi (मराठी) if the user's question is in Marathi, otherwise use English."},
        {"role": "user", "content": question}
    ]
    
    if provider == "ollama":
        import requests
        target_model = model if model else "qwen2:1.5b"
        res = requests.post("http://localhost:11434/api/chat", json={
            "model": target_model,
            "messages": messages,
            "stream": False
        })
        res.raise_for_status()
        return res.json()["message"]["content"]
    else:
        target_model = model if model else settings.LLM_MODEL
        response = client.chat.completions.create(
            messages=messages,
            model=target_model,
            temperature=0.3
        )
        return response.choices[0].message.content

def generate_summary(text: str, provider: str = "groq", model: str = None) -> str:
    messages = [
        {"role": "system", "content": "You are an expert summarizer. Summarize the following text concisely. Highlight the key points."},
        {"role": "user", "content": text}
    ]
    if provider == "ollama":
        import requests
        target_model = model if model else "qwen2:1.5b"
        res = requests.post("http://localhost:11434/api/chat", json={
            "model": target_model,
            "messages": messages,
            "stream": False
        })
        return res.json()["message"]["content"]
    else:
        target_model = model if model else settings.LLM_MODEL
        response = client.chat.completions.create(messages=messages, model=target_model, temperature=0.3)
        return response.choices[0].message.content

def translate_text(text: str, target_language: str, provider: str = "groq", model: str = None) -> str:
    messages = [
        {"role": "system", "content": f"You are a professional translator. Translate the following text into {target_language}. Preserve formatting and tone. Output ONLY the translated text."},
        {"role": "user", "content": text}
    ]
    if provider == "ollama":
        import requests
        target_model = model if model else "qwen2:1.5b"
        res = requests.post("http://localhost:11434/api/chat", json={
            "model": target_model,
            "messages": messages,
            "stream": False
        })
        return res.json()["message"]["content"]
    else:
        target_model = model if model else settings.LLM_MODEL
        response = client.chat.completions.create(messages=messages, model=target_model, temperature=0.3)
        return response.choices[0].message.content
