import React, { useState } from 'react';

const DocumentVerifier = () => {
  const [file, setFile] = useState(null);
  const [hash, setHash] = useState('');
  const [status, setStatus] = useState('idle'); // idle, hashing, verifying, valid, invalid
  const [docInfo, setDocInfo] = useState(null);
  const [error, setError] = useState('');

  const calculateHash = async (fileBuffer) => {
    const hashBuffer = await crypto.subtle.digest('SHA-256', fileBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex;
  };

  const handleFileUpload = async (event) => {
    const uploadedFile = event.target.files[0];
    if (!uploadedFile) return;

    setFile(uploadedFile);
    setStatus('hashing');
    setDocInfo(null);
    setError('');

    try {
      const arrayBuffer = await uploadedFile.arrayBuffer();
      const fileHash = await calculateHash(arrayBuffer);
      setHash(fileHash);
      
      setStatus('verifying');
      
      // Ping backend to check if hash exists in db
      const response = await fetch(`http://localhost:8000/api/verify/${fileHash}`);
      const data = await response.json();
      
      if (response.ok && data.status === 'success') {
        setStatus('valid');
        setDocInfo(data.verification);
      } else {
        setStatus('invalid');
        setError(data.detail || "Hash not found in official database.");
      }
    } catch (e) {
      console.error(e);
      setStatus('invalid');
      setError("Failed to verify document connection or read file.");
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8">
      <h1 className="text-3xl font-bold mb-2">Anti-Tamper Document Verifier</h1>
      <p className="text-gray-600 mb-8">Upload a physical PDF to instantly verify its cryptographic authenticity against the official government database.</p>

      <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
        <div className="border-2 border-dashed border-gray-300 rounded-xl p-12 text-center hover:bg-gray-50 transition-colors">
          <span className="material-symbols-outlined text-4xl text-gray-400 mb-4">upload_file</span>
          <h3 className="text-lg font-semibold mb-2">Drag and drop a PDF file here</h3>
          <p className="text-sm text-gray-500 mb-4">or click to browse from your computer</p>
          <input 
            type="file" 
            accept=".pdf" 
            onChange={handleFileUpload} 
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-white hover:file:bg-blue-700 cursor-pointer"
          />
        </div>

        {status !== 'idle' && (
          <div className="mt-8 border-t pt-8">
            <h4 className="font-bold text-gray-700 mb-4">Verification Results</h4>
            
            <div className="mb-4">
              <span className="text-sm font-bold text-gray-500">Calculated SHA-256 Hash:</span>
              <div className="bg-gray-100 p-3 rounded font-mono text-sm text-gray-800 break-all mt-1">
                {status === 'hashing' ? 'Calculating...' : hash}
              </div>
            </div>

            {status === 'verifying' && (
              <div className="flex items-center text-blue-600 font-bold p-4 bg-blue-50 rounded">
                <span className="material-symbols-outlined animate-spin mr-2">sync</span>
                Checking official ledger...
              </div>
            )}

            {status === 'valid' && docInfo && (
              <div className="p-6 bg-green-50 border-2 border-green-500 rounded-lg">
                <div className="flex items-center text-green-700 font-black text-xl mb-4">
                  <span className="material-symbols-outlined mr-2 text-3xl">verified</span>
                  AUTHENTIC & VERIFIED
                </div>
                <p className="text-green-800 mb-4 font-medium">This document perfectly matches the official digital record. It has not been tampered with.</p>
                
                <div className="bg-white p-4 rounded border border-green-200">
                  <h5 className="font-bold text-gray-800 mb-2 border-b pb-2">Document Details</h5>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div><span className="text-gray-500 block">GR Number:</span> <span className="font-bold">{docInfo.gr_number}</span></div>
                    <div><span className="text-gray-500 block">Department:</span> <span className="font-bold">{docInfo.department}</span></div>
                    <div><span className="text-gray-500 block">Status:</span> <span className="font-bold">{docInfo.current_status}</span></div>
                    <div><span className="text-gray-500 block">Date Generated:</span> <span className="font-bold">{new Date(docInfo.created_at).toLocaleString()}</span></div>
                    <div className="col-span-2"><span className="text-gray-500 block">Subject:</span> <span className="font-bold">{docInfo.subject}</span></div>
                  </div>
                </div>
              </div>
            )}

            {status === 'invalid' && (
              <div className="p-6 bg-red-50 border-2 border-red-500 rounded-lg">
                <div className="flex items-center text-red-700 font-black text-xl mb-2">
                  <span className="material-symbols-outlined mr-2 text-3xl">warning</span>
                  TAMPERED / UNVERIFIED
                </div>
                <p className="text-red-800 font-medium mb-2">This document failed mathematical verification.</p>
                <p className="text-sm text-red-600 bg-white p-3 rounded border border-red-200">Reason: {error}</p>
                <p className="text-sm text-gray-600 mt-4">Even a single extra space added to a PDF will change its mathematical hash and cause it to fail verification.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentVerifier;
