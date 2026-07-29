import requests
import json
import os
import fitz  # PyMuPDF
import shutil

url_init = "http://127.0.0.1:8000/api/draft/initiate"
url_gen = "http://127.0.0.1:8000/api/draft/generate"

objective = "Increase the financial grant fund of VJTI to 10 crores for infrastructure development."

print("=== INITIATE DRAFT (Check for conflicts) ===")
payload_init = {"objective": objective}
response_init = requests.post(url_init, json=payload_init)
data_init = response_init.json()
print("Conflicts Detected:")
print(json.dumps(data_init.get("conflicts", []), indent=2))

print("\n=== GENERATE DRAFT ===")
payload_gen = {
    "objective": objective,
    "officer_decisions": []
}
response_gen = requests.post(url_gen, json=payload_gen)
data_gen = response_gen.json()

analysis = data_gen.get("json_data", {}).get("phase2_analysis", {})
print("References Parsed:")
print(json.dumps(analysis.get("references", {}), indent=2))

print("Terminology Suggestions:")
print(json.dumps(analysis.get("terminology", []), indent=2))

pdf_url = data_gen.get("pdf_url", "")
pdf_filename = pdf_url.split("/")[-1]
pdf_path = os.path.join("data", "output", pdf_filename)
jpg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "artifacts", "vjti_gr.jpg")
artifacts_dir = r"C:\Users\dhira\.gemini\antigravity\brain\2e15a404-0657-4a9f-be5c-776527b31864"
jpg_artifact = os.path.join(artifacts_dir, "vjti_gr.jpg")

print(f"\nConverting PDF to JPG: {pdf_path}")
if os.path.exists(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)  # first page
    pix = page.get_pixmap(dpi=150)
    pix.save(jpg_artifact)
    print(f"Saved JPG to: {jpg_artifact}")
else:
    print(f"PDF not found at {pdf_path}")

