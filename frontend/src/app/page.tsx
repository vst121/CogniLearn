'use client';

import { useState, useActionState, useEffect } from 'react';
import { Logo } from '@/components/Logo';
import { sendChatMessage, ChatState } from './actions';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: ChatState['citations'];
  mode?: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [language, setLanguage] = useState<'en' | 'de'>('en');
  const [mode, setMode] = useState<'citation' | 'socratic'>('citation');
  const [inputQuery, setInputQuery] = useState('');

  // Modern React Hook for Server Action management
  const [state, formAction, isPending] = useActionState(sendChatMessage, null);

  // Append new assistant response when server action completes
  useEffect(() => {
    if (state?.answer) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: state.answer,
          citations: state.citations,
          mode: state.mode,
        },
      ]);
      setInputQuery('');
    } else if (state?.error) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: state.error! },
      ]);
    }
  }, [state]);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    if (!inputQuery.trim()) return;

    // Immediately reflect user message in local state UI
    setMessages((prev) => [...prev, { role: 'user', content: inputQuery }]);
  };

  return (
    <div className="flex flex-col h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md">
        <Logo />
        <div className="flex items-center gap-4">
          {/* Language Switcher */}
          <div className="flex items-center bg-slate-800 p-1 rounded-lg text-xs font-semibold">
            <button
              type="button"
              onClick={() => setLanguage('en')}
              className={`px-3 py-1 rounded-md transition ${language === 'en' ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              EN 🇬🇧
            </button>
            <button
              type="button"
              onClick={() => setLanguage('de')}
              className={`px-3 py-1 rounded-md transition ${language === 'de' ? 'bg-sky-500 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              DE 🇩🇪
            </button>
          </div>

          {/* Mode Switcher */}
          <div className="flex items-center bg-slate-800 p-1 rounded-lg text-xs font-semibold">
            <button
              type="button"
              onClick={() => setMode('citation')}
              className={`px-3 py-1 rounded-md transition ${mode === 'citation' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              Q&A Citation
            </button>
            <button
              type="button"
              onClick={() => setMode('socratic')}
              className={`px-3 py-1 rounded-md transition ${mode === 'socratic' ? 'bg-emerald-600 text-white' : 'text-slate-400 hover:text-white'}`}
            >
              Socratic Tutor
            </button>
          </div>
        </div>
      </header>

      {/* Main Stream Area */}
      <main className="flex-1 overflow-y-auto p-6 space-y-6 max-w-4xl mx-auto w-full">
        {messages.length === 0 && (
          <div className="text-center py-20 text-slate-500">
            <h2 className="text-xl font-semibold mb-2">CogniLearn AI Workspace</h2>
            <p className="text-sm">
              {language === 'de' 
                ? 'Stelle eine Frage zum Kurs DL-101 auf Deutsch oder Englisch.' 
                : 'Ask a question about course DL-101 in English or German.'}
            </p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`p-4 rounded-xl max-w-2xl text-sm leading-relaxed ${
              msg.role === 'user' ? 'bg-sky-600 text-white' : 'bg-slate-900 border border-slate-800 text-slate-200 shadow-md'
            }`}>
              {msg.content}
            </div>

            {/* Render Citations */}
            {msg.citations && msg.citations.length > 0 && (
              <div className="mt-3 space-y-2 max-w-2xl w-full">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">Source Citations</span>
                <div className="grid grid-cols-1 gap-2">
                  {msg.citations.map((cite, cIdx) => (
                    <div key={cIdx} className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 text-xs text-slate-300">
                      <div className="font-semibold text-emerald-400 mb-1">
                        {cite.chapter} — {cite.section}
                      </div>
                      <p className="italic text-slate-400">{cite.content_snippet}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </main>

      {/* Form with Server Action */}
      <footer className="p-4 border-t border-slate-800 bg-slate-900/30">
        <form 
          action={formAction} 
          onSubmit={handleSubmit} 
          className="max-w-4xl mx-auto flex gap-3"
        >
          {/* Hidden inputs to pass language & mode parameters to the Server Action */}
          <input type="hidden" name="course_code" value="DL-101" />
          <input type="hidden" name="language" value={language} />
          <input type="hidden" name="mode" value={mode} />

          <input
            type="text"
            name="query"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder={language === 'de' ? 'Stelle eine Frage zum Kurs...' : 'Ask a question about the course...'}
            className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-100 focus:outline-none focus:border-sky-500"
          />
          <button
            type="submit"
            disabled={isPending}
            className="bg-sky-500 hover:bg-sky-600 disabled:opacity-50 font-semibold px-6 py-3 rounded-xl text-sm transition"
          >
            {isPending ? 'Thinking...' : 'Send'}
          </button>
        </form>
      </footer>
    </div>
  );
}