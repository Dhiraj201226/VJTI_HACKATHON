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
    
    # Since proper DOCX to PDF conversion is complex without MS Word, 
    # we simulate PDF generation for the hackathon using PyMuPDF to create a simple PDF
    # or rely on a system tool. Here we create a simple text PDF from the fields.
    pdf_filename = f"GR_{fields.gr_number.replace('/', '_')}.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_filename)
    
    pdf = fitz.open()
    page = pdf.new_page()
    
    font_path = os.path.join("data", "NotoSansDevanagari.ttf")
    if os.path.exists(font_path):
        page.insert_font(fontname="marathi", fontfile=font_path)
        fontname = "marathi"
    else:
        fontname = "helv"
        
    text = f"""GOVERNMENT OF MAHARASHTRA
Department: {fields.department}
GR Number: {fields.gr_number}
Date: {fields.date}

SUBJECT: {fields.subject}

REFERENCES:
{chr(10).join(fields.references)}

RESOLUTION:
{chr(10).join(fields.body)}

CLAUSES:
{chr(10).join(fields.clauses)}

FINANCIAL IMPLICATIONS:
{fields.financial_implications}

IMPLEMENTATION:
{fields.implementation}

By order and in the name of the Governor of Maharashtra,
{fields.signature}
{fields.designation}

{fields.footer}
"""
    # Use insert_textbox with a Rect to allow text wrapping instead of insert_text
    # Insert Logo
    logo_path = os.path.join("data", "logo.png")
    if os.path.exists(logo_path):
        logo_rect = fitz.Rect(260, 20, 335, 95)  # Center top
        page.insert_image(logo_rect, filename=logo_path)
    
    rect = fitz.Rect(50, 110, 545, 792)  # A4 margins, shifted down for logo
    page.insert_textbox(rect, text, fontsize=10, fontname=fontname)
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
