import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import DraftingPortal from './pages/DraftingPortal';
import ConflictResolution from './pages/ConflictResolution';
import DocumentPreview from './pages/DocumentPreview';

function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col font-sans">
      <header className="bg-blue-900 text-white p-4 shadow-md flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-yellow-500 w-10 h-10 rounded-full flex items-center justify-center font-bold text-blue-900">
            MH
          </div>
          <h1 className="text-xl font-bold tracking-wide">MAHA-GR ALIGN</h1>
        </div>
        <div className="text-sm font-medium opacity-80">Government Resolution Drafting System</div>
      </header>
      <main className="flex-1 p-6 bg-gray-50 flex justify-center">
        <div className="w-full max-w-5xl">
          {children}
        </div>
      </main>
      <footer className="bg-gray-800 text-gray-300 text-center p-4 text-sm">
        &copy; 2026 Government of Maharashtra. All rights reserved.
      </footer>
    </div>
  );
}

function App() {
  const [draftState, setDraftState] = useState({
    objective: '',
    conflicts: [],
    retrievedContext: null,
    finalResult: null,
  });

  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<DraftingPortal draftState={draftState} setDraftState={setDraftState} />} />
          <Route path="/conflicts" element={<ConflictResolution draftState={draftState} setDraftState={setDraftState} />} />
          <Route path="/result" element={<DocumentPreview draftState={draftState} />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
