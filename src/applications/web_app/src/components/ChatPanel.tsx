'use client';
import { useState } from 'react';
import { Send, Bot, User } from 'lucide-react';

interface ChatPanelProps {
  ragContext: any;
}

export default function ChatPanel({ ragContext }: ChatPanelProps) {
  const [messages, setMessages] = useState<{role: 'user' | 'bot', text: string}[]>([
    { role: 'bot', text: 'Olá! Sou o Copiloto Orbital. Como posso ajudar você a analisar as informações do dashboard e a estratégia de comercialização hoje?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMsg,
          rag_context: ragContext
        })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { role: 'bot', text: data.reply || 'Desculpe, ocorreu um erro.' }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', text: 'Erro de conexão com o Copiloto.' }]);
    }
    setLoading(false);
  };

  return (
    <div className="glass-panel fade-in" style={{ display: 'flex', flexDirection: 'column', height: '400px', padding: 0 }}>
      <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--panel-border)', display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(0,0,0,0.2)' }}>
        <Bot size={20} color="var(--accent-primary)" />
        <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Copiloto Comercial</h3>
      </div>
      
      <div style={{ flex: 1, overflowY: 'auto', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {messages.map((msg, idx) => (
          <div key={idx} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
            <div style={{ 
              width: '32px', height: '32px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', 
              background: msg.role === 'user' ? 'var(--accent-primary)' : 'rgba(255,255,255,0.1)' 
            }}>
              {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
            </div>
            <div style={{ 
              background: msg.role === 'user' ? 'rgba(59, 130, 246, 0.2)' : 'rgba(0,0,0,0.3)', 
              padding: '1rem', borderRadius: '8px', maxWidth: '80%', whiteSpace: 'pre-wrap', lineHeight: '1.5',
              border: msg.role === 'user' ? '1px solid rgba(59, 130, 246, 0.4)' : '1px solid var(--panel-border)'
            }}>
              {msg.text}
            </div>
          </div>
        ))}
        {loading && (
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></div>
            <span style={{ color: 'var(--text-muted)' }}>Pensando...</span>
          </div>
        )}
      </div>

      <form onSubmit={sendMessage} style={{ padding: '1rem', borderTop: '1px solid var(--panel-border)', display: 'flex', gap: '0.8rem' }}>
        <input 
          type="text" 
          value={input} 
          onChange={e => setInput(e.target.value)}
          placeholder="Pergunte sobre a estratégia de Basis..." 
          style={{ flex: 1, padding: '0.8rem 1.2rem', borderRadius: '8px', border: '1px solid var(--panel-border)', background: 'rgba(0,0,0,0.2)', color: 'var(--text-main)', outline: 'none', fontSize: '0.95rem' }}
        />
        <button type="submit" disabled={loading || !input.trim()} style={{ 
          background: (loading || !input.trim()) ? 'rgba(255,255,255,0.1)' : 'var(--accent-primary)', 
          color: (loading || !input.trim()) ? 'var(--text-muted)' : '#fff',
          border: 'none',
          borderRadius: '8px',
          width: '50px',
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          cursor: (loading || !input.trim()) ? 'not-allowed' : 'pointer',
          transition: 'all 0.2s',
          flexShrink: 0
        }}>
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
