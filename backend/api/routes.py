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

def string_to_int(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % 10000000

def get_qdrant_results_as_dict(objective: str, top_k: int = 3):
    search_response = search_pipeline(objective, top_k=top_k)
    docs = []
    metas = []
    for res in search_response.results:
        docs.append(res.text)
        metas.append({
            "gr_number": res.gr_no,
            "department": res.department,
            "date": "2023-01-01", # Placeholder since Qdrant payload might not have date
            "policy_area": res.department # Use department as policy area proxy
        })
    return {"documents": [docs], "metadatas": [metas]}

@router.post("/draft/initiate")
def initiate_draft(request: DraftRequest):
    try:
        objective = request.objective
        
        # 1. Retrieve chunks from Qdrant
        results = get_qdrant_results_as_dict(objective, top_k=3)
        
        # 2. Conflict detection
        conflicts = detect_conflicts(results)
        
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
        # Re-retrieve or use passed context
        results = get_qdrant_results_as_dict(request.objective, top_k=3)
        
        # 2. Generate Final Document using LLM
        print("Generating Final GR...")
        json_response = generate_gr_json(request.objective, results, request.officer_decisions, language=request.language)
        
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
        
        # Save to SQLite Database
        fields = json_response.template_fields
        db = SessionLocal()
        gr_id = 999
        try:
            import hashlib

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
                draft_json=json_response.model_dump_json(),
                current_hash=initial_hash
            )
            db.add(new_gr)
            db.commit()
            db.refresh(new_gr)
            gr_id = new_gr.id
        except Exception as e:
            print(f"Error saving to SQLite database: {e}")
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
            print(f"Successfully saved GR {fields.gr_number} to Qdrant")
        except Exception as e:
            print(f"Error adding to RAG: {e}")
        
        return FinalDraftResponse(
            docx_url=f"/api/download/{os.path.basename(docx_path)}",
            pdf_url=f"/api/download/{os.path.basename(pdf_path)}",
            json_data=json_response
        )
    except Exception as e:
        import traceback
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
            text += page.get_text()
        return {"status": "success", "extracted_text": text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/faq/ask")
def ask_faq(request: FAQRequest):
    try:
        answer = answer_faq(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/draft/history")
def get_draft_history():
    db = SessionLocal()
    try:
        history = db.query(GeneratedGR).order_by(GeneratedGR.created_at.desc()).all()
        history_list = []
        for gr in history:
            history_list.append({
                "id": gr.id,
                "gr_number": gr.gr_number,
                "department": gr.department,
                "subject": gr.subject,
                "date": gr.date,
                "status": gr.status,
                "pdf_path": gr.pdf_path,
                "pdf_url": f"/api/download/{os.path.basename(gr.pdf_path)}" if gr.pdf_path else None,
                "docx_url": f"/api/download/{os.path.basename(gr.docx_path)}" if gr.docx_path else None,
                "created_at": gr.created_at.isoformat() if gr.created_at else None,
                "draft_json": gr.draft_json,
                "current_hash": gr.current_hash,
                "ds_notes": gr.deputy_secy_notes
            })
        return {"status": "success", "history": history_list}
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
        else:
            gr.secy_notes = (gr.secy_notes or "") + note_entry
            
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
        db.commit()
        return {"status": "success", "message": "Forwarded to Secretary"}
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
            
        db.commit()
        return {"status": "success", "message": "Approved and Sealed", "hash": gr.sha256_hash}
    finally:
        db.close()

@router.post("/draft/verify")
async def verify_gr(file: UploadFile = File(...)):
    try:
        content = await file.read()
        file_hash = hashlib.sha256(content).hexdigest()
        
        db = SessionLocal()
        gr = db.query(GeneratedGR).filter(GeneratedGR.sha256_hash == file_hash).first()
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
