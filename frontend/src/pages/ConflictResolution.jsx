import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { generateDraft } from '../api/client';

export default function ConflictResolution({ draftState, setDraftState }) {
  const navigate = useNavigate();
  const conflicts = draftState.conflicts || [];
  const [decisions, setDecisions] = useState({});
  const [loading, setLoading] = useState(false);

  const handleDecisionChange = (conflictId, policyChoice) => {
    setDecisions({
      ...decisions,
      [conflictId]: {
        selected_policy: policyChoice,
        justification: "Officer approved recommended policy change."
      }
    });
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const officerDecisions = Object.entries(decisions).map(([conflict_id, data]) => ({
        conflict_id,
        ...data
      }));
      
      const result = await generateDraft(draftState.objective, officerDecisions);
      
      setDraftState({
        ...draftState,
        finalResult: result
      });
      navigate('/result');
    } catch (err) {
      console.error(err);
      alert("Generation failed");
    } finally {
      setLoading(false);
    }
  };

  if (conflicts.length === 0) {
    return (
      <div className="bg-surface-container-lowest rounded-xl shadow-lg p-8 border border-outline-variant text-center mt-8 max-w-2xl mx-auto">
        <div className="text-primary mb-4 flex justify-center">
          <span className="material-symbols-outlined text-6xl">check_circle</span>
        </div>
        <h2 className="font-h2 text-h2 text-on-surface mb-2">No Conflicts Detected</h2>
        <p className="font-body-md text-on-surface-variant mb-8">The AI found relevant context and is ready to generate the GR.</p>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="bg-primary text-white font-bold py-3 px-8 rounded-lg shadow-md transition-all hover:brightness-110 flex items-center gap-2 mx-auto"
        >
          {loading ? (
            <><span className="material-symbols-outlined animate-spin">sync</span> Drafting Resolution...</>
          ) : (
            <><span className="material-symbols-outlined">description</span> Generate Document</>
          )}
        </button>
      </div>
    );
  }

  return (
    <div className="flex-1 flex gap-gutter max-w-container-max mx-auto -m-6 p-gutter">
      {/* Main Workflow Area */}
      <div className="flex-1 space-y-gutter pb-32">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="font-h1 text-h1 text-primary">Policy Conflict Review</h1>
            <p className="font-body-lg text-body-lg text-on-surface-variant mt-2 max-w-3xl">AI has identified logical inconsistencies based on existing statutes. Resolve conflicts to move to the iterative validation loop.</p>
          </div>
        </div>

        {/* Workflow Stepper */}
        <div className="bg-white border border-outline-variant rounded p-stack-md flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-primary text-white flex items-center justify-center text-xs font-bold">1</div>
            <span className="text-body-sm font-semibold text-primary hidden md:block">Objective Submitted</span>
          </div>
          <div className="flex-grow h-0.5 bg-primary mx-4"></div>
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-full bg-primary text-white flex items-center justify-center text-xs font-bold ring-4 ring-primary-container">2</div>
            <span className="text-body-sm font-bold text-primary hidden md:block">Conflict Review</span>
          </div>
          <div className="flex-grow h-0.5 bg-outline-variant mx-4"></div>
          <div className="flex items-center gap-2 opacity-50">
            <div className="h-8 w-8 rounded-full bg-outline-variant text-on-surface flex items-center justify-center text-xs font-bold">3</div>
            <span className="text-body-sm font-medium hidden md:block">Final GR Generation</span>
          </div>
        </div>

        {conflicts.map((conflict) => (
          <div key={conflict.conflict_id} className="bg-white border border-outline-variant rounded overflow-hidden shadow-sm">
            <div className="bg-surface-container-high px-gutter py-stack-sm flex justify-between items-center border-b border-outline-variant">
              <div className="flex gap-4 items-center">
                <span className="px-2 py-0.5 bg-error/10 text-error rounded font-label-caps text-label-caps font-bold">LOGICAL CONFLICT</span>
                <span className="font-body-sm text-body-sm text-on-surface-variant">ID: {conflict.conflict_id}</span>
              </div>
              <span className="px-3 py-1 bg-error-container text-on-error-container rounded font-label-caps text-label-caps font-bold">HIGH SEVERITY</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-outline-variant">
              {/* Source GR */}
              <div className="p-gutter flex flex-col bg-surface-container-lowest">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h4 className="font-label-caps text-label-caps text-on-surface-variant mb-1 uppercase tracking-wider">Source GR (Existing Policy)</h4>
                  </div>
                  <span className="material-symbols-outlined text-outline-variant">history_edu</span>
                </div>
                <div className="flex-1 space-y-4">
                  <div>
                    <div className="bg-surface-container-low border border-outline-variant p-4 rounded-lg font-document-text text-on-surface-variant italic leading-relaxed">
                      {conflict.old_policy}
                    </div>
                  </div>
                </div>
              </div>

              {/* Current Draft */}
              <div className="p-gutter flex flex-col bg-primary-container/5">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h4 className="font-label-caps text-label-caps text-primary mb-1 uppercase tracking-wider">Proposed Policy</h4>
                  </div>
                  <span className="material-symbols-outlined text-primary">edit_document</span>
                </div>
                <div className="flex-1 space-y-4">
                  <div>
                    <div className="bg-white border border-primary/20 p-4 rounded-lg font-document-text shadow-inner leading-relaxed">
                      {conflict.latest_policy}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* AI Reasoning Section */}
            <div className="bg-tertiary-container/10 border-t border-outline-variant p-gutter">
              <div className="flex gap-4">
                <div className="w-10 h-10 bg-tertiary text-white rounded-full flex items-center justify-center shrink-0">
                  <span className="material-symbols-outlined text-sm">psychology</span>
                </div>
                <div className="flex-1">
                  <div className="flex justify-between items-start mb-2">
                    <h5 className="font-body-md font-bold text-tertiary">AI Logic Explanation & Recommendation</h5>
                  </div>
                  <p className="text-body-md text-on-surface mb-4">
                    <span className="font-bold">Reason:</span> {conflict.reason}
                  </p>
                  <div className="bg-white p-3 rounded border border-tertiary-container flex items-center gap-3 mb-4">
                    <span className="material-symbols-outlined text-tertiary">lightbulb</span>
                    <p className="text-body-sm font-medium">{conflict.recommendation}</p>
                  </div>
                  
                  <div className="flex gap-4">
                    <label className={`flex-1 flex flex-col items-center p-4 border rounded cursor-pointer transition-colors ${decisions[conflict.conflict_id]?.selected_policy === 'old' ? 'border-primary bg-primary-container/5' : 'border-outline-variant hover:bg-surface-container-low'}`}>
                      <input 
                        type="radio" 
                        name={conflict.conflict_id} 
                        className="hidden"
                        onChange={() => handleDecisionChange(conflict.conflict_id, 'old')}
                      />
                      <span className={`material-symbols-outlined mb-2 ${decisions[conflict.conflict_id]?.selected_policy === 'old' ? 'text-primary' : 'text-on-surface-variant'}`}>history</span>
                      <span className="text-body-sm font-bold text-center">Retain Old Policy</span>
                    </label>
                    <label className={`flex-1 flex flex-col items-center p-4 border rounded cursor-pointer transition-colors ${decisions[conflict.conflict_id]?.selected_policy === 'latest' ? 'border-primary bg-primary-container/5' : 'border-outline-variant hover:bg-surface-container-low'}`}>
                      <input 
                        type="radio" 
                        name={conflict.conflict_id} 
                        className="hidden"
                        onChange={() => handleDecisionChange(conflict.conflict_id, 'latest')}
                      />
                      <span className={`material-symbols-outlined mb-2 ${decisions[conflict.conflict_id]?.selected_policy === 'latest' ? 'text-primary' : 'text-on-surface-variant'}`}>upgrade</span>
                      <span className="text-body-sm font-bold text-center">Apply Proposed</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Right Sidebar: Contextual Info */}
      <aside className="w-80 space-y-stack-md hidden xl:block">
        <div className="bg-primary/5 border border-primary/20 rounded-xl p-stack-md">
          <h4 className="font-label-caps text-label-caps text-primary border-b border-primary/10 pb-2 mb-4">VALIDATION STATUS</h4>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-body-sm">Pending Resolution</span>
              <span className="h-6 w-6 rounded-full bg-error text-white text-[10px] flex items-center justify-center font-bold">
                {conflicts.length - Object.keys(decisions).length}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-body-sm">Resolved</span>
              <span className="font-bold text-success">{Object.keys(decisions).length}</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Bottom Action Bar */}
      <div className="fixed bottom-0 right-0 left-64 bg-white border-t border-outline-variant px-gutter py-4 flex justify-between items-center z-40">
        <button onClick={() => navigate('/create')} className="flex items-center gap-2 px-6 py-2 border border-outline text-on-surface font-bold rounded-lg hover:bg-surface-container-low transition-colors">
          <span className="material-symbols-outlined">arrow_back</span>
          Back
        </button>
        <button
          onClick={handleGenerate}
          disabled={loading || Object.keys(decisions).length !== conflicts.length}
          className={`px-8 py-2 font-bold rounded-lg transition-all shadow-lg flex items-center gap-2 ${
            loading || Object.keys(decisions).length !== conflicts.length
              ? 'bg-outline-variant text-on-surface/40 cursor-not-allowed'
              : 'bg-primary text-white hover:bg-primary-container'
          }`}
        >
          {loading ? (
            <><span className="material-symbols-outlined animate-spin">sync</span> Drafting...</>
          ) : (
            <><span className="material-symbols-outlined">check_circle</span> Generate Final GR</>
          )}
        </button>
      </div>
    </div>
  );
}
