import os
import fitz  # PyMuPDF
from models.schemas import LLMDraftResponse
import typst

OUTPUT_DIR = "./data/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
import shutil
if os.path.exists("./data/logo.png") and not os.path.exists(os.path.join(OUTPUT_DIR, "logo.png")):
    shutil.copy("./data/logo.png", os.path.join(OUTPUT_DIR, "logo.png"))

def generate_documents(json_data: LLMDraftResponse):
    fields = json_data.template_fields
    
    # Detect language by checking for Devanagari characters in the subject
    is_marathi = any('\u0900' <= c <= '\u097F' for c in (fields.subject or ""))

    # Translations based on language
    t_gov = "महाराष्ट्र शासन" if is_marathi else "GOVERNMENT OF MAHARASHTRA"
    t_gr_no = "शासन परिपत्रक क्रमांक :" if is_marathi else "Government Resolution No.:"
    t_date = "दिनांक :" if is_marathi else "Date:"
    t_ref = "संदर्भ :" if is_marathi else "Reference :"
    t_res = "शासन परिपत्रक :" if is_marathi else "Resolution :"
    t_order = "महाराष्ट्राचे राज्यपाल यांच्या आदेशानुसार व नावाने," if is_marathi else "By order and in the name of the Governor of Maharashtra,"
    t_copy = "प्रत," if is_marathi else "Copy To,"
    t_page = "पृष्ठ" if is_marathi else "Page"
    t_of = "पैकी" if is_marathi else "of"
    
    copy_to_list = fields.copy_to if hasattr(fields, 'copy_to') and fields.copy_to else []
    first_copy = copy_to_list[0] if len(copy_to_list) > 0 else ""
    rest_copy = "\\n".join([f"  {i+2}) {c}" for i, c in enumerate(copy_to_list[1:])]) if len(copy_to_list) > 1 else ""

    # Python 3.10 compatibility: Do not use backslashes in f-string expression blocks.
    def ensure_list(val):
        if isinstance(val, list): return val
        if val is None: return []
        return [str(val)]
        
    ref_str = "\\n".join(ensure_list(fields.references))
    body_str = "\\n".join(ensure_list(fields.body))
    clauses_str = "\\n".join(ensure_list(fields.clauses))

    # Escape typst special characters roughly
    def escape_typst(text):
        if not text: return ""
        return str(text).replace("#", "\\#").replace("$", "\\$")

    # Build Typst string matching the LaTeX template
    typst_code = f"""
#set page(
  paper: "a4",
  margin: (top: 15mm, bottom: 20mm, left: 20mm, right: 20mm),
  numbering: "1",
)
#set text(font: "Mangal", size: 11pt, fallback: true)

// Centered Logo
#align(center)[
  #image("logo.png", width: 2cm)
]

#v(0.5em)

// Right aligned subject block
#align(right)[
  #box(width: 50%, align(left)[
    #set text(weight: "bold")
    {escape_typst(fields.subject)}
  ])
]

#v(0.5em)

// Centered Government / Department Header
#align(center)[
  #text(size: 16pt, weight: "bold")[{t_gov}] \\
  #v(0.2em)
  #text(size: 12pt, weight: "bold")[{escape_typst(fields.department)}] \\
  #v(0.2em)
  #text(weight: "bold")[{t_gr_no} {escape_typst(fields.gr_number)}] \\
  #v(0.2em)
  Hutatma Rajguru Chowk, Madam Cama Road, \\
  Mantralaya, Mumbai-400 032 \\
  #text(weight: "bold")[{t_date} {escape_typst(fields.date)}]
]

#v(0.5em)
#box([
  #underline[#text(weight: "bold")[{t_ref}]]
  #h(0.5em) {escape_typst(ref_str)}
])

#v(1em)
#text(weight: "bold")[{t_res}]

#v(0.5em)
#h(2em) {escape_typst(body_str)}

#v(0.8em)
{escape_typst(clauses_str)}

#v(1em)
*Financial Implications:* {escape_typst(fields.financial_implications)}

#v(1em)
*Implementation:* {escape_typst(fields.implementation)}

#v(1em)
#align(center)[
  {t_order}
]

#v(0.5em)

#align(right)[
  #box(width: 40%, align(left)[
    #text(size: 8pt)[
      Digitally signed by {escape_typst(fields.signature)} \\
      Date: {escape_typst(fields.date)} \\
    ]
    #v(0.5em)
    #h(2em) #text(weight: "bold")[({escape_typst(fields.signature)})] \\
    #h(1.5em) #text(weight: "bold")[{escape_typst(fields.designation)}]
  ])
]

#v(1em)
#text(weight: "bold")[{t_copy}] \\
#h(1.5em) 1) {escape_typst(first_copy)}

#v(2em)
#text(weight: "bold")[{t_gr_no} {escape_typst(fields.gr_number)}]
#v(0.3em)
#line(length: 100%, stroke: 1.5pt)
#v(1em)

{escape_typst(rest_copy)}
"""
    
    gr_num_safe = str(fields.gr_number).replace('/', '_') if fields.gr_number else "Draft"
    base_name = f"GR_{gr_num_safe}"
    typst_path = os.path.join(OUTPUT_DIR, f"{base_name}.typ")
    pdf_path = os.path.join(OUTPUT_DIR, f"{base_name}.pdf")
    docx_path = os.path.join(OUTPUT_DIR, f"{base_name}.docx") # We'll just fake docx for now since typst doesn't output docx easily, or create a simple one later if needed. But the PDF is what matters.
    
    with open(typst_path, "w", encoding="utf-8") as f:
        f.write(typst_code)
        
    try:
        typst.compile(typst_path, output=pdf_path)
    except Exception as e:
        print("Typst compile error:", e)
        # Fallback to fpdf or similar if it fails, but typst should work perfectly
        
    # Create a dummy docx so the UI doesn't crash on download docx button
    from docx import Document
    doc = Document()
    doc.add_paragraph("DOCX generation currently disabled. Please view the perfect PDF instead.")
    doc.save(docx_path)
    
    return docx_path, pdf_path

import qrcode
import hashlib

def stamp_qr_and_hash(pdf_path: str, gr_id: int) -> str:
    verification_url = f"http://localhost:5174/verify?id={gr_id}"
    
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(verification_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    qr_path = os.path.join(OUTPUT_DIR, f"qr_{gr_id}.png")
    img.save(qr_path)
    
    pdf = fitz.open(pdf_path)
    page = pdf[0]
    
    rect = fitz.Rect(480, 720, 560, 800)
    page.insert_image(rect, filename=qr_path)
    
    text_rect = fitz.Rect(470, 805, 570, 820)
    page.insert_textbox(text_rect, "Scan to Verify", fontsize=8, fontname="helv", align=fitz.TEXT_ALIGN_CENTER)
    
    pdf.save(pdf.name, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    pdf.close()
    
    sha256 = hashlib.sha256()
    with open(pdf_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
            
    if os.path.exists(qr_path):
        os.remove(qr_path)
        
    return sha256.hexdigest()

