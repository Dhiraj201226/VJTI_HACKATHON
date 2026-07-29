import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getRagStats } from '../api/client';

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({ total_points_ingested: 0 });

  useEffect(() => {
    getRagStats()
      .then(data => {
        if (data.status === 'success') {
          setStats(data);
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
            <button onClick={() => navigate('/create')} className="bg-surface-container-lowest text-primary px-6 py-2.5 rounded-lg font-bold hover:bg-primary-fixed-dim transition-colors flex items-center gap-2">
              <span className="material-symbols-outlined">add</span>
              Create New GR
            </button>
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
            <span className="font-label-caps text-label-caps text-on-surface-variant uppercase">Total GRs Ingested</span>
            <span className="material-symbols-outlined text-primary">public</span>
          </div>
          <div className="font-h2 text-h2 text-on-surface">{stats.total_points_ingested.toLocaleString()}</div>
          <div className="text-body-sm text-green-600 flex items-center gap-1">
            <span className="material-symbols-outlined text-[14px]">check_circle</span>
            <span>Qdrant DB Active</span>
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
                    <th className="px-6 py-3">Document Title</th>
                    <th className="px-6 py-3">Department</th>
                    <th className="px-6 py-3">Generated Date</th>
                    <th className="px-6 py-3">Action</th>
                  </tr>
                </thead>
                <tbody className="text-body-sm divide-y divide-outline-variant">
                  <tr className="hover:bg-surface-container-high transition-colors">
                    <td className="px-6 py-3 font-semibold text-primary">GR-IT-2024-045.pdf</td>
                    <td className="px-6 py-3">IT &amp; Communication</td>
                    <td className="px-6 py-3">2 hours ago</td>
                    <td className="px-6 py-3">
                      <button className="text-secondary hover:text-primary transition-colors">
                        <span className="material-symbols-outlined">download</span>
                      </button>
                    </td>
                  </tr>
                  <tr className="bg-surface-container-low hover:bg-surface-container-high transition-colors">
                    <td className="px-6 py-3 font-semibold text-primary">GR-EDU-SCHEME-11.pdf</td>
                    <td className="px-6 py-3">School Education</td>
                    <td className="px-6 py-3">Yesterday</td>
                    <td className="px-6 py-3">
                      <button className="text-secondary hover:text-primary transition-colors">
                        <span className="material-symbols-outlined">download</span>
                      </button>
                    </td>
                  </tr>
                  <tr className="hover:bg-surface-container-high transition-colors">
                    <td className="px-6 py-3 font-semibold text-primary">GR-FIN-BUDGET-92.pdf</td>
                    <td className="px-6 py-3">Finance Department</td>
                    <td className="px-6 py-3">Nov 18, 2024</td>
                    <td className="px-6 py-3">
                      <button className="text-secondary hover:text-primary transition-colors">
                        <span className="material-symbols-outlined">download</span>
                      </button>
                    </td>
                  </tr>
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
