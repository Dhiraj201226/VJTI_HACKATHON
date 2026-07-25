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
        // If no conflicts, we could auto-generate, but let's go straight to generation from here
        // We'll skip to conflicts page with 0 conflicts to just hit "Generate"
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
    <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 border-b pb-4">New Government Resolution</h2>
      <div className="mb-6">
        <label className="block text-gray-700 font-semibold mb-2" htmlFor="objective">
          Policy Objective
        </label>
        <p className="text-sm text-gray-500 mb-4">
          Provide the objective for the new GR. The AI will retrieve relevant policies, detect conflicts, and draft the document automatically.
        </p>
        <textarea
          id="objective"
          rows="6"
          className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-shadow resize-none"
          placeholder="e.g., Establish AI Labs in Government Engineering Colleges."
          value={objective}
          onChange={(e) => setObjective(e.target.value)}
        ></textarea>
      </div>
      
      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6 border border-red-200">
          {error}
        </div>
      )}

      <div className="flex justify-end">
        <button
          onClick={handleInitiate}
          disabled={loading || !objective.trim()}
          className={`flex items-center gap-2 px-8 py-3 rounded-lg font-bold text-white transition-all shadow-md ${
            loading || !objective.trim()
              ? 'bg-blue-400 cursor-not-allowed'
              : 'bg-blue-700 hover:bg-blue-800 hover:shadow-lg'
          }`}
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </>
          ) : (
            'Retrieve Context & Analyze'
          )}
        </button>
      </div>
    </div>
  );
}
