import os
from groq import Groq
from config import settings
from .search import search_pipeline

client = Groq(api_key=settings.GROQ_API_KEY)

def generate_answer(query: str, top_k: int = 5, history: list = None):
    if history is None:
        history = []

    # 1. Retrieve context
    search_response = search_pipeline(query, top_k=top_k)
    
    # 2. Format context
    context_text = ""
    for res in search_response.results:
        context_text += f"\n--- GR Number {res.gr_no} ---\n"
        context_text += f"Department: {res.department}\n"
        context_text += f"Content: {res.text}\n"

    # 3. Build Prompt
    system_prompt = (
        "You are the official AI assistant for the Government of Maharashtra. "
        "Your job is to answer questions based on the provided Government Resolutions (GRs). "
        "IMPORTANT RULES:\n"
        "1. If the user says a generic greeting (like 'hello', 'what is this?'), just introduce yourself politely. DO NOT try to answer using the GRs.\n"
        "2. If the user asks a question but the provided GRs are NOT relevant to the question, ignore the GRs and say 'I do not have information on that in the available GRs.'\n"
        "3. Only cite GRs if they actually answer the user's question.\n"
        "4. Always refer to GRs by their actual GR Number (e.g., 'GR 35312'), NOT as 'GR 1' or 'GR 2'."
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

    # 5. Call Groq
    try:
        response = client.chat.completions.create(
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
    for res in search_response.results:
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
