from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DraftRequest(BaseModel):
    objective: str
    language: Optional[str] = "Marathi"
    priority: str = "Standard"
    llm_provider: Optional[str] = "groq"
    llm_model: Optional[str] = None

class Conflict(BaseModel):
    conflict_id: str
    old_policy: str
    latest_policy: str
    reason: str
    recommendation: str
    similarity_score: Optional[int] = None

class OfficerDecision(BaseModel):
    conflict_id: str
    selected_policy: str
    justification: Optional[str] = None

class GenerateRequest(BaseModel):
    objective: str
    officer_decisions: List[OfficerDecision] = []
    language: Optional[str] = "Marathi"
    priority: str = "Standard"
    llm_provider: Optional[str] = "groq"
    llm_model: Optional[str] = None

class Reference(BaseModel):
    gr_number: str
    department: str
    date: str
    title: str

class TemplateFields(BaseModel):
    department: str
    gr_number: str
    date: str
    subject: str
    references: List[str]
    body: List[str]
    clauses: List[str]
    financial_implications: str
    implementation: str
    signature: str
    designation: str
    footer: str
    copy_to: List[str] = []

class LLMDraftResponse(BaseModel):
    references: List[Reference]
    conflicts: List[Conflict]
    template_fields: TemplateFields
    phase2_analysis: Optional[Dict[str, Any]] = None

class FinalDraftResponse(BaseModel):
    status: str
    pdf_url: str
    docx_url: str
    json_data: LLMDraftResponse
    conflict_score: Optional[int] = None

class FAQRequest(BaseModel):
    question: str
    llm_provider: Optional[str] = "groq"
    llm_model: Optional[str] = None

class ReviewRequest(BaseModel):
    notes: str

class ApproveRequest(BaseModel):
    notes: str
