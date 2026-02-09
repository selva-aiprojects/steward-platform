import React, { useState, useEffect, useRef } from 'react';
import ticketService from '../services/ticketService';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';

const Support = () => {
    const [view, setView] = useState('list'); // list, create, detail
    const [tickets, setTickets] = useState([]);
    const [selectedTicket, setSelectedTicket] = useState(null);
    const [formData, setFormData] = useState({ 
        subject: '', 
        description: '', 
        priority: 'MEDIUM' 
    });
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        fetchTickets();
    }, []);

    useEffect(() => {
        if (selectedTicket) {
            setMessages(selectedTicket.messages || []);
            scrollToBottom();
        }
    }, [selectedTicket]);

    useEffect(() => {
        scrollToBottom();
    }, [messages, view]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    const fetchTickets = async () => {
        try {
            const data = await ticketService.getTickets();
            setTickets(data);
        } catch (error) {
            console.error("Error fetching tickets:", error);
        }
    };

    const handleCreateTicket = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await ticketService.createTicket(formData);
            setFormData({ subject: '', description: '', priority: 'MEDIUM' });
            setView('list');
            fetchTickets();
        } catch (error) {
            console.error("Error creating ticket:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!newMessage.trim()) return;
        try {
            await ticketService.addMessage(selectedTicket.id, newMessage);
            // Re-fetch the ticket to get updated messages
            const updatedTicket = await ticketService.getTicket(selectedTicket.id);
            setSelectedTicket(updatedTicket);
            setMessages(updatedTicket.messages || []);
            setNewMessage('');
        } catch (error) {
            console.error("Error sending message:", error);
        }
    };

    const handleViewTicket = async (ticketId) => {
        const ticket = await ticketService.getTicket(ticketId);
        setSelectedTicket(ticket);
        setView('detail');
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'OPEN': return 'default';
            case 'IN_PROGRESS': return 'secondary';
            case 'RESOLVED': return 'default'; // Using default instead of success to avoid undefined variant
            case 'CLOSED': return 'outline';
            default: return 'default';
        }
    };

    return (
        <div className="p-6 space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold tracking-tight">Support</h1>
                {view === 'list' && (
                    <Button onClick={() => setView('create')}>Create Ticket</Button>
                )}
                {view !== 'list' && (
                    <Button 
                        variant="outline" 
                        onClick={() => { 
                            setView('list'); 
                            setSelectedTicket(null); 
                            setMessages([]); 
                        }}
                    >
                        Back to List
                    </Button>
                )}
            </div>

            {view === 'list' && (
                <div className="grid gap-4 md:grid-cols-1">
                    {tickets.length === 0 ? (
                        <Card>
                            <CardContent className="p-6 text-center text-muted-foreground">
                                No support tickets found. Create one to get started.
                            </CardContent>
                        </Card>
                    ) : (
                        tickets.map((ticket) => (
                            <Card 
                                key={ticket.id} 
                                className="cursor-pointer hover:bg-accent/50 transition-colors" 
                                onClick={() => handleViewTicket(ticket.id)}
                            >
                                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                    <CardTitle className="text-xl font-medium">
                                        {ticket.subject}
                                    </CardTitle>
                                    <Badge variant={getStatusColor(ticket.status)}>
                                        {ticket.status}
                                    </Badge>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-sm text-muted-foreground truncate">
                                        {ticket.description}
                                    </div>
                                    <div className="mt-2 text-xs text-muted-foreground">
                                        ID: #{ticket.id} • {new Date(ticket.created_at).toLocaleDateString()} • {ticket.priority}
                                    </div>
                                </CardContent>
                            </Card>
                        ))
                    )}
                </div>
            )}

            {view === 'create' && (
                <Card className="max-w-2xl mx-auto">
                    <CardHeader>
                        <CardTitle>Create New Ticket</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleCreateTicket} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-1">Subject</label>
                                <input
                                    type="text"
                                    required
                                    className="w-full p-2 rounded-md border bg-background"
                                    value={formData.subject}
                                    onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Priority</label>
                                <select
                                    className="w-full p-2 rounded-md border bg-background"
                                    value={formData.priority}
                                    onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                                >
                                    <option value="LOW">Low</option>
                                    <option value="MEDIUM">Medium</option>
                                    <option value="HIGH">High</option>
                                    <option value="URGENT">Urgent</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium mb-1">Description</label>
                                <textarea
                                    required
                                    rows="5"
                                    className="w-full p-2 rounded-md border bg-background"
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                />
                            </div>
                            <Button type="submit" disabled={loading} className="w-full">
                                {loading ? 'Creating...' : 'Submit Ticket'}
                            </Button>
                        </form>
                    </CardContent>
                </Card>
            )}

            {view === 'detail' && selectedTicket && (
                <div className="max-w-4xl mx-auto space-y-6">
                    <Card>
                        <CardHeader>
                            <div className="flex justify-between items-start">
                                <div>
                                    <CardTitle className="text-2xl">
                                        {selectedTicket.subject}
                                    </CardTitle>
                                    <div className="text-sm text-muted-foreground mt-1">
                                        Created on {new Date(selectedTicket.created_at).toLocaleString()}
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <Badge variant="outline">{selectedTicket.priority}</Badge>
                                    <Badge variant={getStatusColor(selectedTicket.status)}>
                                        {selectedTicket.status}
                                    </Badge>
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent className="border-t pt-6 mt-2">
                            <p className="whitespace-pre-wrap">{selectedTicket.description}</p>
                        </CardContent>
                    </Card>

                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold">Discussion</h3>
                        <div className="space-y-4 max-h-[500px] overflow-y-auto p-4 border rounded-lg bg-card/50">
                            {messages.length === 0 ? (
                                <p className="text-center text-muted-foreground text-sm">
                                    No messages yet.
                                </p>
                            ) : (
                                messages.map((msg) => (
                                    <div 
                                        key={msg.id} 
                                        className={`flex flex-col ${msg.user_id === selectedTicket.user_id ? 'items-end' : 'items-start'}`}
                                    >
                                        <div 
                                            className={`max-w-[80%] rounded-lg p-3 ${
                                                msg.user_id === selectedTicket.user_id 
                                                    ? 'bg-primary text-primary-foreground' 
                                                    : 'bg-muted'
                                            }`}
                                        >
                                            <p className="text-sm whitespace-pre-wrap">{msg.message}</p>
                                        </div>
                                        <span className="text-xs text-muted-foreground mt-1">
                                            {new Date(msg.created_at).toLocaleString()}
                                        </span>
                                    </div>
                                ))
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        <form onSubmit={handleSendMessage} className="flex gap-2">
                            <input
                                type="text"
                                className="flex-1 p-2 rounded-md border bg-background"
                                placeholder="Type your reply..."
                                value={newMessage}
                                onChange={(e) => setNewMessage(e.target.value)}
                            />
                            <Button type="submit" disabled={!newMessage.trim()}>
                                Send
                            </Button>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Support;