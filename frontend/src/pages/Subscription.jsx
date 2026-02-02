import React, { useState } from 'react';
import { Card } from "../components/ui/card";
import { Check, X, Zap, Shield, Globe, Award } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useUser } from "../context/UserContext";

const TIERS = [
    {
        id: 'starter',
        name: 'Starter Agent',
        price: 'Free',
        description: 'Perfect for testing the AI waters.',
        features: [
            'Basic Stock Analysis',
            'Daily Portfolio Updates',
            '1 Connected Brokerage',
            'Community Support'
        ],
        unavailable: [
            'Real-time Websocket Data',
            'Automated Trade Execution',
            'Priority Execution Nodes',
            'Dedicated Account Manager'
        ],
        color: 'bg-slate-50',
        btnColor: 'bg-slate-900',
        icon: Globe
    },
    {
        id: 'pro',
        name: 'Pro Steward',
        price: '₹3,999/mo',
        description: 'For serious investors requiring automation.',
        popular: true,
        features: [
            'Real-time Market Data',
            'Unlimited AI Trade Execution',
            '5 Connected Brokerages',
            'Tax-Loss Harvesting',
            'Advanced Risk Metrics'
        ],
        unavailable: [
            'White-label Reports',
            'API Access'
        ],
        color: 'bg-indigo-50/50 border-indigo-100',
        btnColor: 'bg-primary',
        icon: Zap
    },
    {
        id: 'enterprise',
        name: 'Enterprise',
        price: 'Custom',
        description: 'Full-scale infrastructure for funds.',
        features: [
            'Everything in Pro',
            'White-label PDF Reports',
            'Direct Market Access (DMA)',
            'Dedicated Success Manager',
            'Custom Risk Models',
            'SLA 99.99% Uptime'
        ],
        unavailable: [],
        color: 'bg-slate-900 text-white',
        btnColor: 'bg-white text-slate-900',
        icon: Shield
    }
];

export default function Subscription() {
    const navigate = useNavigate();
    const { user } = useUser();
    const [billingCycle, setBillingCycle] = useState('monthly');

    return (
        <div className="max-w-6xl mx-auto space-y-12 animate-in fade-in duration-500 pb-20">
            <div className="text-center space-y-4">
                <h1 className="text-4xl font-black text-slate-900 font-heading">Upgrade Your Intelligence</h1>
                <p className="text-slate-500 max-w-2xl mx-auto text-lg">
                    Unlock the full potential of StockSteward AI with our enterprise-grade infrastructure tiers.
                </p>

                <div className="flex justify-center mt-8">
                    <div className="bg-slate-100 p-1 rounded-xl flex">
                        <button
                            onClick={() => setBillingCycle('monthly')}
                            className={`px-6 py-2 rounded-lg text-sm font-bold transition-all ${billingCycle === 'monthly' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-500 hover:text-slate-900'}`}
                        >
                            Monthly
                        </button>
                        <button
                            onClick={() => setBillingCycle('annual')}
                            className={`px-6 py-2 rounded-lg text-sm font-bold transition-all flex items-center gap-2 ${billingCycle === 'annual' ? 'bg-white shadow-sm text-slate-900' : 'text-slate-500 hover:text-slate-900'}`}
                        >
                            Annual <span className="text-[10px] bg-green-100 text-green-700 px-2 py-0.5 rounded-full uppercase tracking-wider">Save 20%</span>
                        </button>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {TIERS.map((tier) => (
                    <Card key={tier.id} className={`p-8 relative overflow-hidden transition-all hover:shadow-2xl hover:-translate-y-2 border-slate-200 ${tier.color} ${tier.popular ? 'ring-2 ring-primary ring-offset-2' : ''}`}>
                        {tier.popular && (
                            <div className="absolute top-0 right-0 bg-primary text-white text-[10px] font-black uppercase tracking-widest px-4 py-1 rounded-bl-xl">
                                Most Popular
                            </div>
                        )}

                        <div className={`p-3 rounded-2xl w-fit mb-6 ${tier.id === 'enterprise' ? 'bg-white/10 text-white' : 'bg-white shadow-sm text-slate-900'}`}>
                            <tier.icon size={24} />
                        </div>

                        <h3 className={`text-xl font-black mb-2 ${tier.id === 'enterprise' ? 'text-white' : 'text-slate-900'}`}>{tier.name}</h3>
                        <p className={`text-sm mb-6 ${tier.id === 'enterprise' ? 'text-slate-400' : 'text-slate-500'}`}>{tier.description}</p>

                        <div className="mb-8">
                            <span className={`text-4xl font-black ${tier.id === 'enterprise' ? 'text-white' : 'text-slate-900'}`}>{tier.price}</span>
                            {tier.price !== 'Free' && tier.price !== 'Custom' && <span className={`ml-1 text-sm ${tier.id === 'enterprise' ? 'text-slate-500' : 'text-slate-400'}`}>/{billingCycle === 'monthly' ? 'mo' : 'yr'}</span>}
                        </div>

                        <button
                            onClick={() => {
                                window.alert('Order Initiated: StockSteward Agent Provisioning in progress...');
                                navigate('/');
                            }}
                            className={`w-full py-4 rounded-xl font-black text-sm uppercase tracking-widest transition-all hover:opacity-90 mb-8 shadow-lg ${tier.btnColor}`}
                        >
                            {tier.price === 'Custom' ? 'Contact Sales' : 'Get Started'}
                        </button>

                        <div className="space-y-4">
                            <p className="text-[10px] font-black uppercase tracking-widest opacity-50">Features</p>
                            {tier.features.map((feature, i) => (
                                <div key={i} className="flex items-center gap-3">
                                    <div className={`p-0.5 rounded-full ${tier.id === 'enterprise' ? 'bg-green-500/20 text-green-400' : 'bg-green-100 text-green-700'}`}>
                                        <Check size={12} />
                                    </div>
                                    <span className={`text-sm font-medium ${tier.id === 'enterprise' ? 'text-slate-300' : 'text-slate-600'}`}>{feature}</span>
                                </div>
                            ))}
                            {tier.unavailable.map((feature, i) => (
                                <div key={i} className="flex items-center gap-3 opacity-40">
                                    <div className="p-0.5 rounded-full bg-slate-100 text-slate-400">
                                        <X size={12} />
                                    </div>
                                    <span className={`text-sm font-medium ${tier.id === 'enterprise' ? 'text-slate-500' : 'text-slate-500'}`}>{feature}</span>
                                </div>
                            ))}
                        </div>
                    </Card>
                ))}
            </div>

            <div className="mt-12 p-8 rounded-3xl bg-slate-50 border border-slate-100 flex flex-col md:flex-row items-center justify-between gap-8">
                <div className="flex items-center gap-6">
                    <div className="p-4 bg-white rounded-2xl shadow-sm text-yellow-500">
                        <Award size={32} />
                    </div>
                    <div>
                        <h4 className="font-black text-slate-900 text-lg">Enterprise Compliance Guarantee</h4>
                        <p className="text-sm text-slate-500">All paid tiers include our SOC2 Type II compliance audit reports and detailed SLA documentation.</p>
                    </div>
                </div>
                <div className="flex gap-4">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Stripe_Logo%2C_revised_2016.svg/2560px-Stripe_Logo%2C_revised_2016.svg.png" alt="Stripe" className="h-8 opacity-50 grayscale hover:grayscale-0 transition-all cursor-pointer" />
                    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/PayPal.svg/2560px-PayPal.svg.png" alt="PayPal" className="h-8 opacity-50 grayscale hover:grayscale-0 transition-all cursor-pointer" />
                </div>
            </div>
        </div>
    );
}
