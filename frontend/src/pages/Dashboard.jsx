import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRagStats, getDraftHistory, getAvailableModels } from '../api/client';

export default function Dashboard({ userRole, llmProvider, setLlmProvider, llmModel, setLlmModel }) {
  const navigate = useNavigate();
  const [stats, setStats] = useState({ total_points_ingested: 0 });
  const [history, setHistory] = useState([]);
  const [availableModels, setAvailableModels] = useState([]);

  useEffect(() => {
    getRagStats()
      .then(data => {
        if (data.status === 'success') {
          setStats(data);
        }
      })
      .catch(console.error);

    getDraftHistory()
      .then(data => {
        if (data.status === 'success') {
          setHistory(data.history);
        }
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    // Fetch dynamic models when provider changes
    getAvailableModels(llmProvider)
      .then(data => {
        if (data.models) {
          setAvailableModels(data.models);
          // If current selected model is not in new list, reset it
          if (llmModel && !data.models.includes(llmModel)) {
              setLlmModel('');
          }
        }
      })
      .catch(console.error);
  }, [llmProvider]);

  return (
    <>
      {/* Welcome Banner */}
      <section className="relative overflow-hidden bg-primary-container text-on-primary rounded-xl p-8 flex flex-col md:flex-row items-center justify-between shadow-sm border border-outline-variant">
        <div className="z-10 max-w-2xl">
          <h2 className="font-h1 text-h1 mb-2 text-white">Achuk Nirnay, Pragat Maharashtra</h2>
          <p className="font-body-lg text-body-lg text-on-primary-container opacity-90 mb-6">
            Streamline Maharashtra Government Resolutions with AI-powered semantic alignment and conflict detection. Ensure legal consistency across all departments in real-time.
          </p>
          <div className="flex flex-wrap gap-4">
            {userRole === 'Desk Officer' && (
              <button onClick={() => navigate('/create')} className="bg-surface-container-lowest text-primary px-6 py-2.5 rounded-lg font-bold hover:bg-primary-fixed-dim transition-colors flex items-center gap-2">
                <span className="material-symbols-outlined">add</span>
                Create New GR
              </button>
            )}
            <button onClick={() => navigate('/chat')} className="border border-white text-white px-6 py-2.5 rounded-lg font-bold hover:bg-white/10 transition-colors flex items-center gap-2">
              <span className="material-symbols-outlined">gavel</span>
              Legal Chat
            </button>
          </div>
        </div>
      </section>


      {/* Bento Dashboard Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter mt-6">
        {/* Recently Generated & Drafts */}
        <div className="lg:col-span-8 space-y-gutter">
          <div className="bg-surface-container-lowest border border-outline-variant rounded-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-outline-variant flex justify-between items-center bg-surface-container-low">
              <h3 className="font-h3 text-h3">Recently Generated PDFs</h3>
              <a className="text-primary font-bold text-body-sm hover:underline" href="#">View All</a>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead className="bg-on-primary-fixed text-white font-label-caps text-[11px] uppercase tracking-wider">
                  <tr>
                    <th className="px-6 py-3">GR No</th>
                    <th className="px-6 py-3">Department</th>
                    <th className="px-6 py-3">Topic</th>
                    <th className="px-6 py-3 text-right">PDF</th>
                  </tr>
                </thead>
                <tbody className="text-body-sm divide-y divide-outline-variant">
                  {history.length > 0 ? (
                    history.map((gr, index) => (
                      <tr key={gr.id || index} className={`${index % 2 === 1 ? 'bg-surface-container-low ' : ''}hover:bg-surface-container-high transition-colors`}>
                        <td className="px-6 py-3 font-semibold text-primary">{gr.gr_number}</td>
                        <td className="px-6 py-3">{gr.department}</td>
                        <td className="px-6 py-3">{gr.subject}</td>
                        <td className="px-6 py-3 text-right">
                          <a href={`http://localhost:8080${gr.pdf_url || gr.pdf_path?.replace('./data/output', '/api/download')}?t=${Date.now()}`} target="_blank" rel="noreferrer" className="text-secondary hover:text-primary transition-colors inline-block">
                            <span className="material-symbols-outlined">picture_as_pdf</span>
                          </a>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4" className="px-6 py-6 text-center text-on-surface-variant">
                        No GRs generated yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Notifications & Actions Sidebar */}
        <div className="lg:col-span-4 space-y-gutter">
          {/* Quick Actions & Settings */}
          <div className="bg-surface-container-low border border-outline-variant rounded-lg p-6">
            <div className="flex flex-col gap-4 mb-4">
                <div className="flex justify-between items-center">
                    <h3 className="font-label-caps text-label-caps text-on-surface-variant uppercase">Quick Actions</h3>
                    {/* LLM Provider Toggle */}
                    <div className="flex items-center gap-2 bg-surface-container-lowest border border-outline-variant rounded-full p-1 text-xs">
                        <button 
                            onClick={() => setLlmProvider('groq')}
                            className={`px-3 py-1 rounded-full transition-colors ${llmProvider === 'groq' ? 'bg-primary text-white font-bold' : 'text-on-surface-variant hover:text-on-surface'}`}
                        >
                            Groq API
                        </button>
                        <button 
                            onClick={() => setLlmProvider('ollama')}
                            className={`px-3 py-1 rounded-full transition-colors ${llmProvider === 'ollama' ? 'bg-primary text-white font-bold' : 'text-on-surface-variant hover:text-on-surface'}`}
                        >
                            Local Ollama
                        </button>
                    </div>
                </div>
                
                {/* Dynamic Model Dropdown */}
                <div className="flex flex-col gap-2">
                    <label className="text-xs font-bold text-on-surface-variant">Select Model:</label>
                    <select 
                        value={llmModel} 
                        onChange={(e) => setLlmModel(e.target.value)}
                        className="bg-surface-container-lowest border border-outline-variant rounded-md p-2 text-sm focus:border-primary focus:outline-none"
                    >
                        <option value="">-- Default --</option>
                        {availableModels.map(model => (
                            <option key={model} value={model}>{model}</option>
                        ))}
                    </select>
                </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              {userRole === 'Desk Officer' && (
                <button onClick={() => navigate('/create')} className="flex flex-col items-center justify-center gap-2 p-4 bg-surface-container-lowest border border-outline-variant rounded-lg hover:border-primary hover:text-primary transition-all">
                  <span className="material-symbols-outlined">add_circle</span>
                  <span className="text-[11px] font-bold">New GR</span>
                </button>
              )}
              <button onClick={() => navigate('/chat')} className="flex flex-col items-center justify-center gap-2 p-4 bg-surface-container-lowest border border-outline-variant rounded-lg hover:border-primary hover:text-primary transition-all">
                <span className="material-symbols-outlined">auto_awesome</span>
                <span className="text-[11px] font-bold">AI Chat</span>
              </button>
            </div>
          </div>

          {/* Recent Notifications */}
          <div className="bg-surface-container-lowest border border-outline-variant rounded-lg overflow-hidden mt-6">
            <div className="px-6 py-4 border-b border-outline-variant bg-surface-container-low">
              <h3 className="font-h3 text-[16px]">Recent Notifications</h3>
            </div>
            <div className="divide-y divide-outline-variant">
              <div className="px-6 py-4 flex gap-4 hover:bg-surface-container-high transition-colors">
                <div className="w-2 h-2 rounded-full bg-primary mt-2"></div>
                <div className="flex-1">
                  <p className="text-body-sm font-semibold">New Policy Alignment Required</p>
                  <p className="text-[11px] text-on-surface-variant">General Administration Dept issued a new protocol.</p>
                  <p className="text-[10px] text-outline mt-1">10 mins ago</p>
                </div>
              </div>
              <div className="px-6 py-4 flex gap-4 hover:bg-surface-container-high transition-colors">
                <div className="w-2 h-2 rounded-full bg-error mt-2"></div>
                <div className="flex-1">
                  <p className="text-body-sm font-semibold text-error">Conflict Detected: GR-922</p>
                  <p className="text-[11px] text-on-surface-variant">Possible overlap with Agriculture Dept Resolution 2023.</p>
                  <p className="text-[10px] text-outline mt-1">1 hour ago</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
