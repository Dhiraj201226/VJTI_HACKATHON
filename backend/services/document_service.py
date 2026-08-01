import os
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
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
        
        # We use a placeholder logic, so we just create a styled document with placeholders
        # Logo placeholder
        p_logo = doc.add_paragraph('{{LOGO}}')
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Header
        p_header = doc.add_paragraph('महाराष्ट्र शासन\n{{DEPARTMENT}}\nशासन परिपत्रक क्रमांक : {{GR_NUMBER}}\nदिनांक : {{DATE}}')
        p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Subject
        p_sub = doc.add_paragraph('{{SUBJECT}}')
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sub.runs[0].bold = True
        
        # References
        p_ref = doc.add_paragraph('संदर्भ :\n{{REFERENCES}}')
        p_ref.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Body
        p_body = doc.add_paragraph('शासन परिपत्रक :\n{{BODY}}')
        p_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        # Clauses
        p_clauses = doc.add_paragraph('{{CLAUSES}}')
        p_clauses.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        # Signature Command
        p_sigcmd = doc.add_paragraph('\nमहाराष्ट्राचे राज्यपाल यांच्या आदेशानुसार व नावाने,')
        p_sigcmd.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Signature
        p_sig = doc.add_paragraph('{{SIGNATURE}}\n{{DESIGNATION}}')
        p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # Divider Placeholder
        doc.add_paragraph('__________________________________________________________________')
        
        # Copy To
        doc.add_paragraph('प्रत,\n{{COPY_TO}}')
        
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
    
    copy_to_text = ""
    if hasattr(fields, 'copy_to') and fields.copy_to:
        copy_to_text = "\n".join([f"  {i+1}) {c}" for i, c in enumerate(fields.copy_to)])

    replacements = {
        '{{DEPARTMENT}}': fields.department,
        '{{GR_NUMBER}}': fields.gr_number,
        '{{DATE}}': fields.date,
        '{{SUBJECT}}': fields.subject,
        '{{REFERENCES}}': "\n".join([f"    {r}" for r in fields.references]) if fields.references else "",
        '{{BODY}}': "\n\n".join(["    " + p for p in fields.body]),
        '{{CLAUSES}}': "\n\n".join(["    " + c for c in fields.clauses]) if fields.clauses else "",
        '{{SIGNATURE}}': fields.signature,
        '{{DESIGNATION}}': fields.designation,
        '{{COPY_TO}}': copy_to_text,
    }
    
    for placeholder, text in replacements.items():
        replace_placeholder(doc, placeholder, str(text))
        
    # Replace logo placeholder with actual image if exists
    logo_path = os.path.join("data", "logo.png")
    for p in doc.paragraphs:
        if '{{LOGO}}' in p.text:
            p.text = p.text.replace('{{LOGO}}', '')
            if os.path.exists(logo_path):
                r = p.add_run()
                r.add_picture(logo_path, width=Inches(1.0))
        
    docx_filename = f"GR_{fields.gr_number.replace('/', '_')}.docx"
    docx_path = os.path.join(OUTPUT_DIR, docx_filename)
    doc.save(docx_path)
    
    pdf_filename = f"GR_{fields.gr_number.replace('/', '_')}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
    
    # Use docx2pdf for flawless native rendering!
    import pythoncom
    pythoncom.CoInitialize()
    try:
        from docx2pdf import convert
        convert(os.path.abspath(docx_path), os.path.abspath(pdf_path))
    finally:
        pythoncom.CoUninitialize()
    
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
