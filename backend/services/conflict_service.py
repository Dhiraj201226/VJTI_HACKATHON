import uuid
from typing import List, Dict, Any
from models.schemas import Conflict
from core.config import settings
from groq import Groq
import json

client = Groq(api_key=settings.GROQ_API_KEY)

def detect_conflicts(retrieved_chunks: Dict[str, Any], provider: str = "groq", model: str = None) -> List[Conflict]:
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
    {{
      "conflicts": [
        {{
          "conflict_id": "unique string id",
          "old_policy": "Description of policy A",
          "latest_policy": "Description of policy B",
          "reason": "Why they conflict",
          "recommendation": "How the officer should resolve this"
        }}
      ]
    }}
    """
    
    messages = [
        {"role": "system", "content": "You output JSON only."},
        {"role": "user", "content": prompt}
    ]
    
    try:
        if provider == "ollama":
            import requests
            target_model = model if model else "qwen2:1.5b"
            res = requests.post("http://localhost:11434/api/chat", json={
                "model": target_model,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.1, "num_ctx": 4096}
            }, timeout=3000)
            res.raise_for_status()
            content = res.json()["message"]["content"]
        else:
            target_model = model if model else settings.LLM_MODEL
            response = client.chat.completions.create(
                messages=messages,
                model=target_model,
                response_format={"type": "json_object"},
                temperature=0.1
            )
            content = response.choices[0].message.content
            
        if not content or not content.strip():
            print(f"Conflict detection error: The selected model ({model or 'default'}) returned an empty response.")
            return []

        # Robust JSON extraction
        import re
        content = content.strip()
        match = re.search(r'```(?:json)?(.*?)```', content, re.DOTALL)
        if match:
            content = match.group(1).strip()
        else:
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1:
                content = content[start:end+1]
            
        try:
            data = json.loads(content)
            conflicts = data if isinstance(data, list) else data.get("conflicts", [])
            
            # Fallback score if embedding fails
            scores_list = retrieved_chunks.get("scores", [[]])[0]
            max_score = max(scores_list) if scores_list else 0.0
            fallback_score = int(max_score * 100)
            
            conflicts_obj = [Conflict(**c) for c in conflicts]
            
            try:
                from rag.embedder import get_embedding
                for c in conflicts_obj:
                    emb1 = get_embedding(c.old_policy)
                    emb2 = get_embedding(c.latest_policy)
                    
                    # Compute pure cosine similarity
                    dot = sum(a * b for a, b in zip(emb1, emb2))
                    norm1 = sum(a * a for a in emb1) ** 0.5
                    norm2 = sum(b * b for b in emb2) ** 0.5
                    
                    if norm1 > 0 and norm2 > 0:
                        sim = dot / (norm1 * norm2)
                        c.similarity_score = int(abs(sim) * 100)
                    else:
                        c.similarity_score = fallback_score
            except Exception as embed_err:
                print(f"Embedding failed for conflict score: {embed_err}")
                for c in conflicts_obj:
                    c.similarity_score = fallback_score
                    
            return conflicts_obj
        except Exception as e:
            print(f"Conflict detection error: {e}. Raw content: {content[:100]}")
            return []
            
    except Exception as e:
        print(f"Conflict detection error: {e}")
        return []
