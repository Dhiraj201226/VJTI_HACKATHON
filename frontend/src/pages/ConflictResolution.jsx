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

  // If no conflicts, just show a generate button
  if (conflicts.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100 text-center">
        <div className="text-green-500 mb-4">
          <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-800 mb-2">No Conflicts Detected</h2>
        <p className="text-gray-600 mb-8">The AI found relevant context and is ready to generate the GR.</p>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="bg-blue-700 hover:bg-blue-800 text-white font-bold py-3 px-8 rounded-lg shadow-md transition-all"
        >
          {loading ? 'Drafting Resolution...' : 'Generate Document'}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-yellow-50 border-l-4 border-yellow-500 p-6 rounded-r-lg shadow-sm">
        <h2 className="text-2xl font-bold text-yellow-800 mb-2">Policy Conflicts Detected</h2>
        <p className="text-yellow-700">Please review the conflicting policies below and confirm the correct resolution before generating the document.</p>
      </div>

      {conflicts.map((conflict) => (
        <div key={conflict.conflict_id} className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
          <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
            <h3 className="font-bold text-gray-800 text-lg">Conflict: {conflict.conflict_id}</h3>
          </div>
          <div className="p-6">
            <div className="grid md:grid-cols-2 gap-6 mb-6">
              <div className="bg-red-50 p-4 rounded-lg border border-red-100">
                <div className="text-sm font-bold text-red-800 mb-2 uppercase tracking-wide">Old Policy</div>
                <p className="text-gray-700">{conflict.old_policy}</p>
                <div className="mt-4">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input 
                      type="radio" 
                      name={conflict.conflict_id} 
                      className="form-radio text-blue-600 w-5 h-5"
                      onChange={() => handleDecisionChange(conflict.conflict_id, 'old')}
                    />
                    <span className="font-medium text-gray-800">Retain Old Policy</span>
                  </label>
                </div>
              </div>
              <div className="bg-green-50 p-4 rounded-lg border border-green-100">
                <div className="text-sm font-bold text-green-800 mb-2 uppercase tracking-wide">Latest Policy</div>
                <p className="text-gray-700">{conflict.latest_policy}</p>
                <div className="mt-4">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input 
                      type="radio" 
                      name={conflict.conflict_id} 
                      className="form-radio text-blue-600 w-5 h-5"
                      onChange={() => handleDecisionChange(conflict.conflict_id, 'latest')}
                    />
                    <span className="font-medium text-gray-800">Apply Latest Policy</span>
                  </label>
                </div>
              </div>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
              <div className="font-bold text-blue-800 mb-1">AI Analysis</div>
              <p className="text-gray-700 mb-2"><span className="font-semibold">Reason:</span> {conflict.reason}</p>
              <p className="text-gray-700"><span className="font-semibold">Recommendation:</span> {conflict.recommendation}</p>
            </div>
          </div>
        </div>
      ))}

      <div className="flex justify-between items-center bg-white p-6 rounded-xl shadow-lg border border-gray-100">
        <button 
          onClick={() => navigate('/')}
          className="text-gray-600 hover:text-gray-800 font-medium px-4 py-2"
        >
          &larr; Back to Draft
        </button>
        <button
          onClick={handleGenerate}
          disabled={loading || Object.keys(decisions).length !== conflicts.length}
          className={`px-8 py-3 rounded-lg font-bold text-white transition-all shadow-md ${
            loading || Object.keys(decisions).length !== conflicts.length
              ? 'bg-blue-400 cursor-not-allowed'
              : 'bg-blue-700 hover:bg-blue-800 hover:shadow-lg'
          }`}
        >
          {loading ? 'Drafting Document...' : 'Confirm & Generate GR'}
        </button>
      </div>
    </div>
  );
}
