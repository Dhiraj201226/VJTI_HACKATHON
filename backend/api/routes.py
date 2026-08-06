from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from models.schemas import DraftRequest, GenerateRequest, FinalDraftResponse, LLMDraftResponse
from rag.search import search_pipeline
from services.conflict_service import detect_conflicts
from services.llm_service import generate_gr_json
from services.document_service import generate_documents
import os
import hashlib
from rag.qdrant_db import upload_chunks
from rag.embedder import get_embedding
from rag.models import GRChunk
from db.database import SessionLocal
from db.models import GeneratedGR

router = APIRouter()

@router.get("/models")
def get_models(provider: str = "groq"):
    if provider == "groq":
        return {"models": ["llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768", "gemma-7b-it", "gemma4:31b-cloud"]}
    elif provider == "ollama":
        import requests
        try:
            res = requests.get("http://localhost:11434/api/tags", timeout=2)
            if res.status_code == 200:
                data = res.json()
                models = [m["name"] for m in data.get("models", [])]
                return {"models": models}
        except Exception:
            pass
        return {"models": ["qwen2:1.5b", "llama3:8b", "qwen2:7b"]} # fallback
    return {"models": []}


def string_to_int(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % 10000000

def get_qdrant_results_as_dict(objective: str, top_k: int = 3):
    search_response = search_pipeline(objective, top_k=top_k)
    docs = []
    metas = []
    scores = []
    for res in search_response.results:
        docs.append(res.text)
        scores.append(res.score)
        metas.append({
            "gr_number": res.gr_no,
            "department": res.department,
            "date": "2023-01-01", 
            "policy_area": res.department 
        })
    return {"documents": [docs], "metadatas": [metas], "scores": [scores]}

@router.post("/draft/initiate")
def initiate_draft(request: DraftRequest):
    try:
        objective = request.objective
        
        # 1. Retrieve chunks from Qdrant
        results = get_qdrant_results_as_dict(objective, top_k=3)
        
        # 2. Conflict detection
        conflicts = detect_conflicts(results, provider=request.llm_provider, model=request.llm_model)
        
        # 3. If conflicts exist, return them for officer resolution
        if conflicts:
            return {
                "status": "conflicts_detected",
                "conflicts": [c.dict() for c in conflicts],
                "retrieved_context": results
            }
            
        # No conflicts, we could auto-generate, but let's return context to frontend to hit generate next
        return {
            "status": "ready",
            "conflicts": [],
            "retrieved_context": results
        }
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=traceback.format_exc())

from services.reference_parser import extract_and_verify_references
from services.glossary_service import check_terminology

@router.post("/draft/generate", response_model=FinalDraftResponse)
def generate_draft(request: GenerateRequest):
    try:
        # Re-retrieve or use passed context, blending objective with officer notes for better Qdrant retrieval
        print("DEBUG: generate_draft called")
        search_query = request.objective
        if request.officer_decisions:
            decisions_text = " ".join([d.justification for d in request.officer_decisions if d.justification])
            search_query += " " + decisions_text
            
        print("DEBUG: Calling Qdrant...")
        results = get_qdrant_results_as_dict(search_query, top_k=2)
        
        # 2. Generate Final Document using LLM
        print("DEBUG: Generating Final GR via LLM...")
        json_response = generate_gr_json(request.objective, results, request.officer_decisions, language=request.language, provider=request.llm_provider, model=request.llm_model)
        
        # Force current date to prevent LLM hallucination
        from datetime import date
        json_response.template_fields.date = date.today().strftime('%d %B %Y')
        
        # Phase 2.4: Template Enforcement Validation
        template = json_response.template_fields
        warnings = []
        if not template.subject: warnings.append("Missing Subject")
        if not template.body: warnings.append("Missing Preamble/Body")
        if not template.signature: warnings.append("Missing Signature")
        if not template.financial_implications: warnings.append("Missing Budget/Financial Details")
        
        # Extract raw text from body and clauses for analysis
        body_text = " ".join(template.body) if isinstance(template.body, list) else str(template.body)
        clauses_text = " ".join(template.clauses) if isinstance(template.clauses, list) else str(template.clauses)
        full_text = f"{body_text} {clauses_text}"
        
        # Phase 2.1: Reference Parsing
        reference_data = extract_and_verify_references(full_text)
        
        # Phase 2.3: Terminology Checker
        terminology_suggestions = check_terminology(full_text)
        
        # We will inject these analysis results into a custom field
        json_response.phase2_analysis = {
            "template_warnings": warnings,
            "references": reference_data,
            "terminology": terminology_suggestions
        }
        
        # Generate Documents
        docx_path, pdf_path = generate_documents(json_response)
        
        # Extract raw text from body and clauses for analysis
        body_text = "\n".join(template.body) if isinstance(template.body, list) else str(template.body)
        
        # Calculate cosine similarity based conflict score
        scores_list = results.get("scores", [[]])[0]
        max_score = max(scores_list) if scores_list else 0.0
        final_conflict_score = int(max_score * 100) if (hasattr(json_response, 'conflicts') and json_response.conflicts) else 0

        # Save to SQLite Database
        fields = json_response.template_fields
        db = SessionLocal()
        gr_id = 999
        try:
            import hashlib
            import json

            # Calculate initial hash of the generated PDF
            sha256 = hashlib.sha256()
            with open(pdf_path, 'rb') as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            initial_hash = sha256.hexdigest()

            new_gr = GeneratedGR(
                gr_number=fields.gr_number,
                department=fields.department,
                subject=fields.subject,
                date=fields.date,
                docx_path=docx_path,
                pdf_path=pdf_path,
                status="PENDING_DS_REVIEW",
                priority=request.priority,
                conflict_score=final_conflict_score,
                desk_officer_notes="Draft generated successfully",
                draft_json=json.dumps(json_response.dict()),
                current_hash=initial_hash,
                desk_officer_hash=initial_hash
            )
            db.add(new_gr)
            db.commit()
            db.refresh(new_gr)
            gr_id = new_gr.id
        except Exception as e:
            print(f"Error saving to SQLite database: {repr(e)}")
            db.rollback()
        finally:
            db.close()
        
        # Store generated GR in RAG
        try:
            from rag.embedder import get_embedding
            from rag.qdrant_db import upload_chunks
            from rag.models import GRChunk
            import random
            
            doc_text = f"Government Resolution regarding {fields.subject}. {body_text} Dept: {fields.department}. Date: {fields.date}. GR: {fields.gr_number}"
            
            # Try to extract an integer from gr_number for the DB schema, else random
            gr_no_str = ''.join(filter(str.isdigit, str(fields.gr_number)))
            gr_no_int = int(gr_no_str) if gr_no_str else random.randint(100000, 999999)
            
            chunk = GRChunk(
                gr_no=gr_no_int,
                department=fields.department,
                source_file="Generated_AI_Draft",
                language=request.language or "Marathi",
                chunk_id=1,
                text=doc_text
            )
            
            embedding = get_embedding(doc_text)
            upload_chunks([chunk], [embedding])
            try:
                print(f"Successfully saved GR {fields.gr_number} to Qdrant")
            except UnicodeEncodeError:
                print("Successfully saved GR to Qdrant (omitting GR number due to encoding)")
        except Exception as e:
            try:
                print(f"Error adding to RAG: {repr(e)}")
            except UnicodeEncodeError:
                print("Error adding to RAG (omitting details due to encoding)")
        
        return {
            "status": "success",
            "pdf_url": f"/api/download/{os.path.basename(pdf_path)}",
            "docx_url": f"/api/download/{os.path.basename(docx_path)}",
            "json_data": json_response.dict(),
            "conflict_score": final_conflict_score
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=traceback.format_exc())

from fastapi import Body
from services.legal_service import check_constitutional_validity

@router.post("/draft/legal_review")
def legal_review(gr_json: dict = Body(...)):
    review = check_constitutional_validity(gr_json)
    
    # Store the legal review in the RAG vector DB
    try:
        fields = gr_json.get("template_fields", {})
        gr_number = fields.get("gr_number", "UNKNOWN_GR")
        subject = fields.get("subject", "Unknown Subject")
        
        doc_text = f"Legal Review for GR {gr_number} on subject: {subject}. Is Valid: {review.get('is_valid')}. Analysis: {review.get('analysis')}. Recommendation: {review.get('recommendation')}"
        
        chunk = GRChunk(
            gr_no=string_to_int(f"{gr_number}_LEGAL_REVIEW"),
            department=fields.get("department", "Legal"),
            source_file=f"Legal_Review_{gr_number}.txt",
            language="English",
            chunk_id=2, # Use chunk 2 for legal review
            text=doc_text
        )
        embedding = get_embedding(doc_text)
        upload_chunks([chunk], [embedding])
    except Exception as e:
        print(f"Error adding legal review to Qdrant RAG: {e}")
        
    return review

@router.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join("./data/output", filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="File not found")

@router.get("/rag/stats")
def get_rag_stats():
    from rag.qdrant_db import client
    from config import settings
    import json
    from pathlib import Path
    
    try:
        info = client.get_collection(settings.COLLECTION_NAME)
        
        # Read the unique GR count from our persistent stats file
        stats_file = Path(__file__).parent.parent / "data" / "ingestion_stats.json"
        total_grs = 0
        ai_skipped = 0
        if stats_file.exists():
            try:
                stats = json.loads(stats_file.read_text())
                total_grs = stats.get("total_grs", 0)
                ai_skipped = stats.get("ai_skipped", 0)
            except Exception:
                pass
                
        return {
            "status": "success",
            "collection_name": settings.COLLECTION_NAME,
            "total_points_ingested": info.points_count,
            "total_grs_processed": total_grs,
            "total_grs_skipped_by_ai": ai_skipped
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

from models.schemas import FAQRequest
from services.llm_service import answer_faq
import fitz

@router.post("/draft/extract_text")
async def extract_text_from_pdf(file: UploadFile = File(...)):
    try:
        content = await file.read()
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            page_text = page.get_text().strip()
            # If text is too short, assume it's a scanned page and use OCR
            if len(page_text) < 50:
                try:
                    import pytesseract
                    from PIL import Image
                    import io
                    
                    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                    
                    pix = page.get_pixmap()
                    img_bytes = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_bytes))
                    
                    page_text = pytesseract.image_to_string(img, lang='mar+eng')
                except Exception as e:
                    print(f"OCR Failed for page: {e}")
            
            text += page_text + "\n"
            if len(text) > 10000:
                text = text[:10000] + "\n\n[TEXT TRUNCATED DUE TO LENGTH LIMITS...]"
                break
        return {"status": "success", "extracted_text": text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/faq/ask")
def ask_faq(request: FAQRequest):
    try:
        answer = answer_faq(request.question, provider=request.llm_provider, model=request.llm_model)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/draft/history")
def get_draft_history():
    db = SessionLocal()
    try:
        grs = db.query(GeneratedGR).all()
        
        # Custom sort by priority (Critical > Urgent > Standard) then by created_at desc
        priority_map = {"Critical": 1, "Urgent": 2, "Standard": 3}
        grs.sort(key=lambda x: (-x.created_at.timestamp() if x.created_at else 0)) # stable sort newest first
        grs.sort(key=lambda x: priority_map.get(x.priority, 3)) # stable sort priority

        history = []
        for gr in grs:
            history.append({
                "id": gr.id,
                "gr_number": gr.gr_number,
                "department": gr.department,
                "subject": gr.subject,
                "date": gr.date,
                "status": gr.status,
                "priority": getattr(gr, 'priority', 'Standard'),
                "conflict_score": getattr(gr, 'conflict_score', 0),
                "docx_url": f"/api/download/{os.path.basename(gr.docx_path)}" if gr.docx_path else None,
                "pdf_url": f"/api/download/{os.path.basename(gr.pdf_path)}" if gr.pdf_path else None,
                "desk_officer_notes": gr.desk_officer_notes,
                "deputy_secy_notes": gr.deputy_secy_notes,
                "secy_notes": gr.secy_notes,
                "draft_json": gr.draft_json,
                "priority": gr.priority,
                "current_hash": gr.current_hash,
                "desk_officer_hash": gr.desk_officer_hash,
                "deputy_secy_hash": gr.deputy_secy_hash,
                "created_at": gr.created_at.isoformat() if gr.created_at else None
            })
        return {"status": "success", "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
    


from pydantic import BaseModel

class EditDraftRequest(BaseModel):
    draft_json: str
    author_role: str
    notes: str

@router.put("/draft/{gr_id}/edit")
def edit_draft(gr_id: int, request: EditDraftRequest):
    db = SessionLocal()
    try:
        gr = db.query(GeneratedGR).filter(GeneratedGR.id == gr_id).first()
        if not gr:
            raise HTTPException(status_code=404, detail="GR not found")
            
        import json
        from models.schemas import LLMDraftResponse
        
        # Parse the incoming edited JSON
        edited_data = json.loads(request.draft_json)
        json_data = LLMDraftResponse(**edited_data)
        
        # Regenerate documents with the edited text
        from services.document_service import generate_documents
        docx_path, pdf_path = generate_documents(json_data)
        
        # Calculate new hash
        import hashlib
        sha256 = hashlib.sha256()
        with open(pdf_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)
        new_hash = sha256.hexdigest()
        
        # Update database record
        gr.draft_json = request.draft_json
        gr.docx_path = docx_path
        gr.pdf_path = pdf_path
        gr.current_hash = new_hash
        
        # Append to notes log to show chain of custody
        note_entry = f"[{request.author_role}] Edited Document. New Hash: {new_hash[:8]}. Note: {request.notes}\n"
        if request.author_role == 'Deputy Secretary':
            gr.deputy_secy_notes = (gr.deputy_secy_notes or "") + note_entry
            gr.deputy_secy_hash = new_hash
        else:
            gr.secy_notes = (gr.secy_notes or "") + note_entry
            if gr.status == 'PENDING_DS_REVIEW':
                gr.desk_officer_hash = new_hash
            
        db.commit()
        return {"status": "success", "message": "Draft edited, regenerated, and hash updated."}
    except Exception as e:
        import traceback
        db.rollback()
        raise HTTPException(status_code=500, detail=traceback.format_exc())
    finally:
        db.close()

@router.get("/verify/{document_hash}")
def verify_document(document_hash: str):
    db = SessionLocal()
    try:
        gr = db.query(GeneratedGR).filter(GeneratedGR.current_hash == document_hash).first()
        if not gr:
            raise HTTPException(status_code=404, detail="Document hash not found. This document may be tampered with or fake.")
            
        return {
            "status": "success", 
            "verification": {
                "id": gr.id,
                "gr_number": gr.gr_number,
                "department": gr.department,
                "subject": gr.subject,
                "date": gr.date,
                "current_status": gr.status,
                "created_at": gr.created_at.isoformat() if gr.created_at else None,
                "ds_notes": gr.deputy_secy_notes,
                "secy_notes": gr.secy_notes
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

from models.schemas import ReviewRequest, ApproveRequest
from services.document_service import stamp_qr_and_hash

@router.post("/draft/{gr_id}/review")
def ds_review_gr(gr_id: int, request: ReviewRequest):
    db = SessionLocal()
    try:
        gr = db.query(GeneratedGR).filter(GeneratedGR.id == gr_id).first()
        if not gr:
            raise HTTPException(status_code=404, detail="GR not found")
        
        gr.status = "PENDING_SEC_APPROVAL"
        gr.deputy_secy_notes = request.notes
        gr.deputy_secy_hash = gr.current_hash
        
        db.commit()
        return {"status": "success", "message": "Forwarded to Secretary"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.post("/draft/{gr_id}/approve")
def secy_approve_gr(gr_id: int, request: ApproveRequest):
    db = SessionLocal()
    try:
        gr = db.query(GeneratedGR).filter(GeneratedGR.id == gr_id).first()
        if not gr:
            raise HTTPException(status_code=404, detail="GR not found")
        
        gr.status = "APPROVED"
        gr.secy_notes = request.notes
        
        # Stamp QR and hash
        if gr.pdf_path and os.path.exists(gr.pdf_path):
            file_hash = stamp_qr_and_hash(gr.pdf_path, gr.id)
            gr.sha256_hash = file_hash
            gr.current_hash = file_hash  # Fix: Ensure current_hash tracks the final QR-stamped file!
            
        db.commit()
        return {"status": "success", "message": "Approved and Sealed", "hash": gr.sha256_hash}
    finally:
        db.close()

@router.post("/draft/{gr_id}/reject")
def reject_gr(gr_id: int, request: ReviewRequest):
    db = SessionLocal()
    try:
        gr = db.query(GeneratedGR).filter(GeneratedGR.id == gr_id).first()
        if not gr:
            raise HTTPException(status_code=404, detail="GR not found")
        
        gr.status = "REJECTED"
        note_entry = f"[Rejected] Note: {request.notes}\n"
        
        # Append note to the appropriate column based on current status
        if gr.status == "PENDING_SEC_APPROVAL":
            gr.secy_notes = (gr.secy_notes or "") + note_entry
        else:
            gr.deputy_secy_notes = (gr.deputy_secy_notes or "") + note_entry
            
        db.commit()
        return {"status": "success", "message": "Draft rejected and sent back to Desk Officer"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.post("/draft/verify")
async def verify_gr(file: UploadFile = File(...)):
    try:
        content = await file.read()
        file_hash = hashlib.sha256(content).hexdigest()
        
        db = SessionLocal()
        from sqlalchemy import or_
        gr = db.query(GeneratedGR).filter(or_(GeneratedGR.sha256_hash == file_hash, GeneratedGR.current_hash == file_hash)).first()
        db.close()
        
        if gr:
            return {
                "status": "authentic",
                "message": "Document is authentic and verified.",
                "gr_number": gr.gr_number,
                "department": gr.department,
                "subject": gr.subject,
                "date": gr.date
            }
        else:
            return {
                "status": "tampered",
                "message": "Warning: Document has been altered or is fake."
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SummarizeRequest(BaseModel):
    text: str
    llm_provider: str = "groq"
    llm_model: str = None

@router.post("/chat/summarize")
def summarize_text(request: SummarizeRequest):
    try:
        from services.llm_service import generate_summary
        summary = generate_summary(request.text, provider=request.llm_provider, model=request.llm_model)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class TranslateRequest(BaseModel):
    text: str
    target_language: str
    llm_provider: str = "groq"
    llm_model: str = None

@router.post("/draft/translate")
def translate_document(request: TranslateRequest):
    try:
        from services.llm_service import translate_text
        translation = translate_text(request.text, request.target_language, provider=request.llm_provider, model=request.llm_model)
        return {"translation": translation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
