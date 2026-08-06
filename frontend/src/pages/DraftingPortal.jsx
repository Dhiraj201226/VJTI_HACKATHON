import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { initiateDraft, uploadAndExtractText } from '../api/client';

const DEPARTMENTS = [
  "Agriculture, Dairy Development, Animal Husbandry and Fisheries Department",
  "Co-operation, Textiles and Marketing Department",
  "Environment Department",
  "Finance Department",
  "Food, Civil Supplies and Consumer Protection Department",
  "General Administration Department",
  "Higher and Technical Education Department",
  "Home Department",
  "Housing Department",
  "Industries, Energy and Labour Department",
  "Information Technology Department",
  "Law and Judiciary Department",
  "Marathi Language Department",
  "Medical Education and Drugs Department",
  "Minorities Development Department",
  "Other Backward Bahujan Welfare Department",
  "Parliamentary Affairs Department",
  "Persons with Disabilities Welfare Department",
  "Planning Department",
  "Public Health Department",
  "Public Works Department",
  "Revenue and Forest Department",
  "Rural Development Department",
  "School Education and Sports Department",
  "Skill Development and Entrepreneurship Department",
  "Social Justice and Special Assistance Department",
  "Soil and Water Conservation Department",
  "Tourism and Cultural Affairs Department",
  "Tribal Development Department",
  "Urban Development Department",
  "Water Resources Department",
  "Water Supply and Sanitation Department",
  "Women and Child Development Department"
];

export default function DraftingPortal({ draftState, setDraftState }) {
  const [objective, setObjective] = useState(draftState.objective || '');
  const [officerNotes, setOfficerNotes] = useState('');
  const [references, setReferences] = useState('');
  const [copyTo, setCopyTo] = useState('');
  const [priority, setPriority] = useState('Standard');
  const [language, setLanguage] = useState('Marathi');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleInitiate = async () => {
    if (!objective.trim() && !file) return;
    setLoading(true);
    setError(null);
    try {
      let finalObjective = objective;
      
      if (file) {
        const extractResult = await uploadAndExtractText(file);
        if (extractResult.status === 'success' && extractResult.extracted_text) {
          finalObjective += `\n\n[CONTEXT FROM ATTACHED PROPOSAL DOCUMENT]:\n${extractResult.extracted_text}`;
        }
      }

      if (officerNotes.trim()) {
        finalObjective += `\n\n[OFFICER CONFIDENTIAL NOTES]:\n${officerNotes}`;
      }
      
      if (references.trim()) {
        finalObjective += `\n\n[REFERENCES (संदर्भ)]:\n${references}`;
      }
      
      if (copyTo.trim()) {
        finalObjective += `\n\n[COPY TO (प्रत)]:\n${copyTo}`;
      }

      const result = await initiateDraft({ objective: finalObjective, language });
      setDraftState({
        ...draftState,
        objective: finalObjective,
        conflicts: result.conflicts || [],
        retrievedContext: result.retrieved_context,
        language: language
      });
      
      navigate('/conflicts');
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to initiate draft");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateClick = async () => {
    setLoading(true);
    setError(null);
    try {
      // Generate Document with LLM
      const generateResponse = await generateDraft(
        draftState.objective,
        draftState.conflicts.map(c => ({
          conflict_id: c.conflict_id,
          selected_policy: c.decision || 'No decision made',
          justification: c.justification || ''
        })),
        language
      );
      
      setDraftState({
        ...draftState,
        generatedContent: generateResponse.template_fields,
        pdfUrl: generateResponse.pdf_url
      });
      
      navigate('/preview');
    } catch (err) {
      setError(err.response?.data?.detail || "Generation failed");
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  return (
    <section className="p-gutter overflow-y-auto border-outline-variant bg-white w-full rounded-xl shadow-sm border">
      <div className="max-w-2xl mx-auto space-y-stack-lg p-6">
        <header>
          <h2 className="font-h2 text-h2 text-primary mb-2">Government Resolution Parameters</h2>
          <p className="font-body-md text-on-surface-variant">Fill in the institutional requirements to initiate the AI-assisted drafting process.</p>
        </header>

        {error && (
          <div className="bg-error-container text-on-error-container p-4 rounded-lg mb-6 text-sm font-medium">
            {error}
          </div>
        )}

        <div className="space-y-stack-md">
          <div className="space-y-2">
            <label className="font-body-sm font-bold text-on-surface block">Objective & Subject Line</label>
            <textarea 
              className="w-full border border-outline-variant rounded-lg p-3 text-body-md focus:border-primary focus:ring-1 outline-none transition-all" 
              placeholder="e.g., Sanctioning of funds for modernizing district courts in Vidarbha region..." 
              rows="3"
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
            ></textarea>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-stack-md">
            <div className="space-y-2">
              <label className="font-body-sm font-bold text-on-surface block">Department</label>
              <select className="w-full border border-outline-variant rounded-lg p-2.5 text-body-md focus:border-primary focus:ring-1 outline-none bg-white transition-all">
                {DEPARTMENTS.map(dept => (
                  <option key={dept} value={dept}>{dept}</option>
                ))}
              </select>
            </div>
            {/* Policy Category */}
            <div className="space-y-2">
              <label className="font-body-sm font-bold text-on-surface block">Policy Category</label>
              <select className="w-full border border-outline-variant rounded-lg p-2.5 text-body-md focus:border-primary focus:ring-1 outline-none bg-white transition-all">
                <option>Financial Allocation</option>
                <option>Appointment/Recruitment</option>
                <option>New Infrastructure</option>
                <option>Public Policy Amendment</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-stack-md">
            {/* Priority */}
            <div className="space-y-2">
              <label className="font-body-sm font-bold text-on-surface block">Priority Level</label>
              <div className="flex gap-2">
                <button 
                  onClick={() => setPriority('Standard')}
                  className={`flex-1 py-2 px-3 border rounded text-body-sm transition-all ${priority === 'Standard' ? 'border-primary bg-primary-container/10 text-primary font-bold' : 'border-outline-variant hover:bg-surface-container hover:border-primary'}`}
                >Standard</button>
                <button 
                  onClick={() => setPriority('Urgent')}
                  className={`flex-1 py-2 px-3 border rounded text-body-sm transition-all ${priority === 'Urgent' ? 'border-orange-500 bg-orange-50 text-orange-600 font-bold' : 'border-outline-variant hover:bg-surface-container hover:border-orange-500'}`}
                >Urgent</button>
                <button 
                  onClick={() => setPriority('Critical')}
                  className={`flex-1 py-2 px-3 border rounded text-body-sm transition-all ${priority === 'Critical' ? 'border-error bg-error-container/10 text-error font-bold' : 'border-outline-variant hover:bg-surface-container hover:border-error'}`}
                >Critical</button>
              </div>
            </div>
            {/* Language */}
            <div className="space-y-2">
              <label className="font-body-sm font-bold text-on-surface block">Language Mode</label>
              <div className="flex gap-2">
                <button 
                  onClick={() => setLanguage('Marathi')}
                  className={`flex-1 py-2 px-3 border rounded text-body-sm transition-all ${language === 'Marathi' ? 'border-primary text-primary font-bold bg-primary-container/10' : 'border-outline-variant hover:bg-surface-container hover:border-primary'}`}
                >Marathi (Primary)</button>
                <button 
                  onClick={() => setLanguage('English')}
                  className={`flex-1 py-2 px-3 border rounded text-body-sm transition-all ${language === 'English' ? 'border-primary text-primary font-bold bg-primary-container/10' : 'border-outline-variant hover:bg-surface-container hover:border-primary'}`}
                >English</button>
              </div>
            </div>
          </div>

          {/* Officer Notes */}
          <div className="space-y-2">
            <label className="font-body-sm font-bold text-on-surface block">Officer Confidential Notes</label>
            <textarea 
              className="w-full border border-outline-variant rounded-lg p-3 text-body-md focus:border-primary focus:ring-1 outline-none transition-all" 
              placeholder="Internal justifications, reference to past cabinet meetings, or specific clauses to include..." 
              rows="2"
              value={officerNotes}
              onChange={(e) => setOfficerNotes(e.target.value)}
            ></textarea>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-stack-md">
            {/* References */}
            <div className="space-y-2">
              <label className="font-body-sm font-bold text-on-surface block">References (संदर्भ)</label>
              <textarea 
                className="w-full border border-outline-variant rounded-lg p-3 text-body-md focus:border-primary focus:ring-1 outline-none transition-all" 
                placeholder="e.g., शासन निर्णय, शालेय शिक्षण व क्रीडा विभाग, समक्रमांक..." 
                rows="3"
                value={references}
                onChange={(e) => setReferences(e.target.value)}
              ></textarea>
            </div>
            
            {/* Copy To */}
            <div className="space-y-2">
              <label className="font-body-sm font-bold text-on-surface block">Copy To (प्रत)</label>
              <textarea 
                className="w-full border border-outline-variant rounded-lg p-3 text-body-md focus:border-primary focus:ring-1 outline-none transition-all" 
                placeholder="e.g., १) आयुक्त (शिक्षण), महाराष्ट्र राज्य, पुणे\n२) सर्व विभागीय शिक्षण उपसंचालक" 
                rows="3"
                value={copyTo}
                onChange={(e) => setCopyTo(e.target.value)}
              ></textarea>
            </div>
          </div>

          {/* Document Upload */}
          <div className="space-y-2">
            <label className="font-body-sm font-bold text-on-surface block">Supporting Documents (PDF Only)</label>
            <div 
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed ${file ? 'border-primary bg-primary-container/10' : 'border-outline-variant bg-surface-container-lowest'} rounded-lg p-8 flex flex-col items-center justify-center text-center hover:bg-surface-container-low transition-all cursor-pointer`}
            >
              <input 
                type="file" 
                ref={fileInputRef} 
                className="hidden" 
                accept="application/pdf"
                onChange={handleFileChange}
              />
              <span className="material-symbols-outlined text-4xl text-primary mb-2">
                {file ? 'task' : 'cloud_upload'}
              </span>
              <p className="font-body-sm text-on-surface font-semibold">
                {file ? file.name : "Click to upload PDF Proposal"}
              </p>
              {!file && <p className="font-label-caps text-on-surface-variant mt-1">Extracts text and feeds into AI Engine</p>}
              {file && (
                <button 
                  onClick={(e) => { e.stopPropagation(); setFile(null); }}
                  className="mt-2 text-xs text-error hover:underline"
                >
                  Remove File
                </button>
              )}
            </div>
          </div>
        </div>

        <div className="pt-8 border-t border-outline-variant">
          <button 
            onClick={handleInitiate}
            disabled={loading || (!objective.trim() && !file)}
            className={`w-full py-4 rounded-lg font-h3 text-h3 font-semibold shadow-lg transition-all flex items-center justify-center gap-3 active:scale-[0.98] ${
              loading || (!objective.trim() && !file)
                ? 'bg-surface-variant text-on-surface-variant cursor-not-allowed'
                : 'bg-primary-container text-white hover:brightness-110'
            }`}
          >
            {loading ? (
              <>
                <span className="material-symbols-outlined animate-spin">sync</span>
                {file ? "Extracting PDF & Aligning Policies..." : "Processing Alignment..."}
              </>
            ) : (
              <>
                <span className="material-symbols-outlined">psychology</span>
                Generate AI Draft Resolution
              </>
            )}
          </button>
        </div>
      </div>
    </section>
  );
}
