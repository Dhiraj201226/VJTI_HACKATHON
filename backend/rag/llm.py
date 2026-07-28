import os
from groq import Groq
from config import settings
from .search import search_pipeline

client = Groq(api_key=settings.GROQ_API_KEY)

def generate_answer(query: str, top_k: int = 5):
    # 1. Retrieve context
    search_response = search_pipeline(query, top_k=top_k)
    
    # 2. Format context
    context_text = ""
    for i, res in enumerate(search_response.results):
        context_text += f"\n--- GR {i+1} ---\n"
        context_text += f"GR No: {res.gr_no}\n"
        context_text += f"Department: {res.department}\n"
        context_text += f"Content: {res.text}\n"

    # 3. Build Prompt
    system_prompt = (
        "You are an expert AI assistant for the Government of Maharashtra. "
        "Answer the user's question based STRICTLY on the provided Government Resolutions (GRs) below. "
        "If the answer is not contained in the GRs, say 'I do not have information on that in the available GRs.' "
        "Always cite the relevant GR Number and Department when providing your answer. "
        "Keep your answers professional and well-structured."
    )
    
    user_prompt = f"Context:\n{context_text}\n\nQuestion: {query}"

    # 4. Call Groq
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=settings.GROQ_MODEL,
            temperature=0.3,
            max_tokens=1024,
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = f"Error generating response: {str(e)}"
    
    return {
        "answer": answer,
        "sources": search_response.results
    }
