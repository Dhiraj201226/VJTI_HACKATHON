import React, { useState, useEffect } from 'react';
import { getDraftHistory } from '../api/client';

export default function VersionControl() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterScore, setFilterScore] = useState('All');
  const [filterDept, setFilterDept] = useState('All');

  // 33 Official Maharashtra Government Departments
  const MAHA_DEPARTMENTS = [
    "General Administration Department",
    "Information Technology Department",
    "Home Department",
    "Revenue and Forest Department",
    "Agriculture, Animal Husbandry, Dairy Development and Fisheries Department",
    "School Education and Sports Department",
    "Higher and Technical Education Department",
    "Urban Development Department",
    "Public Works Department",
    "Water Resources Department",
    "Law and Judiciary Department",
    "Industries, Energy and Labour Department",
    "Rural Development and Panchayat Raj Department",
    "Food, Civil Supplies and Consumer Protection Department",
    "Planning Department",
    "Social Justice and Special Assistance Department",
    "Water Supply and Sanitation Department",
    "Housing Department",
    "Public Health Department",
    "Medical Education and Drugs Department",
    "Tribal Development Department",
    "Environment and Climate Change Department",
    "Co-operation, Marketing and Textiles Department",
    "Relief and Rehabilitation Department",
    "Women and Child Development Department",
    "Finance Department",
    "Marathi Bhasha Department",
    "Tourism and Cultural Affairs Department",
    "Minority Development Department",
    "Skill Development, Employment and Entrepreneurship Department",
    "Transport Department",
    "Parliamentary Affairs Department",
    "Soil and Water Conservation Department"
  ];

  useEffect(() => {
    getDraftHistory()
      .then(data => {
        if (data.status === 'success') {
          setHistory(data.history);
        }
        setLoading(false);
      })
      .catch(e => {
        console.error(e);
        setLoading(false);
      });
  }, []);

  const filteredHistory = history.filter(gr => {
    const score = gr.conflict_score || 0;
    
    // Score match
    let scoreMatch = true;
    if (filterScore === '0') scoreMatch = score === 0;
    if (filterScore === '1-40') scoreMatch = score > 0 && score <= 40;
    if (filterScore === '40+') scoreMatch = score > 40;
    
    // Dept match
    let deptMatch = true;
    if (filterDept !== 'All') {
      deptMatch = gr.department === filterDept;
    }

    return scoreMatch && deptMatch;
  });

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-6 flex flex-col gap-4">
        <h1 className="text-3xl font-bold">Chain of Custody / Version Control</h1>
        <div className="flex gap-4 items-center">
          <select 
            className="border rounded p-2 bg-white"
            value={filterDept}
            onChange={(e) => setFilterDept(e.target.value)}
          >
            <option value="All">All Departments</option>
            {MAHA_DEPARTMENTS.map(d => <option key={d} value={d}>{d}</option>)}
          </select>

          <select 
            className="border rounded p-2 bg-white"
            value={filterScore}
            onChange={(e) => setFilterScore(e.target.value)}
          >
            <option value="All">All Conflict Scores</option>
            <option value="0">Score: 0%</option>
            <option value="1-40">Score: 1-40%</option>
            <option value="40+">Score: &gt;40%</option>
          </select>
        </div>
      </div>
      
      {loading ? (
        <p>Loading audit logs...</p>
      ) : (
        <div className="space-y-6">
          {filteredHistory.length === 0 ? (
            <p className="text-gray-500">No GR history found matching the filters.</p>
          ) : (
            filteredHistory.map((gr, i) => (
              <div key={i} className="bg-white border rounded-lg shadow-sm p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h2 className="text-xl font-bold text-primary">{gr.gr_number || 'New GR'}</h2>
                    <p className="text-sm text-gray-600">{gr.department} | {gr.subject}</p>
                  </div>
                  <div className="flex gap-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                      gr.status === 'APPROVED' ? 'bg-green-100 text-green-800' : 
                      gr.status === 'REJECTED' ? 'bg-red-100 text-red-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {gr.status}
                    </span>
                    <span className="px-3 py-1 rounded-full text-xs font-bold bg-orange-100 text-orange-800">
                      Similarity Score: {gr.conflict_score || 0}%
                    </span>
                  </div>
                </div>
                
                <div className="border-l-2 border-gray-200 pl-4 space-y-4">
                  {/* Generation */}
                  <div className="relative">
                    <div className="absolute w-3 h-3 bg-gray-400 rounded-full -left-[1.35rem] top-1.5"></div>
                    <p className="text-sm font-bold">Draft Generated (Desk Officer)</p>
                    <p className="text-xs text-gray-500">{new Date(gr.created_at).toLocaleString()}</p>
                    {gr.desk_officer_notes && <p className="text-sm mt-1 bg-gray-50 p-2 rounded">{gr.desk_officer_notes}</p>}
                    {gr.current_hash && <p className="text-xs text-mono text-gray-400 mt-1">Hash: {gr.current_hash.substring(0, 16)}...</p>}
                  </div>

                  {/* Deputy Secy */}
                  {gr.deputy_secy_notes && (
                    <div className="relative">
                      <div className="absolute w-3 h-3 bg-blue-500 rounded-full -left-[1.35rem] top-1.5"></div>
                      <p className="text-sm font-bold text-blue-700">Deputy Secretary Action</p>
                      <p className="text-sm mt-1 bg-blue-50 p-2 rounded whitespace-pre-wrap">{gr.deputy_secy_notes}</p>
                    </div>
                  )}

                  {/* Secy */}
                  {gr.secy_notes && (
                    <div className="relative">
                      <div className="absolute w-3 h-3 bg-green-500 rounded-full -left-[1.35rem] top-1.5"></div>
                      <p className="text-sm font-bold text-green-700">Secretary Action</p>
                      <p className="text-sm mt-1 bg-green-50 p-2 rounded whitespace-pre-wrap">{gr.secy_notes}</p>
                    </div>
                  )}
                  
                  {/* Final Sealing */}
                  {gr.status === 'APPROVED' && gr.sha256_hash && (
                    <div className="relative mt-2">
                      <div className="absolute w-3 h-3 bg-green-600 rounded-full -left-[1.35rem] top-1.5"></div>
                      <p className="text-sm font-bold text-green-800">Final Seal & Cryptographic Hash</p>
                      <p className="text-xs font-mono text-green-600 bg-green-50 p-2 rounded break-all border border-green-200 mt-1">{gr.sha256_hash}</p>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
