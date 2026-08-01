import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Layout({ children, userRole, setUserRole }) {
  const navigate = useNavigate();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleLogout = () => {
    setUserRole(null);
    setIsDropdownOpen(false);
    navigate('/login');
  };

  return (
    <div className="bg-background text-on-surface font-body-md overflow-x-hidden min-h-screen" onClick={() => setIsDropdownOpen(false)}>
      {/* Sidebar Navigation */}
      <aside className="hidden md:flex h-screen w-64 fixed left-0 top-0 bg-surface-container-low border-r border-outline-variant flex-col py-stack-md z-50">
        <div className="px-gutter mb-stack-lg">
          <div className="flex items-center gap-3 mb-6 cursor-pointer" onClick={() => navigate('/')}>
            <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuCDxUvkd8dDo2JpklHyR51sfeGWl9l71qfjFQhi9HdvffeZ9iLV0UYE3giDfdpsVpNGvumpdng4phCOMTwj8_SLVJ7xLEC-PFBJbYwpYpz0YJBpP-ahSse85CRK6pFZlCSJOawKUxx_w3DUW8jdhc9TmFJkmhHTbmhA3FhxxF_k8wUdHUUsB1eop1sme4_ZMbX5JxdlAGENBhzohL8xoEHiGffLjvzcdY5LXqmKztSZcISrgWbHO6M95dK1qNyTTJRmfg" alt="Emblem" className="w-12 h-12 object-contain" />
            <div>
              <h2 className="font-h3 text-[16px] leading-tight text-on-surface font-bold">Govt of Maharashtra</h2>
              <p className="font-body-sm text-body-sm text-on-surface-variant">e-Governance Cell</p>
            </div>
          </div>
        </div>
        <nav className="flex-1 sidebar-scroll overflow-y-auto">
          <ul className="space-y-1">
            <li>
              <button onClick={() => navigate('/')} className="w-full flex items-center gap-3 px-gutter py-3 bg-primary-container text-on-primary-container border-r-4 border-primary font-semibold transition-transform active:scale-95">
                <span className="material-symbols-outlined">dashboard</span>
                <span className="font-body-sm text-body-sm">Dashboard</span>
              </button>
            </li>
            {userRole === 'Desk Officer' && (
              <li>
                <button onClick={() => navigate('/create')} className="w-full flex items-center gap-3 px-gutter py-3 text-on-surface-variant hover:bg-surface-container-high transition-all active:scale-95">
                  <span className="material-symbols-outlined">add_circle</span>
                  <span className="font-body-sm text-body-sm">Create New GR</span>
                </button>
              </li>
            )}
            <li>
              <button onClick={() => navigate('/conflicts')} className="w-full flex items-center gap-3 px-gutter py-3 text-on-surface-variant hover:bg-surface-container-high transition-all active:scale-95">
                <span className="material-symbols-outlined">rule</span>
                <span className="font-body-sm text-body-sm">Conflict Detection</span>
              </button>
            </li>
            {(userRole === 'Deputy Secretary' || userRole === 'Secretary') && (
              <li>
                <button onClick={() => navigate('/queue')} className="w-full flex items-center gap-3 px-gutter py-3 text-on-surface-variant hover:bg-surface-container-high transition-all active:scale-95">
                  <span className="material-symbols-outlined">pending_actions</span>
                  <span className="font-body-sm text-body-sm">
                    {userRole === 'Secretary' ? 'Finalize GR' : 'Approval Queue'}
                  </span>
                </button>
              </li>
            )}
            <li>
              <button onClick={() => navigate('/chat')} className="w-full flex items-center gap-3 px-gutter py-3 text-on-surface-variant hover:bg-surface-container-high transition-all active:scale-95">
                <span className="material-symbols-outlined">gavel</span>
                <span className="font-body-sm text-body-sm">AI Legal Advisor</span>
              </button>
            </li>
            <li>
              <button onClick={() => navigate('/faq')} className="w-full flex items-center gap-3 px-gutter py-3 text-on-surface-variant hover:bg-surface-container-high transition-all active:scale-95">
                <span className="material-symbols-outlined">help</span>
                <span className="font-body-sm text-body-sm">FAQ / Help</span>
              </button>
            </li>
            <li>
              <button onClick={() => navigate('/verify')} className="w-full flex items-center gap-3 px-gutter py-3 text-on-surface-variant hover:bg-surface-container-high transition-all active:scale-95">
                <span className="material-symbols-outlined">verified</span>
                <span className="font-body-sm text-body-sm">Verify Authenticity</span>
              </button>
            </li>
          </ul>
        </nav>
        <div className="px-gutter pt-stack-md border-t border-outline-variant">
          <button className="w-full flex items-center gap-3 py-2 text-on-surface-variant hover:bg-surface-container-high transition-all">
            <span className="material-symbols-outlined">settings</span>
            <span className="font-body-sm text-body-sm">Settings</span>
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="md:ml-64 flex flex-col min-h-screen">
        {/* Top Navigation Bar */}
        <header className="bg-surface-container-highest flex justify-between items-center px-gutter py-stack-sm w-full border-b border-outline-variant sticky top-0 z-40">
          <div className="flex items-center gap-stack-lg">
            <h1 className="font-h2 text-h2 font-bold tracking-tight text-primary">MAHA-GR ALIGN</h1>
          </div>
          <div className="flex items-center gap-stack-md">
            <div className="relative hidden sm:block">
              <input className="bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-1.5 text-body-sm focus:ring-2 focus:ring-primary outline-none w-64 transition-all focus:w-80" placeholder="Search GRs, files..." type="text" />
              <span className="material-symbols-outlined absolute right-3 top-2 text-on-surface-variant text-sm">search</span>
            </div>
            <div className="flex items-center gap-2">
              <button className="p-2 text-on-surface-variant hover:text-primary transition-colors">
                <span className="material-symbols-outlined">notifications</span>
              </button>
              <div className="relative cursor-pointer" onClick={(e) => { e.stopPropagation(); setIsDropdownOpen(!isDropdownOpen); }}>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-primary hidden sm:block">
                    {userRole || 'Not logged in'}
                  </span>
                  <div className="w-8 h-8 rounded-full bg-primary-container flex items-center justify-center border border-primary overflow-hidden ml-2">
                    <span className="material-symbols-outlined text-on-primary-container">person</span>
                  </div>
                </div>
                {userRole && isDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 border border-gray-200">
                    <button 
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Page Canvas */}
        <div className="flex-1 px-gutter py-stack-lg space-y-stack-lg max-w-container-max mx-auto w-full">
          {children}
        </div>

        {/* Footer */}
        <footer className="bg-surface-container-highest w-full py-stack-md border-t border-outline-variant mt-auto">
          <div className="flex flex-col md:flex-row justify-between items-center px-section-padding gap-stack-md max-w-container-max mx-auto w-full">
            <div className="text-center md:text-left">
              <p className="font-label-caps text-label-caps font-bold text-on-surface mb-1">GOVERNMENT OF MAHARASHTRA</p>
              <p className="font-body-sm text-[10px] text-on-surface-variant opacity-80">© 2026. Achuk Nirnay, Pragat Maharashtra. All Rights Reserved.</p>
            </div>
            <div className="flex gap-stack-md">
              <a className="font-label-caps text-[11px] text-on-surface-variant hover:underline hover:text-primary transition-opacity duration-200" href="#">Privacy Policy</a>
              <a className="font-label-caps text-[11px] text-on-surface-variant hover:underline hover:text-primary transition-opacity duration-200" href="#">Terms of Service</a>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}
