import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'backend'))

from groq import Groq
from core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)

response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are a professional translator. Translate the following text to Marathi. ONLY output the Marathi text in Devanagari script, nothing else."},
        {"role": "user", "content": "Cancellation of 10th and 12th standard board exams across the state"}
    ],
    model=settings.LLM_MODEL,
    temperature=0.1
)

print(response.choices[0].message.content)
