import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Bot, User, MessageSquare } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from './ui/card';
import aiService from '../services/aiService';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatWidget = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Hello! I am **StockSteward AI**. How can I assist you with your trading today?' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const toggleChat = () => setIsOpen(!isOpen);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        if (isOpen) {
            scrollToBottom();
        }
    }, [messages, isOpen]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMessage = input.trim();
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setInput('');
        setLoading(true);

        try {
            const data = await aiService.chat(userMessage);
            setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
        } catch (error) {
            console.error("Chat error:", error);
            setMessages(prev => [...prev, { role: 'assistant', content: "I'm having trouble connecting to the neural network. Please check your connection and try again." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
            {isOpen && (
                <Card className="w-[350px] md:w-[420px] h-[550px] shadow-[0_20px_50px_rgba(0,0,0,0.3)] mb-4 animate-in slide-in-from-bottom-10 fade-in duration-300 flex flex-col border-white/20 bg-white/95 backdrop-blur-xl overflow-hidden rounded-2xl">
                    <CardHeader className="bg-[#0A2A4D] text-white p-5 rounded-t-2xl flex flex-row items-center justify-between border-b border-white/10">
                        <div className="flex items-center gap-3">
                            <div className="h-10 w-10 rounded-xl bg-primary/20 flex items-center justify-center border border-primary/20 shadow-inner">
                                <Bot size={22} className="text-primary" />
                            </div>
                            <div>
                                <CardTitle className="text-base font-black tracking-tight">StockSteward AI</CardTitle>
                                <div className="flex items-center gap-1.5 mt-0.5">
                                    <div className="h-1.5 w-1.5 rounded-full bg-green-500 animate-pulse" />
                                    <span className="text-[10px] font-bold text-white/60 uppercase tracking-widest">Neural Link Active</span>
                                </div>
                            </div>
                        </div>
                        <Button variant="ghost" size="icon" onClick={toggleChat} className="h-8 w-8 text-white/70 hover:text-white hover:bg-white/10 transition-colors">
                            <X size={20} />
                        </Button>
                    </CardHeader>
                    <CardContent className="flex-1 overflow-y-auto p-5 space-y-6 bg-slate-50/50">
                        {messages.map((msg, idx) => (
                            <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                                <div className={`h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0 shadow-sm ${msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-primary text-white'}`}>
                                    {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                                </div>
                                <div className={`max-w-[85%] p-3.5 rounded-2xl text-[13px] leading-relaxed shadow-sm ${msg.role === 'user'
                                    ? 'bg-indigo-600 text-white rounded-tr-none'
                                    : 'bg-white border border-slate-200 text-slate-800 rounded-tl-none'
                                    }`}>
                                    {msg.role === 'user' ? (
                                        <div className="font-medium">{msg.content}</div>
                                    ) : (
                                        <div className="prose prose-slate prose-sm max-w-none">
                                            <ReactMarkdown
                                                remarkPlugins={[remarkGfm]}
                                                components={{
                                                    p: ({ node, ...props }) => <p className="mb-3 last:mb-0" {...props} />,
                                                    ul: ({ node, ...props }) => <ul className="list-disc pl-5 mb-3 space-y-1" {...props} />,
                                                    ol: ({ node, ...props }) => <ol className="list-decimal pl-5 mb-3 space-y-1" {...props} />,
                                                    li: ({ node, ...props }) => <li className="mb-0.5" {...props} />,
                                                    strong: ({ node, ...props }) => <strong className="font-bold text-slate-900" {...props} />,
                                                    code: ({ node, inline, className, children, ...props }) => {
                                                        const match = /language-(\w+)/.exec(className || '');
                                                        if (inline || !match) {
                                                            return <code className="bg-slate-100 text-indigo-600 px-1.5 py-0.5 rounded font-mono text-xs" {...props}>{children}</code>;
                                                        }
                                                        return (
                                                            <div className="relative group my-4">
                                                                <pre className="bg-slate-900 text-slate-100 p-4 rounded-xl overflow-x-auto border border-slate-800 font-mono text-xs leading-normal">
                                                                    <code {...props}>{children}</code>
                                                                </pre>
                                                            </div>
                                                        );
                                                    },
                                                    h1: ({ node, ...props }) => <h1 className="text-lg font-black mt-4 mb-2 border-b pb-1" {...props} />,
                                                    h2: ({ node, ...props }) => <h2 className="text-base font-bold mt-4 mb-2" {...props} />,
                                                    blockquote: ({ node, ...props }) => (
                                                        <blockquote className="border-l-4 border-primary pl-4 py-1 italic bg-primary/5 rounded-r text-slate-600 my-3" {...props} />
                                                    ),
                                                }}
                                            >
                                                {msg.content}
                                            </ReactMarkdown>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                        {loading && (
                            <div className="flex gap-3">
                                <div className="h-8 w-8 rounded-lg bg-primary text-white flex items-center justify-center shadow-sm">
                                    <Bot size={16} />
                                </div>
                                <div className="bg-white border border-slate-200 p-4 rounded-2xl rounded-tl-none flex gap-1.5 items-center shadow-sm">
                                    <span className="w-1.5 h-1.5 bg-primary/40 rounded-full animate-bounce [animation-delay:-0.3s]" />
                                    <span className="w-1.5 h-1.5 bg-primary/60 rounded-full animate-bounce [animation-delay:-0.15s]" />
                                    <span className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce" />
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </CardContent>
                    <CardFooter className="p-4 border-t bg-white">
                        <form onSubmit={handleSend} className="flex w-full gap-2 items-center">
                            <div className="relative flex-1">
                                <input
                                    type="text"
                                    className="w-full pl-4 pr-10 py-3 rounded-xl border border-slate-200 bg-slate-50 text-[13px] focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all pr-12"
                                    placeholder="Ask about strategy, Nifty levels..."
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    disabled={loading}
                                />
                                <div className={`absolute right-3 top-1/2 -translate-y-1/2 text-[10px] font-bold uppercase transition-opacity duration-300 ${input.length > 0 ? 'opacity-40' : 'opacity-0'}`}>
                                    Enter
                                </div>
                            </div>
                            <Button
                                type="submit"
                                size="icon"
                                disabled={loading || !input.trim()}
                                className={`h-11 w-11 rounded-xl shadow-lg transition-all duration-300 ${input.trim() ? 'bg-primary scale-100' : 'bg-slate-200 scale-90 translate-y-1'}`}
                            >
                                <Send size={18} className={loading ? 'animate-pulse' : ''} />
                            </Button>
                        </form>
                    </CardFooter>
                </Card>
            )}

            <Button
                onClick={toggleChat}
                className={`h-14 w-14 rounded-2xl shadow-2xl hover:scale-110 active:scale-95 transition-all duration-300 flex items-center justify-center p-0 border-none ${isOpen ? 'bg-red-500 text-white rotate-90' : 'bg-primary text-white'}`}
            >
                {isOpen ? <X size={28} /> : <MessageSquare size={28} />}
            </Button>
        </div>
    );
};

export default ChatWidget;