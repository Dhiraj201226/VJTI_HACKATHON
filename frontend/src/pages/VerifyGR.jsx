import React, { useState } from 'react';
import { ShieldCheckIcon, DocumentCheckIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const VerifyGR = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setResult(null);
    }
  };

  const handleVerify = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('http://localhost:8000/api/draft/verify', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      setResult(data);
    } catch (e) {
      console.error(e);
      setResult({ status: 'error', message: 'Verification service unreachable.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-10">
      <div className="text-center mb-10">
        <ShieldCheckIcon className="w-16 h-16 text-blue-600 mx-auto mb-4" />
        <h1 className="text-3xl font-bold text-gray-900">Public GR Verification Portal</h1>
        <p className="mt-2 text-gray-600">Upload a Government Resolution PDF to instantly verify its cryptographic authenticity.</p>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-10 text-center">
          <input 
            type="file" 
            accept=".pdf" 
            onChange={handleFileChange} 
            className="hidden" 
            id="gr-upload" 
          />
          <label 
            htmlFor="gr-upload" 
            className="cursor-pointer bg-gray-50 text-gray-700 px-6 py-3 rounded-md font-medium hover:bg-gray-100 inline-block mb-4"
          >
            Select PDF File
          </label>
          <p className="text-sm text-gray-500">
            {file ? `Selected: ${file.name}` : "or drag and drop here"}
          </p>
        </div>

        <div className="mt-6 text-center">
          <button 
            onClick={handleVerify}
            disabled={!file || loading}
            className={`px-8 py-3 rounded-full font-bold text-white transition-colors ${!file ? 'bg-gray-300' : 'bg-blue-600 hover:bg-blue-700'}`}
          >
            {loading ? 'Verifying...' : 'Verify Authenticity'}
          </button>
        </div>
      </div>

      {result && (
        <div className={`mt-8 p-6 rounded-lg border-2 ${result.status === 'authentic' ? 'border-green-500 bg-green-50' : 'border-red-500 bg-red-50'}`}>
          <div className="flex items-start">
            <div className="flex-shrink-0 mt-1">
              {result.status === 'authentic' ? (
                <DocumentCheckIcon className="h-8 w-8 text-green-600" />
              ) : (
                <ExclamationTriangleIcon className="h-8 w-8 text-red-600" />
              )}
            </div>
            <div className="ml-4">
              <h3 className={`text-xl font-bold ${result.status === 'authentic' ? 'text-green-800' : 'text-red-800'}`}>
                {result.status === 'authentic' ? 'AUTHENTIC DOCUMENT' : 'WARNING: TAMPERED OR FAKE DOCUMENT'}
              </h3>
              <p className={`mt-1 font-medium ${result.status === 'authentic' ? 'text-green-700' : 'text-red-700'}`}>
                {result.message}
              </p>
              
              {result.status === 'authentic' && (
                <div className="mt-4 bg-white bg-opacity-50 p-4 rounded text-sm text-gray-800">
                  <p><strong>GR Number:</strong> {result.gr_number}</p>
                  <p><strong>Department:</strong> {result.department}</p>
                  <p><strong>Subject:</strong> {result.subject}</p>
                  <p><strong>Date Issued:</strong> {result.date}</p>
                  <p className="mt-2 text-xs text-green-600 font-mono flex items-center gap-1">
                    <ShieldCheckIcon className="w-3 h-3"/> SHA-256 Signature Verified
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VerifyGR;
