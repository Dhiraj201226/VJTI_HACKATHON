import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { checkLegalCompliance } from '../api/client';

export default function DocumentPreview({ draftState }) {
  const navigate = useNavigate();
  const [isReviewing, setIsReviewing] = useState(false);
  const [legalResult, setLegalResult] = useState(null);
  const { finalResult } = draftState;

  if (!finalResult) {
    return (
      <div className="text-center mt-10">
        <p className="text-xl text-on-surface-variant mb-4">No document generated yet.</p>
        <button onClick={() => navigate('/')} className="text-primary underline">Go back</button>
      </div>
    );
  }

  const { json_data, docx_url, pdf_url } = finalResult;
  const fields = json_data.template_fields;
  const baseUrl = "http://localhost:8000"; // Should be env var

  const handleLegalReview = async () => {
    setIsReviewing(true);
    setLegalResult(null);
    try {
      const result = await checkLegalCompliance(json_data);
      setLegalResult(result);
    } catch (error) {
      console.error("Legal review failed:", error);
      setLegalResult({ 
        is_valid: false, 
        violations: ["Server/API Error"],
        analysis: error.response?.data?.detail || error.message || "Failed to reach server.",
        recommendation: "Check backend logs or console."
      });
    } finally {
      setIsReviewing(false);
    }
  };

  return (
    <div className="flex flex-col flex-1 h-full -m-6">
      {/* TopNavBar Replacement (Inline for Editor) */}
      <header className="bg-surface-container-highest flex justify-between items-center px-gutter py-stack-sm w-full border-b border-outline-variant z-10">
        <div className="flex items-center gap-4">
          <span className="text-on-surface-variant font-medium font-body-md">Draft Editor</span>
        </div>
        <div className="flex items-center gap-4">
          <a 
            href={`${baseUrl}${docx_url}`} download
            className="bg-white border border-outline-variant px-4 py-2 rounded text-body-sm font-medium hover:bg-surface-container-high transition-all flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-lg">download</span> Download DOCX
          </a>
          <a 
            href={`${baseUrl}${pdf_url}`} download
            className="bg-primary text-white px-6 py-2 rounded text-body-sm font-bold hover:brightness-110 transition-all flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-lg">picture_as_pdf</span> Download PDF
          </a>
        </div>
      </header>

      {/* Workspace */}
      <div className="flex flex-1 overflow-hidden">
        {/* Editor Panel (70%) */}
        <section className="w-full lg:w-[70%] overflow-y-auto p-8 flex flex-col items-center">
          <div className="bg-white mx-auto shadow-2xl overflow-hidden" style={{ width: '210mm', minHeight: '297mm', fontFamily: '"Noto Sans Devanagari", "Mangal", "Arial Unicode MS", serif' }}>
            <div className="p-[20mm]">
              {/* Header */}
              <div className="text-center mb-10">
                <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuCmo0MjyHYoX5jRhX7RDGVXen8paQIhImmLlh87xD7CQdJSaqS8305l7BPhZvugp2MUH7ikvjU_ZG1hg2d7Qk2thkNVTPVdwRZLwmbQjwfsNXzBGTXjSR-MpR8_Jb4er0nF1zBF3_XzTVnSb8bdKFW-0AFxf0ieIxRXybKjFsBK7cNbxn_m7YdoVYGpp4_tJfX1VQpvrrwCbNtt20ZIvEaKvuQHVk28Xzax3OU3YOpayJ2BHWIFZjwQD3M41npIm5BqoQ" alt="Emblem" className="w-16 h-16 mx-auto mb-2 opacity-80 object-contain" />
                <h1 className="font-h3 text-h3 uppercase tracking-widest font-bold">Government of Maharashtra</h1>
                <h2 className="font-h4 text-h4 mt-2">{fields.department}</h2>
                <div className="mt-4 text-sm font-medium">
                  <p>Government Resolution No: {fields.gr_number}</p>
                  <p>Mantralaya, Mumbai 400 032</p>
                  <p>Date: {fields.date}</p>
                </div>
              </div>

              {/* Body */}
              <div className="space-y-6 text-[11pt] leading-relaxed">
                <div className="text-center">
                  <h4 className="font-bold underline uppercase mb-2">Subject:</h4>
                  <p className="font-bold text-lg px-12">{fields.subject}</p>
                </div>

                <div className="space-y-2">
                  <h5 className="font-bold underline uppercase">Reference:</h5>
                  <div className="min-h-[50px] outline-none" contentEditable="true">
                    <ul className="list-disc ml-6 space-y-1">
                      {fields.references?.map((ref, idx) => (
                        <li key={idx}>{ref}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="space-y-2">
                  <h5 className="font-bold underline uppercase">Background:</h5>
                  <div className="min-h-[100px] outline-none" contentEditable="true">
                    {fields.body?.map((para, idx) => (
                      <p key={idx} className="mb-2 text-justify">{para}</p>
                    ))}
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <h5 className="font-bold underline uppercase">Government Resolution:</h5>
                <div className="min-h-[150px] outline-none" contentEditable="true">
                  <ol className="list-decimal ml-6 space-y-2">
                    {fields.clauses?.map((clause, idx) => (
                      <li key={idx} className="text-justify">{clause}</li>
                    ))}
                  </ol>
                </div>
              </div>

              <div className="py-4">
                <h5 className="font-bold text-sm text-gray-600">Financial Implications:</h5>
                <div className="p-1 outline-none" contentEditable="true">{fields.financial_implications}</div>
              </div>

              <div className="pt-12 text-right">
                <p className="font-bold">By order and in the name of the Governor of Maharashtra,</p>
                <div className="mt-16">
                  <p className="font-bold border-t border-black inline-block pt-1 px-8">({fields.signature})</p>
                  <p>{fields.designation}</p>
                </div>
              </div>
            </div>
          </div>
          <div className="text-center text-on-surface-variant font-label-caps opacity-50 my-10 uppercase tracking-widest">
              Achuk Nirnay, Pragat Maharashtra
          </div>
        </section>

        {/* AI Assistant Panel (30%) */}
        <aside className="hidden lg:block w-[30%] bg-surface-container border-l border-outline-variant overflow-y-auto">
          <div className="p-6 space-y-stack-lg">
            <header className="flex items-center justify-between">
              <h3 className="font-h3 text-primary flex items-center gap-2">
                <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>psychology</span>
                AI Assistant
              </h3>
              <span className="bg-primary-container/20 text-primary px-2 py-1 rounded text-[10px] font-bold uppercase">v2.4 Active</span>
            </header>

            {/* Legal Advisor Section */}
            <div className="bg-white rounded-lg p-4 border border-outline-variant shadow-sm space-y-4">
              <h4 className="font-label-caps text-on-surface-variant">Constitutional & Legal Check</h4>
              <p className="text-body-sm text-on-surface-variant">
                Verify if this drafted GR violates any Indian laws or constitutional principles using the AI Legal Advisor.
              </p>
              {/* Action Buttons */}
              <div className="flex gap-4">
                <button 
                  onClick={handleLegalReview}
                  disabled={isReviewing}
                  className="flex-1 bg-surface-container-high border-2 border-outline rounded-lg p-4 flex flex-col items-center justify-center gap-2 hover:bg-surface-container-highest transition-colors disabled:opacity-50"
                >
                  <span className="material-symbols-outlined text-3xl text-primary">
                    {isReviewing ? 'hourglass_empty' : 'gavel'}
                  </span>
                  <span className="font-bold text-on-surface">
                    {isReviewing ? 'Analyzing...' : 'Run Legal Review'}
                  </span>
                </button>

                <button 
                  onClick={() => {
                    alert("Success! The draft has been securely forwarded to the Deputy Secretary's Approval Queue.");
                    window.location.href = "/";
                  }}
                  className="flex-1 bg-primary text-white border-2 border-primary rounded-lg p-4 flex flex-col items-center justify-center gap-2 hover:brightness-110 transition-colors"
                >
                  <span className="material-symbols-outlined text-3xl">
                    send
                  </span>
                  <span className="font-bold">
                    Forward to Deputy Secy
                  </span>
                </button>
              </div>

              {legalResult && (
                <div className={`mt-4 p-4 rounded-lg border ${legalResult.is_valid ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                  <h5 className={`font-bold flex items-center gap-2 ${legalResult.is_valid ? 'text-green-700' : 'text-red-700'}`}>
                    <span className="material-symbols-outlined">
                      {legalResult.is_valid ? "check_circle" : "warning"}
                    </span>
                    {legalResult.is_valid ? "Constitutionally Valid" : "Potential Violations Found"}
                  </h5>
                  {!legalResult.is_valid && legalResult.violations && legalResult.violations.length > 0 && (
                    <ul className="list-disc ml-5 mt-2 text-sm text-red-600">
                      {legalResult.violations.map((v, i) => <li key={i}>{v}</li>)}
                    </ul>
                  )}
                  <p className="text-xs mt-3 text-on-surface-variant leading-relaxed">
                    <strong>Analysis:</strong> {legalResult.analysis}
                  </p>
                  <p className="text-xs mt-2 text-on-surface-variant leading-relaxed">
                    <strong>Recommendation:</strong> {legalResult.recommendation}
                  </p>
                </div>
              )}
            </div>

            {/* Phase 2 Analysis */}
            <div className="space-y-4 border-t border-outline-variant pt-4 mt-4">
              <h4 className="font-label-caps text-on-surface-variant">AI Quality Assurance</h4>
              
              {/* Terminology */}
              {json_data.phase2_analysis?.terminology?.length > 0 && (
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 rounded-r-lg">
                  <p className="text-body-sm text-yellow-800 font-bold mb-1 flex items-center gap-1">
                    <span className="material-symbols-outlined text-sm">spellcheck</span> Terminology Suggestions
                  </p>
                  <ul className="text-xs text-yellow-700 space-y-1 list-disc ml-4">
                    {json_data.phase2_analysis.terminology.map((term, i) => (
                      <li key={i}>
                        Found: <strong>"{term.found}"</strong> → Suggestion: <strong>"{term.suggestion}"</strong>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Template Warnings */}
              {json_data.phase2_analysis?.template_warnings?.length > 0 && (
                <div className="bg-red-50 border-l-4 border-red-500 p-3 rounded-r-lg">
                  <p className="text-body-sm text-red-800 font-bold mb-1 flex items-center gap-1">
                    <span className="material-symbols-outlined text-sm">error</span> Template Warnings
                  </p>
                  <ul className="text-xs text-red-700 space-y-1 list-disc ml-4">
                    {json_data.phase2_analysis.template_warnings.map((warn, i) => (
                      <li key={i}>{warn}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* References Verification */}
              <div className="bg-blue-50 border-l-4 border-blue-500 p-3 rounded-r-lg">
                <p className="text-body-sm text-blue-800 font-bold mb-1 flex items-center gap-1">
                  <span className="material-symbols-outlined text-sm">library_books</span> Reference Check
                </p>
                <p className="text-xs text-blue-700">
                  Verified: <strong>{json_data.phase2_analysis?.references?.verified_references?.length || 0}</strong>
                </p>
                {json_data.phase2_analysis?.references?.missing_references?.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-blue-200">
                    <p className="text-xs text-red-600 font-bold">Unverified / Missing:</p>
                    <ul className="text-xs text-red-600 list-disc ml-4">
                      {json_data.phase2_analysis.references.missing_references.map((miss, i) => (
                        <li key={i}>{miss}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>

            <button 
              onClick={() => navigate('/create')}
              className="w-full mt-4 bg-surface-container-highest hover:bg-outline-variant text-on-surface font-bold py-3 px-4 rounded-lg transition-colors text-center text-sm"
            >
              Start New Draft
            </button>
          </div>
        </aside>
      </div>
    </div>
  );
}
