import os
import requests
from groq import Groq
from config import settings
from .search import search_pipeline

# Change this to "ollama" if you want to use the local model
PROVIDER = "ollama"
groq_client = Groq(api_key=settings.GROQ_API_KEY)

def generate_answer(query: str, top_k: int = 5, history: list = None):
    if history is None:
        history = []

    # 1. Retrieve context
    search_response = search_pipeline(query, top_k=top_k)
    
    # Print scores for debugging
    print(f"--- QUERY: {query} ---")
    for res in search_response.results:
        print(f"GR {res.gr_no} Score: {res.score}")
    print("------------------------")

    # Filter by confidence score threshold (e.g., lower to 0.30 to be safe, adjust as needed)
    filtered_results = [res for res in search_response.results if res.score >= 0.30]

    if not filtered_results:
        return {
            "answer": "Not found. The available GRs do not closely match your query.",
            "sources": []
        }
    
    # 2. Format context
    context_text = ""
    for res in filtered_results:
        context_text += f"\n--- GR Number {res.gr_no} ---\n"
        context_text += f"Department: {res.department}\n"
        context_text += f"Content: {res.text}\n"

    # 3. Build Prompt
    system_prompt = (
        "You are a helpful AI assistant for the Government of Maharashtra.\n"
        "You must answer the user's question using ONLY the context provided below.\n"
        "If the user asks you to summarize or explain a GR, you MUST provide a clear and simple summary.\n"
        "Always respond in the same language as the user (English or Marathi). "
        "Do not refuse to answer. Just provide the summary."
    )
    
    user_prompt = f"Context:\n{context_text}\n\nQuestion: {query}"

    # 4. Construct Messages with History
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add last 4 messages from history to keep context window reasonable
    for msg in history[-4:]:
        # Skip the initial greeting message to save tokens
        if msg.role == "assistant" and "Namaskar" in msg.content:
            continue
        messages.append({"role": msg.role, "content": msg.content})
        
    messages.append({"role": "user", "content": user_prompt})

    # 5. Call LLM
    try:
        if PROVIDER == "ollama":
            res = requests.post("http://localhost:11434/api/chat", json={
                "model": "gemma4:31b-cloud",
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.3, "num_predict": 1024}
            }, timeout=3000)
            res.raise_for_status()
            answer = res.json()["message"]["content"]
        else:
            response = groq_client.chat.completions.create(
                messages=messages,
                model=settings.GROQ_MODEL,
                temperature=0.3,
                max_tokens=1024,
            )
            answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Error generating response: {str(e)}"
    
    # Group sources by GR number to avoid duplicates in the UI
    unique_sources = {}
    for res in filtered_results:
        if res.gr_no not in unique_sources:
            unique_sources[res.gr_no] = {
                "gr_no": res.gr_no,
                "department": res.department,
                "score": res.score,
                "source_file": res.source_file,
                "text": res.text
            }
        else:
            unique_sources[res.gr_no]["text"] += f"\n\n[...]\n\n{res.text}"

    return {
        "answer": answer,
        "sources": list(unique_sources.values())
    }
