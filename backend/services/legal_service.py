import json
from groq import Groq
from core.config import settings
from qdrant_client import QdrantClient

client = Groq(api_key=settings.GROQ_API_KEY)
qdrant_client = QdrantClient(host="127.0.0.1", port=6333)

def check_constitutional_validity(gr_json: dict) -> dict:
    """
    Evaluates a generated Government Resolution for constitutional validity.
    """
    try:
        subject = gr_json.get("template_fields", {}).get("subject", "")
        body = "\n".join(gr_json.get("template_fields", {}).get("body", []))
        clauses = "\n".join(gr_json.get("template_fields", {}).get("clauses", []))

        gr_text = f"Subject: {subject}\nBody: {body}\nClauses: {clauses}"
        
        # RAG: Retrieve relevant constitutional articles
        retrieved_articles = ""
        try:
            from rag.embedder import get_embedding
            query_embedding = get_embedding(subject + " " + clauses)
            search_result = qdrant_client.query_points(
                collection_name="constitution",
                query=query_embedding,
                limit=3
            )
            if search_result.points:
                retrieved_articles = "\n\n".join([p.payload.get("text", "") for p in search_result.points])
        except Exception as e:
            print(f"Warning: Could not retrieve constitution articles: {e}")

        prompt = f"""
You are an expert Legal Advisor and Constitutional Law AI for the Government of Maharashtra.
Your task is to review the following drafted Government Resolution (GR) and strictly evaluate it against the real Constitution of India.

You must base your analysis entirely on the actual text and legal precedents of the Indian Constitution. 
Here are the most relevant Constitutional Articles retrieved for this case:
{retrieved_articles if retrieved_articles else 'No specific articles retrieved, please rely on your internal knowledge of the Indian Constitution.'}

If there are any violations of fundamental rights (e.g., Article 14, 19, 21), state policies, or constitutional principles, you MUST cite the exact Article number and explain how the text violates it.

Draft GR Text:
{gr_text}

Provide a legal review. Return ONLY a valid JSON object with the following structure:
{{
    "is_valid": boolean,
    "violations": ["List the specific Article numbers (e.g., 'Article 14') and laws violated, or empty if none"],
    "analysis": "Detailed explanation of your legal reasoning citing the exact constitutional text",
    "recommendation": "What should the officer do before issuing this GR?"
}}
"""

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a specialized Legal AI that outputs ONLY valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=settings.LLM_MODEL,
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        import traceback
        return {
            "is_valid": False,
            "violations": ["Internal Server Error Caught in Legal Service"],
            "analysis": traceback.format_exc(),
            "recommendation": "Check backend logs or this traceback."
        }
