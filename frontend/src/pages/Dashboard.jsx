import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRagStats, getDraftHistory } from '../api/client';

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({ total_points_ingested: 0 });
  const [history, setHistory] = useState([]);

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

      {/* Quick Stats Grid */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-gutter mt-6">
        <div className="bg-surface-container-lowest border border-outline-variant p-stack-md rounded-lg flex flex-col gap-1">
          <div className="flex justify-between items-center mb-1">
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">Unique GRs Ingested</span>
            <span className="material-symbols-outlined text-primary">public</span>
          </div>
          <div className="font-h2 text-h2 text-on-surface">
            {stats.total_grs_processed ? stats.total_grs_processed.toLocaleString() : "0"}
          </div>
          <div className="text-body-sm text-green-600 flex items-center justify-between gap-1 mt-1">
            <span className="flex items-center gap-1">
              <span className="material-symbols-outlined text-[14px]">database</span>
              <span>{stats.total_points_ingested ? stats.total_points_ingested.toLocaleString() : "0"} chunks</span>
            </span>
            <span className="text-error flex items-center gap-1" title="Garbage files skipped by AI Classifier">
              <span className="material-symbols-outlined text-[14px]">delete</span>
              <span>{stats.total_grs_skipped_by_ai ? stats.total_grs_skipped_by_ai.toLocaleString() : "0"} skipped</span>
            </span>
          </div>
        </div>
        <div className="bg-surface-container-lowest border border-outline-variant p-stack-md rounded-lg flex flex-col gap-1">
          <div className="flex justify-between items-center mb-1">
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">Drafts in Progress</span>
            <span className="material-symbols-outlined text-secondary">edit_note</span>
          </div>
          <div className="font-h2 text-h2 text-on-surface">3</div>
          <div className="text-body-sm text-on-surface-variant">Modified today</div>
        </div>
        <div className="bg-surface-container-lowest border border-outline-variant p-stack-md rounded-lg flex flex-col gap-1">
          <div className="flex justify-between items-center mb-1">
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">Pending Review</span>
            <span className="material-symbols-outlined text-amber-600">pending_actions</span>
          </div>
          <div className="font-h2 text-h2 text-on-surface">1</div>
          <div className="text-body-sm text-amber-600 flex items-center gap-1">
            <span>Awaiting signature</span>
          </div>
        </div>
        <div className="bg-surface-container-lowest border border-outline-variant p-stack-md rounded-lg flex flex-col gap-1">
          <div className="flex justify-between items-center mb-1">
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">Conflicts Prevented</span>
            <span className="material-symbols-outlined text-error">shield</span>
          </div>
          <div className="font-h2 text-h2 text-on-surface">14</div>
          <div className="text-body-sm text-on-surface-variant">AI Auto-resolved</div>
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
                          <a href={`http://localhost:8000${gr.pdf_url || gr.pdf_path?.replace('./data/output', '/api/download')}?t=${Date.now()}`} target="_blank" rel="noreferrer" className="text-secondary hover:text-primary transition-colors inline-block">
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
          {/* Quick Actions */}
          <div className="bg-surface-container-low border border-outline-variant rounded-lg p-6">
            <h3 className="font-label-caps text-label-caps text-on-surface-variant uppercase mb-4">Quick Actions</h3>
            <div className="grid grid-cols-2 gap-3">
              <button onClick={() => navigate('/create')} className="flex flex-col items-center justify-center gap-2 p-4 bg-surface-container-lowest border border-outline-variant rounded-lg hover:border-primary hover:text-primary transition-all">
                <span className="material-symbols-outlined">add_circle</span>
                <span className="text-[11px] font-bold">New GR</span>
              </button>
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
