import fitz
import os

pdf_path = r"C:\Users\dhira\OneDrive\Desktop\CEP SEM4\1st attempt\ARA-1-Financial-Agent\VJTI_HACKATHON\mahGRs\88cca69e868e50b217f855be2fb8bdba.pdf"
out_path = r"C:\Users\dhira\OneDrive\Desktop\CEP SEM4\1st attempt\ARA-1-Financial-Agent\VJTI_HACKATHON\backend\data\constitution.txt"

print(f"Opening {pdf_path}...")
doc = fitz.open(pdf_path)
text = ""

for page in doc:
    text += page.get_text()

with open(out_path, "w", encoding="utf-8") as f:
    f.write(text)

print(f"Saved {len(text)} characters to {out_path}!")
