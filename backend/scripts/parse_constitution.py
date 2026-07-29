import fitz
import re
import json

pdf_path = r"C:\Users\dhira\OneDrive\Desktop\CEP SEM4\1st attempt\ARA-1-Financial-Agent\VJTI_HACKATHON\mahGRs\88cca69e868e50b217f855be2fb8bdba.pdf"
out_path = r"C:\Users\dhira\OneDrive\Desktop\CEP SEM4\1st attempt\ARA-1-Financial-Agent\VJTI_HACKATHON\backend\data\constitution.json"

print(f"Opening {pdf_path}...")
doc = fitz.open(pdf_path)

raw_text = ""
for page in doc[35:]:
    raw_text += page.get_text() + "\n"

items = []
current_type = None
current_number = None
current_title = None
current_text = []

lines = raw_text.split('\n')
article_pattern = re.compile(r'^(\d+[A-Z]*)\.\s+(.*?)[.—](.*)')
schedule_pattern = re.compile(r'^([A-Z]+ SCHEDULE)\b')

def save_current():
    if current_type:
        items.append({
            "type": current_type,
            "number": current_number,
            "title": current_title,
            "body": " ".join(current_text).strip()
        })

for line in lines:
    line = line.strip()
    if not line:
        continue
    
    art_match = article_pattern.match(line)
    if art_match:
        save_current()
        current_type = "Article"
        current_number = art_match.group(1)
        current_title = art_match.group(2).strip()
        current_text = [art_match.group(3).strip()]
        continue
    
    sch_match = schedule_pattern.match(line)
    if sch_match:
        save_current()
        current_type = "Schedule"
        current_number = sch_match.group(1).replace(" SCHEDULE", "")
        current_title = sch_match.group(1)
        current_text = []
        continue
        
    if re.match(r'^\d+$', line) or line.startswith("THE CONSTITUTION OF INDIA"):
        continue
        
    if current_type:
        current_text.append(line)

save_current()

print(f"Parsed {len(items)} structured items.")

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(items, f, indent=4, ensure_ascii=False)

print(f"Saved structured JSON to {out_path}!")
