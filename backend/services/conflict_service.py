import uuid
from typing import List, Dict, Any
from models.schemas import Conflict
from config import settings
from groq import Groq
import json

client = Groq(api_key=settings.GROQ_API_KEY)

def detect_conflicts(retrieved_chunks: Dict[str, Any]) -> List[Conflict]:
    """
    Analyzes retrieved chunks for actual semantic conflicts using LLM reasoning.
    Finds overlapping or contradictory policies from the Qdrant DB.
    """
    docs = retrieved_chunks.get('documents', [[]])[0]
    
    if not docs:
        return []
        
    context_str = "\n---\n".join(docs)
    
    prompt = f"""
    You are an AI assisting the Maharashtra Government.
    Review the following retrieved policies/GRs for any contradictions, 
    overlaps, or conflicts between them regarding a unified objective.
    
    Context:
    {context_str}
    
    If there are conflicts (e.g. one policy says X, another says Y), return a JSON list of them.
    If no conflicts, return [].
    
    Output exactly in this JSON format:
    [
      {{
        "conflict_id": "unique string id",
        "old_policy": "Description of policy A",
        "latest_policy": "Description of policy B",
        "reason": "Why they conflict",
        "recommendation": "How the officer should resolve this"
      }}
    ]
    """
    
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You output JSON only."},
                {"role": "user", "content": prompt}
            ],
            model=settings.GROQ_MODEL,
            response_format={"type": "json_object"},
            temperature=0.1
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        conflicts = data if isinstance(data, list) else data.get("conflicts", [])
        
        return [Conflict(**c) for c in conflicts]
    except Exception as e:
        print(f"Conflict detection error: {e}")
        return []
