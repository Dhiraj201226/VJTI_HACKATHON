import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './Layout';
import Dashboard from './pages/Dashboard';
import DraftingPortal from './pages/DraftingPortal';
import ConflictResolution from './pages/ConflictResolution';
import DocumentPreview from './pages/DocumentPreview';
import Chat from './pages/Chat';
import FAQ from './pages/FAQ';
import Login from './pages/Login';
import ApprovalQueue from './pages/ApprovalQueue';
import VerifyGR from './pages/VerifyGR';
import DocumentVerifier from './pages/DocumentVerifier';
import VersionControl from './pages/VersionControl';

function App() {
  const [draftState, setDraftState] = useState(() => {
    const saved = localStorage.getItem('draftState');
    return saved ? JSON.parse(saved) : {
      objective: '',
      conflicts: [],
      retrievedContext: null,
      finalResult: null,
    };
  });
  
  const [userRole, setUserRole] = useState(() => {
    return localStorage.getItem('userRole') || null;
  });

  useEffect(() => {
    localStorage.setItem('draftState', JSON.stringify(draftState));
  }, [draftState]);

  useEffect(() => {
    if (userRole) {
      localStorage.setItem('userRole', userRole);
    } else {
      localStorage.removeItem('userRole');
    }
  }, [userRole]);

  return (
    <BrowserRouter>
      {userRole ? (
        <Layout userRole={userRole} setUserRole={setUserRole}>
          <Routes>
            <Route path="/" element={<Dashboard userRole={userRole} />} />
            <Route path="/create" element={<DraftingPortal draftState={draftState} setDraftState={setDraftState} />} />
            <Route path="/conflicts" element={<ConflictResolution draftState={draftState} setDraftState={setDraftState} />} />
            <Route path="/result" element={<DocumentPreview draftState={draftState} />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/faq" element={<FAQ />} />
            <Route path="/queue" element={<ApprovalQueue userRole={userRole} />} />
            <Route path="/verify" element={<DocumentVerifier />} />
            <Route path="/versions" element={<VersionControl />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </Layout>
      ) : (
        <Routes>
          <Route path="/login" element={<Login setRole={setUserRole} />} />
          <Route path="/verify" element={
             <Layout userRole={null} setUserRole={setUserRole}>
               <VerifyGR />
             </Layout>
          } />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      )}
    </BrowserRouter>
  );
}
export default App;
