import React, { useState } from 'react';
import { askFAQ } from '../api/client';

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState(null);
  const [question, setQuestion] = useState("");
  const [aiAnswer, setAiAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const faqs = [
    {
      question: "What is MAHA-GR ALIGN?",
      answer: "MAHA-GR ALIGN is an AI-powered drafting portal designed to assist government officers in drafting, verifying, and generating Government Resolutions (GRs) efficiently while ensuring they comply with past policies and constitutional guidelines."
    },
    {
      question: "How does the AI detect conflicts?",
      answer: "When a new GR is drafted, the AI scans our vector database (Qdrant) containing previously ingested GRs. It compares the semantic meaning of the new draft against historical policies and flags any contradictions, duplicate funding allocations, or policy overlaps."
    },
    {
      question: "What is the Bilingual Terminology Checker?",
      answer: "The terminology checker scans your draft for informal or colloquial Marathi/English words (like 'paripatra' or 'shasan nirnay') and suggests the standardized official government terminology to ensure the document maintains a professional and legal tone."
    },
    {
      question: "How are references verified?",
      answer: "The AI automatically extracts any cited GR numbers or reference documents from your draft. It then searches the database to confirm those documents actually exist. If it detects a hallucinated or incorrect reference, it will flag it as 'Missing'."
    },
    {
      question: "Can I download the generated GR?",
      answer: "Yes! Once the draft is finalized and approved, you can download it in both DOCX and PDF formats. The system automatically formats the document according to the official Government of Maharashtra template."
    }
  ];

  const toggleFAQ = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  const handleAskAI = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    setLoading(true);
    setAiAnswer("");
    try {
      const result = await askFAQ(question);
      setAiAnswer(result.answer);
    } catch (err) {
      setAiAnswer("Sorry, I encountered an error connecting to the AI service.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8 pb-12">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-primary mb-2">Frequently Asked Questions</h2>
        <p className="text-on-surface-variant">Find answers to common questions about using the AI Drafting Portal.</p>
      </div>

      <div className="space-y-4">
        {faqs.map((faq, index) => (
          <div 
            key={index} 
            className="border border-outline-variant rounded-lg bg-surface-container-lowest overflow-hidden transition-all duration-200"
          >
            <button 
              className="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-surface-container-low focus:outline-none"
              onClick={() => toggleFAQ(index)}
            >
              <span className="font-semibold text-lg text-on-surface">{faq.question}</span>
              <span className="material-symbols-outlined text-primary transition-transform duration-300" style={{ transform: openIndex === index ? 'rotate(180deg)' : 'rotate(0deg)' }}>
                expand_more
              </span>
            </button>
            
            <div 
              className="px-6 text-on-surface-variant"
              style={{
                maxHeight: openIndex === index ? '500px' : '0',
                paddingBottom: openIndex === index ? '1rem' : '0',
                opacity: openIndex === index ? 1 : 0,
                transition: 'all 0.3s ease-in-out'
              }}
            >
              {faq.answer}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-12 bg-surface-container-low border border-outline-variant rounded-lg p-6 shadow-sm">
        <h3 className="text-xl font-bold text-primary flex items-center gap-2 mb-4">
          <span className="material-symbols-outlined">psychology</span>
          Have another question? Ask the AI!
        </h3>
        <form onSubmit={handleAskAI} className="flex gap-4">
          <input 
            type="text"
            className="flex-1 bg-white border border-outline-variant rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="E.g., How do I export a GR as a PDF?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <button 
            type="submit"
            disabled={loading || !question.trim()}
            className="bg-primary text-white font-bold py-3 px-6 rounded-lg hover:bg-primary-container hover:text-primary transition-colors disabled:opacity-50"
          >
            {loading ? "Thinking..." : "Ask AI"}
          </button>
        </form>
        {aiAnswer && (
          <div className="mt-6 bg-white p-4 rounded border border-primary/20 shadow-inner">
            <p className="text-on-surface-variant font-medium text-sm mb-2 text-primary">AI Answer:</p>
            <p className="text-on-surface whitespace-pre-wrap">{aiAnswer}</p>
          </div>
        )}
      </div>
    </div>
  );
}
