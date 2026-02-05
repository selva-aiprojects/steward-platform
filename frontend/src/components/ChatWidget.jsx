import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Bot, User } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from './ui/card';
import aiService from '../services/aiService';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const ChatWidget = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Hello! I am StockSteward AI. How can I assist you with your trading today?' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const toggleChat = () => setIsOpen(!isOpen);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isOpen]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = input.trim();
        setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
        setInput('');
        setLoading(true);

        try {
            const data = await aiService.chat(userMessage);
            setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);
        } catch (error) {
            console.error("Chat error:", error);
            setMessages(prev => [...prev, { role: 'assistant', content: "I'm having trouble connecting right now. Please try again later." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
            {isOpen && (
                <Card className="w-[350px] md:w-[400px] h-[500px] shadow-2xl mb-4 animate-in slide-in-from-bottom-10 fade-in duration-300 flex flex-col">
                    <CardHeader className="bg-primary text-primary-foreground p-4 rounded-t-xl flex flex-row items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Bot size={20} />
                            <CardTitle className="text-lg">StockSteward AI</CardTitle>
                        </div>
                        <Button variant="ghost" size="icon" onClick={toggleChat} className="h-8 w-8 text-primary-foreground hover:bg-primary-foreground/20">
                            <X size={18} />
                        </Button>
                    </CardHeader>
                    <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
                        {messages.map((msg, idx) => (
                            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`max-w-[80%] p-3 rounded-lg text-sm ${msg.role === 'user' ? 'bg-primary text-primary-foreground rounded-tr-none' : 'bg-muted rounded-tl-none'}`}>
                                    {msg.role === 'user' ? (
                                        msg.content
                                    ) : (
                                        <ReactMarkdown
                                            remarkPlugins={[remarkGfm]}
                                            components={{
                                                // Custom rendering for different markdown elements
                                                p: ({node, ...props}) => <p className="mb-2" {...props} />,
                                                ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-2" {...props} />,
                                                ol: ({node, ...props}) => <ol className="list-decimal pl-5 mb-2" {...props} />,
                                                li: ({node, ...props}) => <li className="mb-1" {...props} />,
                                                strong: ({node, ...props}) => <strong className="font-bold" {...props} />,
                                                em: ({node, ...props}) => <em className="italic" {...props} />,
                                                code: ({node, inline, ...props}) => {
                                                    if (inline) {
                                                        return <code className="bg-gray-200 text-gray-800 px-1 py-0.5 rounded text-xs" {...props} />;
                                                    } else {
                                                        return (
                                                            <pre className="bg-gray-800 text-gray-100 p-3 rounded mt-2 overflow-x-auto">
                                                                <code className="text-sm" {...props} />
                                                            </pre>
                                                        );
                                                    }
                                                },
                                                h1: ({node, ...props}) => <h1 className="text-xl font-bold mb-2" {...props} />,
                                                h2: ({node, ...props}) => <h2 className="text-lg font-bold mb-2" {...props} />,
                                                h3: ({node, ...props}) => <h3 className="text-base font-bold mb-2" {...props} />,
                                                blockquote: ({node, ...props}) => (
                                                    <blockquote className="border-l-4 border-primary pl-4 italic text-gray-600" {...props} />
                                                ),
                                            }}
                                        >
                                            {msg.content}
                                        </ReactMarkdown>
                                    )}
                                </div>
                            </div>
                        ))}
                        {loading && (
                            <div className="flex justify-start">
                                <div className="bg-muted p-3 rounded-lg rounded-tl-none text-sm flex gap-1 items-center">
                                    <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                    <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                    <span className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </CardContent>
                    <CardFooter className="p-3 border-t">
                        <form onSubmit={handleSend} className="flex w-full gap-2">
                            <input
                                type="text"
                                className="flex-1 px-3 py-2 rounded-md border text-sm"
                                placeholder="Ask about stocks, trends..."
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                disabled={loading}
                            />
                            <Button type="submit" size="icon" disabled={loading || !input.trim()}>
                                <Send size={18} />
                            </Button>
                        </form>
                    </CardFooter>
                </Card>
            )}

            <Button
                onClick={toggleChat}
                className="h-14 w-14 rounded-full shadow-xl hover:scale-105 transition-transform bg-primary text-primary-foreground"
            >
                {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
            </Button>
        </div>
    );
};

export default ChatWidget;
