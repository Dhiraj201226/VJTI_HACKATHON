import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function DocumentPreview({ draftState }) {
  const navigate = useNavigate();
  const { finalResult } = draftState;

  if (!finalResult) {
    return (
      <div className="text-center mt-10">
        <p className="text-xl text-gray-600 mb-4">No document generated yet.</p>
        <button onClick={() => navigate('/')} className="text-blue-600 underline">Go back</button>
      </div>
    );
  }

  const { json_data, docx_url, pdf_url } = finalResult;
  const fields = json_data.template_fields;
  const baseUrl = "http://localhost:8000"; // Should be env var

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
        <div className="flex justify-between items-start mb-8 border-b pb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Document Generated Successfully</h2>
            <p className="text-gray-600">The AI has drafted the Government Resolution based on your objective.</p>
          </div>
          <div className="flex gap-4">
            <a 
              href={`${baseUrl}${docx_url}`} 
              download
              className="flex items-center gap-2 bg-blue-100 text-blue-700 hover:bg-blue-200 px-4 py-2 rounded-lg font-semibold transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
              Download DOCX
            </a>
            <a 
              href={`${baseUrl}${pdf_url}`} 
              download
              className="flex items-center gap-2 bg-red-100 text-red-700 hover:bg-red-200 px-4 py-2 rounded-lg font-semibold transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
              Download PDF
            </a>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Preview Panel */}
          <div className="md:col-span-2 bg-gray-50 p-8 rounded-lg border border-gray-200 shadow-inner font-serif">
            <div className="text-center mb-6">
              <h1 className="font-bold text-xl uppercase underline">GOVERNMENT OF MAHARASHTRA</h1>
              <p className="mt-2 font-semibold">Department: {fields.department}</p>
              <p>Government Resolution No.: {fields.gr_number}</p>
              <p>Date: {fields.date}</p>
            </div>
            
            <div className="mb-6">
              <h2 className="font-bold underline mb-2">Subject:</h2>
              <p className="pl-4">{fields.subject}</p>
            </div>
            
            <div className="mb-6">
              <h2 className="font-bold underline mb-2">References:</h2>
              <ul className="list-disc pl-8">
                {fields.references.map((ref, idx) => (
                  <li key={idx} className="mb-1">{ref}</li>
                ))}
              </ul>
            </div>
            
            <div className="mb-6">
              <h2 className="font-bold underline mb-2">Resolution:</h2>
              {fields.body.map((para, idx) => (
                <p key={idx} className="mb-3 text-justify indent-8">{para}</p>
              ))}
            </div>
            
            <div className="mb-6">
              <h2 className="font-bold underline mb-2">Clauses:</h2>
              {fields.clauses.map((clause, idx) => (
                <p key={idx} className="mb-3 pl-4">{clause}</p>
              ))}
            </div>
            
            <div className="mb-6">
              <h2 className="font-bold underline mb-2">Financial Implications:</h2>
              <p className="pl-4">{fields.financial_implications}</p>
            </div>
            
            <div className="mt-12 text-right">
              <p>By order and in the name of the Governor of Maharashtra,</p>
              <br/><br/>
              <p className="font-bold">{fields.signature}</p>
              <p>{fields.designation}</p>
            </div>
          </div>
          
          {/* Metadata Panel */}
          <div className="space-y-6">
            <div className="bg-blue-50 p-6 rounded-lg border border-blue-100">
              <h3 className="font-bold text-blue-900 mb-4 border-b border-blue-200 pb-2">AI Extraction Metadata</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <span className="font-semibold text-blue-800 block">Identified References:</span>
                  <span className="text-gray-700">{json_data.references.length} documents linked</span>
                </div>
                <div>
                  <span className="font-semibold text-blue-800 block">Conflicts Resolved:</span>
                  <span className="text-gray-700">{json_data.conflicts.length} policies aligned</span>
                </div>
              </div>
            </div>
            
            <button 
              onClick={() => navigate('/')}
              className="w-full bg-gray-800 hover:bg-gray-900 text-white font-bold py-3 px-4 rounded-lg transition-colors text-center"
            >
              Start New Draft
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
