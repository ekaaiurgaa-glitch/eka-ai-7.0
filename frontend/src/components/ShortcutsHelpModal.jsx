import { useEffect } from 'react';
import { X, Keyboard } from 'lucide-react';

const SHORTCUTS = [
    { key: 'Ctrl + D', description: 'Go to Dashboard' },
    { key: 'Ctrl + J', description: 'Go to Job Cards' },
    { key: 'Ctrl + O', description: 'Go to Operator AI' },
    { key: 'Ctrl + F', description: 'Focus Search' },
    { key: '?', description: 'Show this help' },
    { key: 'Esc', description: 'Close modal' },
];

export default function ShortcutsHelpModal({ isOpen, onClose }) {
    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.key === 'Escape') {
                onClose();
            }
        };

        if (isOpen) {
            window.addEventListener('keydown', handleKeyDown);
            return () => window.removeEventListener('keydown', handleKeyDown);
        }
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    return (
        <div 
            className="modal-overlay"
            onClick={onClose}
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'rgba(0, 0, 0, 0.7)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000,
                backdropFilter: 'blur(4px)'
            }}
        >
            <div 
                className="modal"
                onClick={e => e.stopPropagation()}
                style={{
                    background: 'var(--bg-secondary)',
                    borderRadius: 12,
                    padding: 24,
                    minWidth: 400,
                    maxWidth: 500,
                    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
                    border: '1px solid var(--border-glass)'
                }}
            >
                <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    alignItems: 'center',
                    marginBottom: 20,
                    borderBottom: '1px solid var(--border-glass)',
                    paddingBottom: 16
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <Keyboard size={22} color="var(--accent)" />
                        <h3 style={{ margin: 0, fontSize: '1.2rem' }}>Keyboard Shortcuts</h3>
                    </div>
                    <button 
                        onClick={onClose}
                        style={{
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            color: 'var(--text-muted)',
                            padding: 4,
                            borderRadius: 4,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}
                    >
                        <X size={20} />
                    </button>
                </div>

                <div style={{ display: 'grid', gap: '12px' }}>
                    {SHORTCUTS.map((shortcut) => (
                        <div 
                            key={shortcut.key}
                            style={{ 
                                display: 'flex', 
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                padding: '10px 12px',
                                background: 'var(--bg-glass)',
                                borderRadius: 8,
                                border: '1px solid var(--border-glass)'
                            }}
                        >
                            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                {shortcut.description}
                            </span>
                            <kbd style={{ 
                                background: 'var(--bg-primary)', 
                                padding: '4px 10px', 
                                borderRadius: 6,
                                fontFamily: 'monospace',
                                fontSize: '0.8rem',
                                border: '1px solid var(--border-glass)',
                                color: 'var(--text-primary)',
                                fontWeight: 600,
                                minWidth: 80,
                                textAlign: 'center'
                            }}>
                                {shortcut.key}
                            </kbd>
                        </div>
                    ))}
                </div>

                <div style={{ 
                    marginTop: 20, 
                    padding: 12, 
                    background: 'var(--bg-glass)', 
                    borderRadius: 8,
                    fontSize: '0.8rem',
                    color: 'var(--text-muted)',
                    textAlign: 'center',
                    border: '1px solid var(--border-glass)'
                }}>
                    Press <kbd style={{ 
                        background: 'var(--bg-primary)', 
                        padding: '2px 6px', 
                        borderRadius: 4,
                        fontFamily: 'monospace'
                    }}>?</kbd> anytime to show this help
                </div>
            </div>
        </div>
    );
}
