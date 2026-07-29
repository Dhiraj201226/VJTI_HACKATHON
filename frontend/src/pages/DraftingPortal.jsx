import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { initiateDraft } from '../api/client';

export default function DraftingPortal({ draftState, setDraftState }) {
  const [objective, setObjective] = useState(draftState.objective || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleInitiate = async () => {
    if (!objective.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await initiateDraft(objective);
      setDraftState({
        ...draftState,
        objective: objective,
        conflicts: result.conflicts || [],
        retrievedContext: result.retrieved_context
      });
      
      if (result.status === 'conflicts_detected') {
        navigate('/conflicts');
      } else {
        navigate('/conflicts');
      }
    } catch (err) {
      console.error(err);
      setError('Failed to initiate draft. Is the backend running?');
    } finally {
      setLoading(false);
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
          {/* Objective */}
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
            {/* Department */}
            <div className="space-y-2">
              <label className="font-body-sm font-bold text-on-surface block">Department</label>
              <select className="w-full border border-outline-variant rounded-lg p-2.5 text-body-md focus:border-primary focus:ring-1 outline-none bg-white transition-all">
                <option>Home Department</option>
                <option>Finance Department</option>
                <option>Revenue & Forest</option>
                <option>Law & Judiciary</option>
                <option>Public Health</option>
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
                <button className="flex-1 py-2 px-3 border border-outline-variant rounded text-body-sm hover:bg-surface-container hover:border-primary transition-all">Standard</button>
                <button className="flex-1 py-2 px-3 border border-outline-variant rounded text-body-sm hover:bg-surface-container hover:border-primary transition-all">Urgent</button>
                <button className="flex-1 py-2 px-3 border border-error rounded text-error font-bold text-body-sm bg-error-container/10">Critical</button>
              </div>
            </div>
            {/* Language */}
            <div className="space-y-2">
              <label className="font-body-sm font-bold text-on-surface block">Language Mode</label>
              <div className="flex gap-2">
                <button className="flex-1 py-2 px-3 border border-primary text-primary font-bold bg-primary-container/10 rounded text-body-sm">Marathi (Primary)</button>
                <button className="flex-1 py-2 px-3 border border-outline-variant rounded text-body-sm hover:bg-surface-container">English</button>
              </div>
            </div>
          </div>

          {/* Officer Notes */}
          <div className="space-y-2">
            <label className="font-body-sm font-bold text-on-surface block">Officer Confidential Notes</label>
            <textarea className="w-full border border-outline-variant rounded-lg p-3 text-body-md focus:border-primary focus:ring-1 outline-none transition-all" placeholder="Internal justifications, reference to past cabinet meetings, or specific clauses to include..." rows="4"></textarea>
          </div>

          {/* Document Upload */}
          <div className="space-y-2">
            <label className="font-body-sm font-bold text-on-surface block">Supporting Documents (PDF/DOCX)</label>
            <div className="border-2 border-dashed border-outline-variant rounded-lg p-8 flex flex-col items-center justify-center text-center bg-surface-container-lowest hover:bg-surface-container-low transition-all cursor-pointer">
              <span className="material-symbols-outlined text-4xl text-primary mb-2">cloud_upload</span>
              <p className="font-body-sm text-on-surface font-semibold">Click to upload or drag and drop</p>
              <p className="font-label-caps text-on-surface-variant mt-1">MAX SIZE 25MB PER FILE</p>
            </div>
          </div>
        </div>

        <div className="pt-8 border-t border-outline-variant">
          <button 
            onClick={handleInitiate}
            disabled={loading || !objective.trim()}
            className={`w-full py-4 rounded-lg font-h3 text-h3 font-semibold shadow-lg transition-all flex items-center justify-center gap-3 active:scale-[0.98] ${
              loading || !objective.trim()
                ? 'bg-surface-variant text-on-surface-variant cursor-not-allowed'
                : 'bg-primary-container text-white hover:brightness-110'
            }`}
          >
            {loading ? (
              <>
                <span className="material-symbols-outlined animate-spin">sync</span>
                Processing Alignment...
              </>
            ) : (
              <>
                <span className="material-symbols-outlined">psychology</span>
                Generate AI Draft Resolution
              </>
            )}
          </button>
          <p className="text-center font-body-sm text-on-surface-variant mt-4">Drafting engine will analyze 142,000+ past GRs for semantic alignment.</p>
        </div>
      </div>
    </section>
  );
}
