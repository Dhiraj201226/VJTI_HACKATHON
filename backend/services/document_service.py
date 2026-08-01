import os
from docx import Document
import fitz  # PyMuPDF
from models.schemas import LLMDraftResponse
import shutil

TEMPLATE_PATH = "./templates/official_template.docx"
OUTPUT_DIR = "./data/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_mock_template_if_not_exists():
    os.makedirs("./templates", exist_ok=True)
    if not os.path.exists(TEMPLATE_PATH):
        doc = Document()
        doc.add_heading('GOVERNMENT OF MAHARASHTRA', 0)
        doc.add_paragraph('Department: {{DEPARTMENT}}')
        doc.add_paragraph('GR Number: {{GR_NUMBER}}')
        doc.add_paragraph('Date: {{DATE}}')
        doc.add_heading('Subject', level=1)
        doc.add_paragraph('{{SUBJECT}}')
        doc.add_heading('References', level=1)
        doc.add_paragraph('{{REFERENCES}}')
        doc.add_heading('Resolution', level=1)
        doc.add_paragraph('{{BODY}}')
        doc.add_heading('Clauses', level=2)
        doc.add_paragraph('{{CLAUSES}}')
        doc.add_heading('Financial Implications', level=2)
        doc.add_paragraph('{{FINANCIAL_IMPLICATIONS}}')
        doc.add_heading('Implementation', level=2)
        doc.add_paragraph('{{IMPLEMENTATION}}')
        doc.add_paragraph('\n\nBy order and in the name of the Governor of Maharashtra,\n')
        doc.add_paragraph('{{SIGNATURE}}')
        doc.add_paragraph('{{DESIGNATION}}')
        doc.add_paragraph('\n{{FOOTER}}')
        doc.save(TEMPLATE_PATH)

def replace_placeholder(doc, placeholder, replacement_text):
    for p in doc.paragraphs:
        if placeholder in p.text:
            p.text = p.text.replace(placeholder, replacement_text)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    if placeholder in p.text:
                        p.text = p.text.replace(placeholder, replacement_text)

def generate_documents(json_data: LLMDraftResponse):
    create_mock_template_if_not_exists()
    
    doc = Document(TEMPLATE_PATH)
    fields = json_data.template_fields
    
    replacements = {
        '{{DEPARTMENT}}': fields.department,
        '{{GR_NUMBER}}': fields.gr_number,
        '{{DATE}}': fields.date,
        '{{SUBJECT}}': fields.subject,
        '{{REFERENCES}}': "\n".join(fields.references),
        '{{BODY}}': "\n\n".join(fields.body),
        '{{CLAUSES}}': "\n\n".join(fields.clauses),
        '{{FINANCIAL_IMPLICATIONS}}': fields.financial_implications,
        '{{IMPLEMENTATION}}': fields.implementation,
        '{{SIGNATURE}}': fields.signature,
        '{{DESIGNATION}}': fields.designation,
        '{{FOOTER}}': fields.footer,
    }
    
    for placeholder, text in replacements.items():
        replace_placeholder(doc, placeholder, str(text))
        
    docx_filename = f"GR_{fields.gr_number.replace('/', '_')}.docx"
    docx_path = os.path.join(OUTPUT_DIR, docx_filename)
    doc.save(docx_path)
    
    # Overleaf/LaTeX style PDF generation
    pdf_filename = f"GR_{fields.gr_number.replace('/', '_')}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
    
    pdf = fitz.open()
    page = pdf.new_page(width=595, height=842) # A4 size
    
    font_path = os.path.join("data", "NotoSansDevanagari.ttf")
    if os.path.exists(font_path):
        page.insert_font(fontname="marathi", fontfile=font_path)
        fontname = "marathi"
    else:
        fontname = "helv"
        
    # Layout constants
    MARGIN_LEFT = 50
    MARGIN_RIGHT = 545
    MARGIN_TOP = 50
    current_y = MARGIN_TOP
    
    # 1. Logo (Center Top)
    logo_path = os.path.join("data", "logo.png")
    if os.path.exists(logo_path):
        logo_rect = fitz.Rect(260, current_y, 335, current_y + 75)
        page.insert_image(logo_rect, filename=logo_path)
        current_y += 85
    
    # 2. Header Information (Center)
    header_text = f"महाराष्ट्र शासन\n{fields.department}\nशासन परिपत्रक क्रमांक : {fields.gr_number}\nदिनांक : {fields.date}"
    page.insert_textbox(fitz.Rect(MARGIN_LEFT, current_y, MARGIN_RIGHT, current_y + 80), 
                       header_text, fontsize=12, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER)
    current_y += 90
    
    # 3. Subject (Center, Bold/Large)
    page.insert_textbox(fitz.Rect(MARGIN_LEFT + 50, current_y, MARGIN_RIGHT - 50, current_y + 60), 
                       fields.subject, fontsize=14, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER)
    current_y += 70
    
    # 4. References (Left aligned, indented slightly)
    if fields.references:
        ref_text = "संदर्भ :\n" + "\n".join([f"    {r}" for r in fields.references])
        page.insert_textbox(fitz.Rect(MARGIN_LEFT, current_y, MARGIN_RIGHT, current_y + 60), 
                           ref_text, fontsize=11, fontname=fontname, align=fitz.TEXT_ALIGN_LEFT)
        current_y += 70
    
    # 5. Main Body ("शासन परिपत्रक :")
    page.insert_textbox(fitz.Rect(MARGIN_LEFT, current_y, MARGIN_RIGHT, current_y + 20), 
                       "शासन परिपत्रक :", fontsize=12, fontname=fontname, align=fitz.TEXT_ALIGN_LEFT)
    current_y += 30
    
    body_text = "\n\n".join(["    " + p for p in fields.body])
    if fields.clauses:
        body_text += "\n\n" + "\n\n".join(["    " + c for c in fields.clauses])
    
    # Estimate body height, insert text
    page.insert_textbox(fitz.Rect(MARGIN_LEFT, current_y, MARGIN_RIGHT, current_y + 250), 
                       body_text, fontsize=11, fontname=fontname, align=fitz.TEXT_ALIGN_JUSTIFY)
    current_y += 260
    
    # 6. Signature Block (Right aligned)
    sig_y = current_y + 20
    page.insert_textbox(fitz.Rect(MARGIN_LEFT, sig_y, MARGIN_RIGHT, sig_y + 20), 
                       "महाराष्ट्राचे राज्यपाल यांच्या आदेशानुसार व नावाने,", fontsize=11, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER)
    
    sig_text = f"\n\n{fields.signature}\n{fields.designation}"
    page.insert_textbox(fitz.Rect(MARGIN_RIGHT - 200, sig_y + 30, MARGIN_RIGHT, sig_y + 100), 
                       sig_text, fontsize=11, fontname=fontname, align=fitz.TEXT_ALIGN_RIGHT)
    current_y = sig_y + 110
    
    # 7. Horizontal Line
    page.draw_line(fitz.Point(MARGIN_LEFT, current_y), fitz.Point(MARGIN_RIGHT, current_y), color=(0,0,0), width=1.5)
    current_y += 20
    
    # 8. Copy To (प्रत)
    if hasattr(fields, 'copy_to') and fields.copy_to:
        copy_text = "प्रत,\n" + "\n".join([f"  {i+1}) {c}" for i, c in enumerate(fields.copy_to)])
        page.insert_textbox(fitz.Rect(MARGIN_LEFT, current_y, MARGIN_RIGHT, current_y + 120), 
                           copy_text, fontsize=10, fontname=fontname, align=fitz.TEXT_ALIGN_LEFT)
    
    # 9. Page Number (Footer)
    page.insert_textbox(fitz.Rect(MARGIN_LEFT, 800, MARGIN_RIGHT, 820), 
                       "पृष्ठ १ पैकी १", fontsize=10, fontname=fontname, align=fitz.TEXT_ALIGN_CENTER)
    
    pdf.save(pdf_path)
    
    return docx_path, pdf_path

import qrcode
import hashlib

def stamp_qr_and_hash(pdf_path: str, gr_id: int) -> str:
    """Stamps a QR code onto an existing PDF, saves it, and returns the SHA256 hash."""
    verification_url = f"http://localhost:5174/verify?id={gr_id}"
    
    # Generate QR Code image
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(verification_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    qr_path = os.path.join(OUTPUT_DIR, f"qr_{gr_id}.png")
    img.save(qr_path)
    
    # Open the existing PDF
    pdf = fitz.open(pdf_path)
    page = pdf[0] # Stamp on first page
    
    # Insert QR at bottom right corner (approx coords for A4)
    rect = fitz.Rect(480, 720, 560, 800)
    page.insert_image(rect, filename=qr_path)
    
    # Add a small text below QR
    text_rect = fitz.Rect(470, 805, 570, 820)
    page.insert_textbox(text_rect, "Scan to Verify", fontsize=8, fontname="helv", align=fitz.TEXT_ALIGN_CENTER)
    
    # Overwrite the PDF
    pdf.save(pdf.name, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    pdf.close()
    
    # Calculate SHA256 Hash
    sha256 = hashlib.sha256()
    with open(pdf_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
            
    # Clean up QR image
    if os.path.exists(qr_path):
        os.remove(qr_path)
        
    return sha256.hexdigest()
