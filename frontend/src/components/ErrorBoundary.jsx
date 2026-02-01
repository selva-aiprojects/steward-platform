import React from 'react';
import { Card } from "./ui/card";
import { AlertCircle, RefreshCw } from 'lucide-react';

export class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        this.setState({ errorInfo });
        // Log error to console - in prod this would go to Sentry/LogRocket
        console.error("Uncaught error:", error, errorInfo);

        // Attempt to log to backend
        // self-contained fetch to avoid import dependencies in error state
        try {
            const url = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
            fetch(`${url}/logs/error`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    level: 'CRITICAL',
                    message: error.toString(),
                    context: { componentStack: errorInfo.componentStack },
                    source: 'Frontend-ErrorBoundary'
                })
            }).catch(e => console.error("Failed to log error to backend:", e));
        } catch (e) {
            // Silent fail for logging
        }
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen flex items-center justify-center p-4 bg-slate-50">
                    <Card className="max-w-md w-full p-8 shadow-xl border-red-100 bg-white">
                        <div className="flex flex-col items-center text-center">
                            <div className="p-4 bg-red-50 rounded-full mb-4 text-red-500">
                                <AlertCircle size={48} />
                            </div>
                            <h1 className="text-xl font-black text-slate-900 mb-2">System Application Error</h1>
                            <p className="text-sm text-slate-500 mb-6 leading-relaxed">
                                The AI Dashboard encountered an unexpected state. This event has been securely logged for audit.
                            </p>

                            <div className="w-full bg-slate-50 p-4 rounded-lg border border-slate-100 mb-6 text-left overflow-auto max-h-32">
                                <code className="text-[10px] font-mono text-red-500 break-all">
                                    {this.state.error && this.state.error.toString()}
                                </code>
                            </div>

                            <button
                                onClick={() => window.location.reload()}
                                className="w-full py-3 bg-[#0A2A4D] hover:bg-[#0A2A4D]/90 text-white rounded-xl font-bold flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-900/20"
                            >
                                <RefreshCw size={16} />
                                Reboot System Interface
                            </button>
                        </div>
                    </Card>
                </div>
            );
        }

        return this.props.children;
    }
}
