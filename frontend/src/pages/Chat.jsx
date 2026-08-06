import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Namaskar! I am your AI Legal Advisor for Maharashtra Government Resolutions. How can I assist you with legal queries or policy clarifications today?',
      sources: []
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const historyPayload = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const res = await axios.post('http://localhost:8080/chat', {
        query: userMessage.content,
        history: historyPayload,
        top_k: 5
      });
      
      const aiMessage = {
        role: 'assistant',
        content: res.data.answer,
        sources: res.data.sources || []
      };
      
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error connecting to the database.', sources: [] }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async () => {
    if (messages.length <= 1 || loading) return;
    setLoading(true);
    try {
      // Find all unique sources from the chat history
      const allSources = [];
      messages.forEach(m => {
        if (m.sources) {
          m.sources.forEach(s => {
            if (!allSources.find(as => as.gr_no === s.gr_no)) {
              allSources.push(s);
            }
          });
        }
      });

      if (allSources.length === 0) {
        setMessages((prev) => [...prev, { role: 'assistant', content: 'No GRs found in the chat to summarize.', sources: [] }]);
        setLoading(false);
        return;
      }

      const textToSummarize = allSources.map(s => `GR Number: ${s.gr_no}\nDepartment: ${s.department}\nText: ${s.text}`).join('\n\n---\n\n');
      
      const res = await axios.post('http://localhost:8080/api/chat/summarize', {
        text: `Please provide a brief, distinct summary for each of the following Government Resolutions:\n\n${textToSummarize}`,
        llm_provider: 'groq'
      });
      
      const summaryMsg = {
        role: 'assistant',
        content: `**GR Summaries:**\n\n${res.data.summary}`,
        sources: []
      };
      setMessages((prev) => [...prev, summaryMsg]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, failed to generate summary.', sources: [] }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] -m-6 max-h-[900px] bg-background">
      {/* Header Section */}
      <header className="px-gutter py-stack-md border-b border-outline-variant bg-surface flex flex-col md:flex-row md:items-end justify-between gap-stack-md">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <h1 className="font-h1 text-h1 text-on-surface">AI Legal Advisor</h1>
            <span className="bg-primary-container/10 text-primary px-3 py-1 rounded-full text-body-sm font-bold border border-primary-container/20 flex items-center gap-1">
              <span className="material-symbols-outlined text-[14px]">psychology</span>
              AI Advisory Module
            </span>
          </div>
          <p className="text-on-surface-variant font-body-lg text-body-lg max-w-3xl">
            Query the archive of Maharashtra GRs for legal precedents, rules, and policy clarifications.
          </p>
        </div>
        <div className="flex gap-4">
          <button 
            onClick={handleSummarize}
            disabled={messages.length <= 1 || loading}
            className="flex items-center gap-2 px-4 py-2 bg-secondary text-white font-bold rounded shadow-sm hover:bg-secondary/90 disabled:opacity-50"
          >
            <span className="material-symbols-outlined text-[18px]">summarize</span>
            Summarize Chat
          </button>
        </div>
      </header>

      {/* Main Chat Area */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Chat Interface */}
        <div className="flex-1 flex flex-col bg-surface-container-lowest">
          <div className="flex-1 overflow-y-auto p-gutter space-y-6 custom-scrollbar">
            {messages.map((msg, index) => (
              <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center mr-3 mt-1 shrink-0">
                    <span className="material-symbols-outlined text-white text-[16px]">gavel</span>
                  </div>
                )}
                <div 
                  className={`max-w-[85%] rounded-2xl p-5 shadow-sm font-body-md leading-relaxed ${
                    msg.role === 'user' 
                      ? 'bg-primary text-white rounded-tr-sm' 
                      : 'bg-surface border border-outline-variant text-on-surface rounded-tl-sm'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                  
                  {/* Citations / Sources */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-5 pt-4 border-t border-outline-variant/30">
                      <p className="font-label-caps text-label-caps opacity-80 mb-3 uppercase tracking-wider flex items-center gap-2">
                        <span className="material-symbols-outlined text-[14px]">auto_stories</span>
                        Verified Sources
                      </p>
                      <div className="flex flex-col gap-2">
                        {msg.sources.map((source, idx) => (
                          <div key={idx} className={`rounded text-body-sm border overflow-hidden ${msg.role === 'user' ? 'bg-primary-fixed text-on-primary-fixed border-primary-fixed-dim' : 'bg-surface-container-low text-on-surface border-outline-variant'}`}>
                            <div className="p-3 font-bold flex items-center border-b border-outline-variant/20">
                              <span className="mr-2 text-primary">GR {source.gr_no}</span> 
                              <span className="font-normal truncate flex-1 opacity-70">• {source.department}</span>
                            </div>
                            <div className="p-4 bg-surface-container-lowest text-sm leading-relaxed whitespace-pre-wrap font-document-text opacity-90">
                              {source.text}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center mr-3 mt-1 shrink-0">
                  <span className="material-symbols-outlined text-white text-[16px]">psychology</span>
                </div>
                <div className="bg-surface border border-outline-variant text-on-surface rounded-2xl rounded-tl-sm p-5 shadow-sm flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                  <span className="ml-2 font-body-sm text-on-surface-variant italic">Analyzing legal archives...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-gutter border-t border-outline-variant bg-surface-container-low">
            <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about legal provisions, financial limits, or specific GRs..."
                className="w-full bg-surface-container-lowest border border-outline-variant rounded-full pl-6 pr-16 py-4 font-body-md text-on-surface focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all shadow-sm"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={!input.trim() || loading}
                className={`absolute right-2 top-2 bottom-2 rounded-full w-12 h-12 flex items-center justify-center transition-all shadow ${
                  !input.trim() || loading 
                    ? 'bg-surface-variant text-on-surface-variant cursor-not-allowed' 
                    : 'bg-primary hover:bg-primary-container hover:text-on-primary-container text-white transform hover:scale-105'
                }`}
              >
                <span className="material-symbols-outlined">send</span>
              </button>
            </form>
            <div className="text-center mt-3">
              <span className="font-label-caps text-[10px] text-on-surface-variant uppercase tracking-widest">
                Achuk Nirnay, Pragat Maharashtra
              </span>
            </div>
          </div>
        </div>

        {/* Right Sidebar Placeholder (Optional for Legal Info) */}
        <aside className="hidden lg:block w-80 bg-surface border-l border-outline-variant p-stack-md overflow-y-auto">
          <div className="bg-primary/5 border border-primary/20 rounded-xl p-stack-md mb-6">
            <h4 className="font-label-caps text-label-caps text-primary border-b border-primary/10 pb-2 mb-4">SYSTEM CAPABILITIES</h4>
            <ul className="space-y-3 font-body-sm text-on-surface">
              <li className="flex items-start gap-2">
                <span className="material-symbols-outlined text-primary text-[18px]">search</span>
                Semantic Search across 10,000+ GRs
              </li>
              <li className="flex items-start gap-2">
                <span className="material-symbols-outlined text-primary text-[18px]">rule</span>
                Identify conflicting clauses
              </li>
              <li className="flex items-start gap-2">
                <span className="material-symbols-outlined text-primary text-[18px]">summarize</span>
                Summarize long documents
              </li>
            </ul>
          </div>
          
          <div className="bg-surface-container-lowest border border-outline-variant rounded-xl p-4">
             <h4 className="font-label-caps text-label-caps text-on-surface-variant border-b border-outline-variant pb-2 mb-3">EXAMPLE QUERIES</h4>
             <div className="space-y-2">
               <button onClick={() => setInput("What are the financial limits for district-level procurement?")} className="w-full text-left text-body-sm text-on-surface p-2 hover:bg-surface-container-low rounded border border-transparent hover:border-outline-variant transition-all">
                 "What are the financial limits for district-level procurement?"
               </button>
               <button onClick={() => setInput("Show me GRs related to agricultural subsidies from 2022.")} className="w-full text-left text-body-sm text-on-surface p-2 hover:bg-surface-container-low rounded border border-transparent hover:border-outline-variant transition-all">
                 "Show me GRs related to agricultural subsidies from 2022."
               </button>
             </div>
          </div>
        </aside>
      </div>
    </div>
  );
}
