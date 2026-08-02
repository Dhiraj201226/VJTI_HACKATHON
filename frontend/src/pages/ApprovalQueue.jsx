import React, { useState, useEffect } from 'react';
import { getDraftHistory } from '../api/client';

const ApprovalQueue = ({ userRole }) => {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [selectedGR, setSelectedGR] = useState(null);
  
  // Editing state
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState(null);
  const [notes, setNotes] = useState('');

  useEffect(() => {
    fetchQueue();
  }, [userRole]);

  const fetchQueue = async () => {
    try {
      const response = await getDraftHistory();
      let filtered = [];
      if (userRole === 'Deputy Secretary') {
        filtered = response.history.filter(gr => gr.status === 'PENDING_DS_REVIEW');
      } else if (userRole === 'Secretary') {
        filtered = response.history.filter(gr => gr.status === 'PENDING_SEC_APPROVAL');
      }
      setQueue(filtered);
      setErrorMsg(null);
    } catch (error) {
      console.error("Error fetching queue:", error);
      setErrorMsg(error.message || String(error));
    } finally {
      setLoading(false);
    }
  };

  const handleSelectGR = (gr) => {
    setSelectedGR(gr);
    setNotes('');
    setIsEditing(false);
    if (gr.draft_json) {
      try {
        const parsed = JSON.parse(gr.draft_json);
        setEditForm({
          subject: parsed.template_fields?.subject || '',
          body: parsed.template_fields?.body?.join('\n\n') || '',
          clauses: parsed.template_fields?.clauses?.join('\n\n') || '',
          financial_implications: parsed.template_fields?.financial_implications || ''
        });
      } catch (e) {
        console.error("Failed to parse draft_json", e);
      }
    }
  };

  const handleSaveEdit = async () => {
    if (!editForm) return;
    try {
      // Reconstruct full JSON
      const parsed = JSON.parse(selectedGR.draft_json);
      parsed.template_fields.subject = editForm.subject;
      parsed.template_fields.body = editForm.body.split('\n\n');
      parsed.template_fields.clauses = editForm.clauses.split('\n\n');
      parsed.template_fields.financial_implications = editForm.financial_implications;

      await fetch(`http://localhost:8080/api/draft/${selectedGR.id}/edit`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          draft_json: JSON.stringify(parsed),
          author_role: userRole,
          notes: notes || "Minor text corrections."
        })
      });
      alert('Draft Regenerated & Hash Updated!');
      setIsEditing(false);
      fetchQueue();
      setSelectedGR(null); // Return to queue to re-fetch PDF
    } catch (e) {
      alert("Error saving edits");
    }
  };

  const handleAction = async () => {
    try {
      if (userRole === 'Deputy Secretary') {
        await fetch(`http://localhost:8080/api/draft/${selectedGR.id}/review`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ notes })
        });
        alert('Forwarded to Secretary');
      } else if (userRole === 'Secretary') {
        await fetch(`http://localhost:8080/api/draft/${selectedGR.id}/approve`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ notes })
        });
        alert('GR Approved, Sealed, and SHA-256 Hashed!');
      }
      setSelectedGR(null);
      setNotes('');
      fetchQueue();
    } catch (e) {
      alert("Error taking action");
    }
  };

  if (loading) return <div className="text-center py-10">Loading queue...</div>;

  return (
    <div className="max-w-7xl mx-auto py-6 space-y-6">
      <h1 className="text-2xl font-bold">
        {userRole === 'Deputy Secretary' ? 'Legal & Financial Clearance Queue' : 'Final Approval Queue'}
      </h1>

      {selectedGR ? (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <button onClick={() => setSelectedGR(null)} className="text-blue-600">&larr; Back to Queue</button>
            <div className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded text-sm font-mono font-bold">
              Current Hash: {selectedGR.current_hash ? selectedGR.current_hash.substring(0, 12) + '...' : 'Pending'}
            </div>
          </div>
          
          <h2 className="text-xl font-bold mb-4">Review GR: {selectedGR.gr_number}</h2>
          
          {selectedGR.ds_notes && (
            <div className="mb-4 p-4 bg-blue-50 border-l-4 border-blue-500 rounded text-sm text-blue-800 whitespace-pre-wrap">
              <strong>Prior Remarks / Edits log:</strong>
              <br/>{selectedGR.ds_notes}
            </div>
          )}

          <div className="bg-gray-50 p-4 rounded mb-4">
            <p><strong>Department:</strong> {selectedGR.department}</p>
            <p><strong>Subject:</strong> {selectedGR.subject}</p>
            <p className="mt-2 text-sm">
              <a href={`http://localhost:8080${selectedGR.pdf_url}`} target="_blank" rel="noreferrer" className="text-blue-600 underline font-bold">
                View Current Draft PDF
              </a>
            </p>
          </div>
          
          {isEditing && editForm ? (
            <div className="space-y-4 border p-4 rounded bg-white shadow-inner mb-4">
              <h3 className="font-bold text-lg text-primary">Edit Document Text</h3>
              <div>
                <label className="block text-sm font-medium text-gray-700">Subject</label>
                <input type="text" className="w-full border p-2 rounded" value={editForm.subject} onChange={e => setEditForm({...editForm, subject: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Resolution Body</label>
                <textarea className="w-full border p-2 rounded" rows="5" value={editForm.body} onChange={e => setEditForm({...editForm, body: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Clauses</label>
                <textarea className="w-full border p-2 rounded" rows="4" value={editForm.clauses} onChange={e => setEditForm({...editForm, clauses: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Financial Implications</label>
                <textarea className="w-full border p-2 rounded" rows="3" value={editForm.financial_implications} onChange={e => setEditForm({...editForm, financial_implications: e.target.value})} />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 text-error">Mandatory Change Remark</label>
                <input type="text" className="w-full border-error border p-2 rounded" placeholder="E.g., Removed 77 hectare restriction" value={notes} onChange={e => setNotes(e.target.value)} />
              </div>
              <div className="flex gap-2">
                <button onClick={handleSaveEdit} className="bg-primary text-white px-4 py-2 rounded font-bold hover:bg-blue-700">Save & Update Hash</button>
                <button onClick={() => setIsEditing(false)} className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400">Cancel Edit</button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex gap-2 mb-4">
                <button onClick={() => setIsEditing(true)} className="bg-amber-100 text-amber-700 px-4 py-2 rounded font-medium hover:bg-amber-200 border border-amber-300 flex items-center gap-2">
                  <span className="material-symbols-outlined text-sm">edit</span> Edit Text & Regenerate
                </button>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Add Approval/Clearance Note</label>
                <textarea 
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm p-2 border" 
                  rows="3" 
                  placeholder="Enter official notes before forwarding/approving..."
                ></textarea>
              </div>
              <button 
                onClick={handleAction}
                className="bg-green-600 text-white px-4 py-2 rounded font-bold hover:bg-green-700"
              >
                {userRole === 'Deputy Secretary' ? 'Clear & Forward to Secretary' : 'Approve & Seal GR'}
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {errorMsg && (
            <div className="p-4 bg-red-50 text-red-700 border-b border-red-200">
              <strong>Error:</strong> {errorMsg}
            </div>
          )}
          {queue.length === 0 ? (
            <p className="p-6 text-gray-500">No GRs pending your review.</p>
          ) : (
            <ul className="divide-y divide-gray-200">
              {queue.map(gr => (
                <li key={gr.id} className="p-6 hover:bg-gray-50 flex justify-between items-center">
                  <div>
                    <h3 className="font-bold text-gray-900">{gr.subject}</h3>
                    <p className="text-sm text-gray-500">GR No: {gr.gr_number} | Dept: {gr.department}</p>
                    {gr.current_hash && <p className="text-xs text-blue-500 font-mono mt-1">Hash: {gr.current_hash.substring(0, 8)}...</p>}
                  </div>
                  <button 
                    onClick={() => handleSelectGR(gr)}
                    className="bg-blue-50 text-blue-600 px-4 py-2 rounded font-medium hover:bg-blue-100"
                  >
                    Review
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
};

export default ApprovalQueue;
