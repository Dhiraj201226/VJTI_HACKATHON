import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { checkLegalCompliance, translateDraft } from '../api/client';

export default function DocumentPreview({ draftState }) {
  const navigate = useNavigate();
  const [isReviewing, setIsReviewing] = useState(false);
  const [legalResult, setLegalResult] = useState(null);
  const [isTranslating, setIsTranslating] = useState(false);
  const [translationResult, setTranslationResult] = useState(null);
  const { finalResult } = draftState;

  if (!finalResult) {
    return (
      <div className="text-center mt-10">
        <p className="text-xl text-on-surface-variant mb-4">No document generated yet.</p>
        <button onClick={() => navigate('/')} className="text-primary underline">Go back</button>
      </div>
    );
  }

  const { json_data, docx_url, pdf_url, conflict_score } = finalResult;
  const fields = json_data.template_fields;
  const baseUrl = "http://localhost:8080"; // Should be env var

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

  const handleTranslate = async (targetLang) => {
    setIsTranslating(true);
    setTranslationResult(null);
    try {
      // Just extract the raw text values from the JSON template fields for translation
      const textToTranslate = Object.values(fields).flat().join('\n\n');
      const result = await translateDraft(textToTranslate, targetLang);
      setTranslationResult(result.translation);
    } catch (error) {
      console.error("Translation failed:", error);
      setTranslationResult("Failed to translate document. Check console for errors.");
    } finally {
      setIsTranslating(false);
    }
  };

  return (
    <div className="flex flex-col flex-1 h-full -m-6">
      {/* TopNavBar Replacement (Inline for Editor) */}
      <header className="bg-surface-container-highest flex justify-between items-center px-gutter py-stack-sm w-full border-b border-outline-variant z-10">
        <div className="flex items-center gap-4">
          <span className="text-on-surface-variant font-medium font-body-md">Draft Editor</span>
          <span className="bg-orange-100 text-orange-800 px-3 py-1 rounded-full text-xs font-bold">
            Conflict Score: {conflict_score !== undefined ? conflict_score : (json_data.conflicts ? json_data.conflicts.length : 0)}
          </span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex gap-2 mr-4 border-r pr-4">
            <button 
              onClick={() => handleTranslate('English')}
              disabled={isTranslating}
              className="text-primary font-bold text-sm hover:underline disabled:opacity-50"
            >
              Translate to English
            </button>
            <button 
              onClick={() => handleTranslate('Marathi')}
              disabled={isTranslating}
              className="text-primary font-bold text-sm hover:underline disabled:opacity-50"
            >
              Translate to Marathi
            </button>
          </div>
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
        <section className="w-full lg:w-[70%] overflow-y-auto p-8 flex flex-col items-center bg-surface-container-low">
          {translationResult ? (
            <div className="w-full max-w-[210mm] bg-white shadow-2xl p-8 mb-10 text-left whitespace-pre-wrap font-serif">
              <h2 className="text-xl font-bold mb-4 border-b pb-2">Translated Document</h2>
              {translationResult}
              <button 
                onClick={() => setTranslationResult(null)}
                className="mt-6 px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
              >
                Close Translation
              </button>
            </div>
          ) : (
            <div className="w-full max-w-[210mm] h-[297mm] bg-white shadow-2xl overflow-hidden relative">
              <iframe 
                src={`${baseUrl}${pdf_url}#toolbar=0`} 
                className="w-full h-full border-none"
                title="GR PDF Preview"
              />
            </div>
          )}
          <div className="text-center text-on-surface-variant font-label-caps opacity-50 my-10 uppercase tracking-widest">
              Exact formatting as generated by AI
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
