import time
import logging
from groq import Groq
from config import settings
from remap_departments import ALLOWED_DEPTS

logger = logging.getLogger(__name__)
client = Groq(api_key=settings.GROQ_API_KEY)

def classify_department_with_llm(gr_text: str, max_retries=3) -> str:
    """
    Summarizes the GR text and classifies it into one of the 33 official departments.
    Uses exponential backoff for rate limiting.
    """
    
    # We truncate the GR text to ~3000 chars to save tokens and speed up inference
    truncated_text = gr_text[:3000]
    
    system_prompt = (
        "You are an AI assistant for the Government of Maharashtra. "
        "Your task is to classify the provided Government Resolution (GR) text into exactly ONE of the following 33 official departments. "
        "You must respond WITH ONLY THE EXACT DEPARTMENT NAME from the list below. Do not add any extra text, punctuation, or explanations.\n\n"
        "Official Departments:\n" + "\n".join([f"- {d}" for d in ALLOWED_DEPTS])
    )
    
    user_prompt = f"Classify this GR text:\n{truncated_text}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    base_wait_time = 2  # Start with 2 seconds backoff
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=messages,
                model=settings.GROQ_MODEL,
                temperature=0.0,  # 0 temperature for strict classification
                max_tokens=50,
            )
            
            raw_answer = response.choices[0].message.content.strip()
            
            # Clean up potential markdown or bullet points from the model
            raw_answer = raw_answer.replace("- ", "").replace("*", "").strip()
            
            # Check if it perfectly matches one of the 33
            for dept in ALLOWED_DEPTS:
                if dept.lower() == raw_answer.lower():
                    return dept
                    
            # If the model hallucinates a different name, return None so we can skip it
            return None
            
        except Exception as e:
            error_msg = str(e).lower()
            if "rate limit" in error_msg or "429" in error_msg:
                wait_time = base_wait_time * (2 ** attempt)
                logger.warning(f"Groq Rate Limit hit. Waiting {wait_time}s before retry {attempt+1}/{max_retries}")
                time.sleep(wait_time)
            else:
                logger.error(f"Groq API Error: {e}")
                return None
                
    return None
