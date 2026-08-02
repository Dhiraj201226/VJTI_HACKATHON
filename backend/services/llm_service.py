import json
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
3. YOU MUST STRICTLY FOLLOW the objective requested by the user, especially any FINANCIAL FIGURES (e.g., 10 crores), NAMES, or LOCATIONS. Do not hallucinate different numbers or ignore user instructions.
4. Do NOT include placeholder tags in your text.
5. Return ONLY a JSON object that perfectly matches the structure below.
6. AUTO-GENERATED REFERENCES: You MUST automatically extract the GR Numbers, Departments, and Dates from the RETRIEVED CONTEXT and construct the 'references' array in `template_fields` formatting them as standard official references. If no references can be extracted from the RETRIEVED CONTEXT because the data is not found, you MUST explicitly output ["No references found in context"] for the references array. Do NOT hallucinate or hardcode fake references.
7. TRANSLATE everything to {language.upper()} before outputting the JSON.

EXPECTED JSON STRUCTURE:
{{
    "references": [
        {{"gr_number": "", "department": "", "date": "", "title": ""}}
    ],
    "conflicts": [
        {{
            "conflict_id": "string",
            "old_policy": "string",
            "latest_policy": "string",
            "reason": "string",
            "recommendation": "string"
        }}
    ],
    "template_fields": {{
        "department": "Name of the Department",
        "gr_number": "Generated or retrieved GR number",
        "date": "Today's date or specific date",
        "subject": "The subject of the GR",
        "references": ["String array of formatted references"],
        "body": ["String array of paragraphs for the preamble/body"],
        "clauses": ["String array of specific clauses or resolutions"],
        "financial_implications": "Details about budget, if any",
        "implementation": "Implementation instructions",
        "signature": "Name of signing authority",
        "designation": "Designation of signing authority",
        "footer": "Official footer text",
        "copy_to": ["String array of distribution recipients (prat)"]
    }}
}}
"""

def generate_gr_json(objective: str, retrieved_chunks: dict, officer_decisions: list = None, language: str = "English") -> LLMDraftResponse:
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
    
    # We use Groq's JSON mode if supported, or just prompt engineering
    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a specialized AI that outputs ONLY valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model=settings.LLM_MODEL,
        response_format={"type": "json_object"},
        temperature=0.2
    )
    
    content = response.choices[0].message.content
    parsed_json = json.loads(content)
    
    # Validate and return using Pydantic
    return LLMDraftResponse(**parsed_json)

def answer_faq(question: str) -> str:
    prompt = f"""
You are the AI Assistant for MAHA-GR ALIGN, a portal for drafting Government Resolutions (GRs) for the Government of Maharashtra.
Your job is to answer user questions about how the platform works.
Keep your answers concise, helpful, and professional.

System Context:
- MAHA-GR ALIGN uses RAG (Retrieval-Augmented Generation) to search past GRs.
- It detects semantic conflicts and duplicate funding.
- It verifies references against a Qdrant vector database.
- It suggests official bilingual terminology.
- It generates legally compliant PDFs and DOCXs.

User Question: {question}
"""
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant for MAHA-GR ALIGN."},
            {"role": "user", "content": prompt}
        ],
        model=settings.LLM_MODEL,
        temperature=0.3
    )
    return response.choices[0].message.content

