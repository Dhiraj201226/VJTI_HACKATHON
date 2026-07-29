import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import Dashboard from './pages/Dashboard';
import DraftingPortal from './pages/DraftingPortal';
import ConflictResolution from './pages/ConflictResolution';
import DocumentPreview from './pages/DocumentPreview';
import Chat from './pages/Chat';
import FAQ from './pages/FAQ';

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
          <Route path="/" element={<Dashboard />} />
          <Route path="/create" element={<DraftingPortal draftState={draftState} setDraftState={setDraftState} />} />
          <Route path="/conflicts" element={<ConflictResolution draftState={draftState} setDraftState={setDraftState} />} />
          <Route path="/result" element={<DocumentPreview draftState={draftState} />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/faq" element={<FAQ />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
export default App;
