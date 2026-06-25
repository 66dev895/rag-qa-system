import { useState, useRef, useEffect } from 'react';
import { Upload, FileText, Send, Bot, User, Loader2, Database } from 'lucide-react';
import { uploadFile, indexDocuments, listDocuments, chatStream, healthCheck, Source } from './api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [ragReady, setRagReady] = useState(false);
  const [docCount, setDocCount] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const chatRef = useRef<HTMLDivElement>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => { checkHealth(); }, []);

  const checkHealth = async () => {
    try {
      const h = await healthCheck();
      setRagReady(h.rag_ready);
      setDocCount(h.documents || 0);
    } catch { /* backend not running */ }
  };

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const r = await uploadFile(file);
      if (r.status === 'ok') {
        const idx = await indexDocuments();
        setDocCount(idx.vector_count || 0);
        setRagReady(true);
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: `✅ 已上传并索引文档 "${r.filename}"（${r.pages} 页，${idx.total_chunks} 个片段）。现在可以开始提问了！`
        }]);
      }
    } catch (err) {
      alert('上传失败，请确认后端服务已启动');
    }
    setUploading(false);
  };

  const handleSend = async () => {
    const query = input.trim();
    if (!query || loading) return;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: query }]);
    setLoading(true);

    const assistantMsg: Message = { role: 'assistant', content: '' };
    setMessages(prev => [...prev, assistantMsg]);

    chatStream(
      query,
      (token) => {
        assistantMsg.content += token;
        setMessages(prev => [...prev.slice(0, -1), { ...assistantMsg }]);
      },
      (sources) => { assistantMsg.sources = sources; },
      () => setLoading(false),
      async () => {
        // 流式失败，回退到非流式
        try {
          const { chat: apiChat } = await import('./api');
          const r = await apiChat(query);
          assistantMsg.content = r.answer;
          assistantMsg.sources = r.sources;
          setMessages(prev => [...prev.slice(0, -1), { ...assistantMsg }]);
        } catch { assistantMsg.content = '⚠ 请求失败，请检查后端服务'; }
        setLoading(false);
      }
    );
  };

  useEffect(() => {
    chatRef.current?.scrollTo({ top: chatRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  return (
    <div style={{ display:'flex', width:'100%', height:'100vh' }}>
      {/* Sidebar */}
      <div style={{
        width: collapsed ? 0 : 280, minWidth: collapsed ? 0 : 280,
        background:'#161b22', borderRight:'1px solid #21262d',
        transition:'width .2s', overflow:'hidden',
        display:'flex', flexDirection:'column', padding: collapsed ? 0 : 20
      }}>
        <h2 style={{ color:'#58a6ff', fontSize:'1.1rem', marginBottom:16,
          display:'flex', alignItems:'center', gap:8 }}>
          <Database size={20} /> 文档管理
        </h2>
        <div style={{ marginBottom:16, fontSize:'0.85rem', color:'#8b949e' }}>
          状态：<span style={{ color: ragReady ? '#3fb950' : '#f85149' }}>
            {ragReady ? `就绪 (${docCount} 块)` : '未初始化'}
          </span>
        </div>
        <input ref={fileRef} type="file" accept=".pdf,.txt,.md"
          onChange={handleUpload} style={{ display:'none' }} />
        <button onClick={() => fileRef.current?.click()} disabled={uploading}
          style={{
            border:'1px dashed #30363d', borderRadius:8, padding:'16px',
            background:'#0d1117', color:'#c9d1d9', cursor:'pointer',
            display:'flex', alignItems:'center', gap:8, justifyContent:'center'
          }}>
          {uploading ? <Loader2 size={20} className="spin" /> : <Upload size={20} />}
          {uploading ? '上传中...' : '上传文档 (.pdf/.txt/.md)'}
        </button>
        <div style={{ marginTop:'auto', fontSize:'0.75rem', color:'#484f58', textAlign:'center' }}>
          RAG QA System v1.0
        </div>
      </div>

      {/* Chat */}
      <div style={{ flex:1, display:'flex', flexDirection:'column', minWidth:0 }}>
        <div ref={chatRef} style={{ flex:1, overflow:'auto', padding:'24px 32px' }}>
          {messages.length === 0 && (
            <div style={{ textAlign:'center', marginTop:'25vh', color:'#484f58' }}>
              <FileText size={48} style={{ marginBottom:16, opacity:0.5 }} />
              <p style={{ fontSize:'1.1rem' }}>上传文档后即可开始智能问答</p>
              <p style={{ fontSize:'0.85rem', marginTop:8 }}>
                支持 PDF、TXT、Markdown 格式
              </p>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} style={{ marginBottom:20, display:'flex', gap:12 }}>
              <div style={{
                width:36, height:36, borderRadius:'50%', display:'flex',
                alignItems:'center', justifyContent:'center', flexShrink:0,
                background: msg.role === 'user' ? '#238636' : '#1f6feb'
              }}>
                {msg.role === 'user' ? <User size={18} color="white" /> : <Bot size={18} color="white" />}
              </div>
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontSize:'0.8rem', color:'#8b949e', marginBottom:4 }}>
                  {msg.role === 'user' ? '你' : 'AI 助手'}
                </div>
                <div style={{
                  lineHeight:1.7, whiteSpace:'pre-wrap', wordBreak:'break-word',
                  background: msg.role === 'assistant' ? '#161b22' : 'transparent',
                  borderRadius:8, padding: msg.role === 'assistant' ? '12px 16px' : 0,
                  border: msg.role === 'assistant' ? '1px solid #21262d' : 'none',
                }}>
                  {msg.content || (loading && i === messages.length - 1 ? <Loader2 size={16} className="spin" /> : '')}
                </div>
                {msg.sources && msg.sources.length > 0 && (
                  <div style={{ marginTop:8 }}>
                    <div style={{ fontSize:'0.75rem', color:'#484f58', marginBottom:4 }}>📚 参考来源</div>
                    {msg.sources.map((s, j) => (
                      <div key={j} style={{
                        fontSize:'0.75rem', background:'#0d1117', borderRadius:4,
                        padding:'6px 10px', marginBottom:4, border:'1px solid #21262d'
                      }}>
                        <span style={{ color:'#58a6ff' }}>{s.source}</span>
                        <span style={{ color:'#484f58', marginLeft:8 }}>
                          相关度 {Math.round(s.score * 100)}%
                        </span>
                        <div style={{ color:'#8b949e', marginTop:2 }}>{s.content}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Input */}
        <div style={{ padding:'16px 32px', borderTop:'1px solid #21262d', background:'#161b22' }}>
          <div style={{ display:'flex', gap:8, maxWidth:800, margin:'0 auto' }}>
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
              placeholder={ragReady ? '基于文档提问...' : '请先上传文档'}
              style={{
                flex:1, padding:'12px 16px', borderRadius:8,
                background:'#0d1117', border:'1px solid #30363d', color:'#c9d1d9',
                fontSize:'0.95rem', outline:'none'
              }}
            />
            <button onClick={handleSend} disabled={loading || !ragReady}
              style={{
                width:48, height:48, borderRadius:8, border:'none',
                background: loading ? '#1f6feb44' : '#1f6feb',
                color:'white', cursor: loading ? 'default' : 'pointer',
                display:'flex', alignItems:'center', justifyContent:'center'
              }}>
              {loading ? <Loader2 size={20} className="spin" /> : <Send size={20} />}
            </button>
          </div>
        </div>
      </div>
      <style>{`.spin { animation: spin 1s linear infinite; } @keyframes spin { from { transform:rotate(0deg) } to { transform:rotate(360deg) } }`}</style>
    </div>
  );
}

export default App;
