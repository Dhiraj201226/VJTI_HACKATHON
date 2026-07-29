from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DraftRequest(BaseModel):
    objective: str

class Conflict(BaseModel):
    conflict_id: str
    old_policy: str
    latest_policy: str
    reason: str
    recommendation: str

class OfficerDecision(BaseModel):
    conflict_id: str
    selected_policy: str
    justification: Optional[str] = None

class GenerateRequest(BaseModel):
    objective: str
    officer_decisions: List[OfficerDecision] = []

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

class LLMDraftResponse(BaseModel):
    references: List[Reference]
    conflicts: List[Conflict]
    template_fields: TemplateFields
    phase2_analysis: Optional[Dict[str, Any]] = None

class FinalDraftResponse(BaseModel):
    docx_url: str
    pdf_url: str
    json_data: LLMDraftResponse

class FAQRequest(BaseModel):
    question: str
