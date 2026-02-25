import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';

export default function ChatPage() {
    const [messages, setMessages] = useState([
        {
            role: 'ai',
            content: "Hello! I'm **EKA**, your governed automobile intelligence assistant. Ask me about vehicle diagnostics, maintenance, or service queries.\n\n_Example: \"My 2019 Swift makes a grinding noise when braking\"_",
        },
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [vehicle, setVehicle] = useState({ make: '', model: '', year: '', fuel: '' });
    const [showVehicle, setShowVehicle] = useState(false);
    const bottomRef = useRef(null);

    useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

    const sendMessage = async () => {
        if (!input.trim() || loading) return;
        const userMsg = input.trim();
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setLoading(true);

        try {
            const token = localStorage.getItem('eka_token');
            const vehiclePayload = vehicle.make ? vehicle : undefined;
            const res = await fetch('/api/v1/chat/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ query: userMsg, vehicle: vehiclePayload }),
            });

            if (!res.ok) {
                const err = await res.json();
                setMessages(prev => [...prev, { role: 'ai', content: `⚠️ **Gate Blocked**: ${err.detail}`, isError: true }]);
                return;
            }

            const data = await res.json();
            const formatted = `**Issue Summary**\n${data.issue_summary}\n\n**Probable Causes**\n${(data.probable_causes || []).map(c => `• ${c}`).join('\n')}\n\n**Diagnostic Steps**\n${(data.diagnostic_steps || []).map((s, i) => `${i + 1}. ${s}`).join('\n')}\n\n**Safety Advisory**\n⚠️ ${data.safety_advisory}\n\n**Confidence**: ${data.confidence_level}%${data.tokens_used ? ` • **Tokens**: ${data.tokens_used}` : ''}`;

            setMessages(prev => [...prev, { role: 'ai', content: formatted }]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'ai', content: `❌ Error: ${err.message}`, isError: true }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fade-in">
            <div className="main__header">
                <div>
                    <h2 style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <Sparkles size={22} color="var(--accent)" /> EKA Intelligence
                    </h2>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.84rem', marginTop: 4 }}>
                        Domain-locked • 4-gate governed • RAG-augmented
                    </p>
                </div>
                <button className="btn btn--ghost btn--sm" onClick={() => setShowVehicle(!showVehicle)}>
                    {showVehicle ? 'Hide' : 'Set'} Vehicle Context
                </button>
            </div>

            {/* Vehicle context panel */}
            {showVehicle && (
                <div className="card" style={{ marginBottom: 20, padding: 16 }}>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
                        <div><label>Make</label><input className="input" placeholder="e.g. Maruti" value={vehicle.make} onChange={e => setVehicle({ ...vehicle, make: e.target.value })} /></div>
                        <div><label>Model</label><input className="input" placeholder="e.g. Swift" value={vehicle.model} onChange={e => setVehicle({ ...vehicle, model: e.target.value })} /></div>
                        <div><label>Year</label><input className="input" type="number" placeholder="e.g. 2019" value={vehicle.year} onChange={e => setVehicle({ ...vehicle, year: e.target.value })} /></div>
                        <div><label>Fuel</label>
                            <select className="input" value={vehicle.fuel} onChange={e => setVehicle({ ...vehicle, fuel: e.target.value })}>
                                <option value="">Select</option>
                                <option value="petrol">Petrol</option>
                                <option value="diesel">Diesel</option>
                                <option value="electric">Electric</option>
                                <option value="hybrid">Hybrid</option>
                            </select>
                        </div>
                    </div>
                </div>
            )}

            {/* Chat messages */}
            <div className="chat">
                <div className="chat__messages">
                    {messages.map((msg, i) => (
                        <div key={i} className={`chat__bubble chat__bubble--${msg.role === 'user' ? 'user' : 'ai'}`}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                                {msg.role === 'ai' ? <Bot size={15} /> : <User size={15} />}
                                <span style={{ fontSize: '0.72rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                    {msg.role === 'ai' ? 'EKA' : 'You'}
                                </span>
                            </div>
                            <div style={{ whiteSpace: 'pre-wrap' }}>
                                {msg.content.split('\n').map((line, j) => {
                                    const bold = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
                                    const italic = bold.replace(/_(.*?)_/g, '<em>$1</em>');
                                    return <div key={j} dangerouslySetInnerHTML={{ __html: italic }} />;
                                })}
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="chat__bubble chat__bubble--ai" style={{ opacity: 0.6 }}>
                            <div style={{ display: 'flex', gap: 6 }}>
                                <span style={{ animation: 'pulse 1s infinite' }}>●</span>
                                <span style={{ animation: 'pulse 1s 0.2s infinite' }}>●</span>
                                <span style={{ animation: 'pulse 1s 0.4s infinite' }}>●</span>
                            </div>
                        </div>
                    )}
                    <div ref={bottomRef} />
                </div>

                <div className="chat__input-row">
                    <input
                        className="input" placeholder="Ask EKA about automotive diagnostics…"
                        value={input} onChange={e => setInput(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && sendMessage()}
                        disabled={loading}
                    />
                    <button className="btn btn--primary" onClick={sendMessage} disabled={loading}>
                        <Send size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
}
