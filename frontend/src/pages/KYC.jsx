import React, { useEffect, useMemo, useState } from "react";
import { Card } from "../components/ui/card";
import { ShieldCheck, FileText, CheckCircle2, XCircle, RefreshCw, UserPlus, BadgeCheck } from "lucide-react";
import { useUser } from "../context/UserContext";
import {
    submitKycApplication,
    fetchKycApplications,
    reviewKycApplication,
    approveKycApplication,
    rejectKycApplication
} from "../services/api";

const emptyForm = {
    full_name: "",
    email: "",
    phone: "",
    dob: "",
    pan: "",
    aadhaar_last4: "",
    address_line1: "",
    address_line2: "",
    city: "",
    state: "",
    pincode: "",
    country: "India",
    occupation: "",
    income_range: "5L-10L",
    source_of_funds: "",
    pep: false,
    sanctions: false,
    tax_residency: "India",
    bank_account_last4: "",
    ifsc: "",
    desired_role: "TRADER",
    requested_trading_mode: "AUTO",
    risk_tolerance: "MODERATE"
};

const statusStyles = {
    DRAFT: "bg-slate-100 text-slate-500",
    SUBMITTED: "bg-amber-100 text-amber-700",
    UNDER_REVIEW: "bg-blue-100 text-blue-700",
    APPROVED: "bg-emerald-100 text-emerald-700",
    REJECTED: "bg-red-100 text-red-700"
};

export function KYC() {
    const { isAdmin } = useUser();
    const [form, setForm] = useState(emptyForm);
    const [documents, setDocuments] = useState([{ type: "PAN", ref: "" }]);
    const [consents, setConsents] = useState({ accuracy: false, privacy: false, trading: false });
    const [submitting, setSubmitting] = useState(false);
    const [submitResult, setSubmitResult] = useState(null);
    const [error, setError] = useState("");

    const [applications, setApplications] = useState([]);
    const [loadingApps, setLoadingApps] = useState(false);
    const [selectedId, setSelectedId] = useState(null);
    const [reviewNote, setReviewNote] = useState("");
    const [filter, setFilter] = useState("ALL");
    const [approvalResult, setApprovalResult] = useState(null);

    const selectedApp = useMemo(() => applications.find(a => a.id === selectedId), [applications, selectedId]);

    const canSubmit = useMemo(() => {
        return (
            form.full_name &&
            form.email &&
            form.phone &&
            form.dob &&
            form.pan &&
            form.address_line1 &&
            form.city &&
            form.state &&
            form.pincode &&
            consents.accuracy &&
            consents.privacy &&
            consents.trading
        );
    }, [form, consents]);

    const loadApplications = async () => {
        setLoadingApps(true);
        const data = await fetchKycApplications();
        setApplications(Array.isArray(data) ? data : []);
        setLoadingApps(false);
    };

    useEffect(() => {
        if (isAdmin) {
            loadApplications();
        }
    }, [isAdmin]);

    const handleDocChange = (index, field, value) => {
        const next = [...documents];
        next[index] = { ...next[index], [field]: value };
        setDocuments(next);
    };

    const addDocument = () => {
        setDocuments([...documents, { type: "ADDRESS_PROOF", ref: "" }]);
    };

    const removeDocument = (index) => {
        const next = documents.filter((_, i) => i !== index);
        setDocuments(next.length ? next : [{ type: "PAN", ref: "" }]);
    };

    const handleSubmit = async () => {
        setError("");
        setSubmitResult(null);
        if (!canSubmit) {
            setError("Please complete all required fields and consents.");
            return;
        }
        setSubmitting(true);
        const payload = {
            ...form,
            documents_json: JSON.stringify(documents.filter(d => d.ref).map(d => ({
                type: d.type,
                ref: d.ref
            })))
        };
        const result = await submitKycApplication(payload);
        if (!result) {
            setError("Unable to submit KYC. Please retry or contact support.");
        } else {
            setSubmitResult(result);
            setForm(emptyForm);
            setDocuments([{ type: "PAN", ref: "" }]);
            setConsents({ accuracy: false, privacy: false, trading: false });
        }
        setSubmitting(false);
    };

    const handleReview = async (status) => {
        if (!selectedApp) return;
        const updated = await reviewKycApplication(selectedApp.id, status, reviewNote);
        if (updated) {
            setReviewNote("");
            await loadApplications();
            setSelectedId(updated.id);
        }
    };

    const handleApprove = async () => {
        if (!selectedApp) return;
        const approved = await approveKycApplication(selectedApp.id);
        if (approved) {
            setApprovalResult(approved);
            await loadApplications();
        }
    };

    const handleReject = async () => {
        if (!selectedApp) return;
        const rejected = await rejectKycApplication(selectedApp.id, reviewNote || "Rejected after compliance review.");
        if (rejected) {
            setReviewNote("");
            await loadApplications();
        }
    };

    const filteredApplications = useMemo(() => {
        if (filter === "ALL") return applications;
        return applications.filter(app => app.status === filter);
    }, [applications, filter]);

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <header className="flex flex-col gap-2">
                <h1 className="text-3xl font-black text-slate-900 font-heading">Investor KYC Center</h1>
                <p className="text-xs font-bold text-slate-500 uppercase tracking-[0.2em]">Compliance-first onboarding and role provisioning</p>
            </header>

            <Card className="p-6 border-slate-100 shadow-sm bg-white">
                <div className="flex items-start justify-between gap-6 flex-col lg:flex-row">
                    <div className="max-w-xl">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="h-12 w-12 rounded-2xl bg-emerald-50 flex items-center justify-center text-emerald-600">
                                <ShieldCheck size={24} />
                            </div>
                            <div>
                                <h2 className="text-lg font-black text-slate-900">KYC Application</h2>
                                <p className="text-xs text-slate-500 font-medium">Regulated onboarding for trading access.</p>
                            </div>
                        </div>
                        <div className="text-xs text-slate-500 leading-relaxed">
                            Submit your investor profile and compliance declarations. Our compliance team reviews and auto-provisions
                            the requested role on approval.
                        </div>
                    </div>
                    <div className="flex items-center gap-3 text-[10px] font-black uppercase tracking-widest text-slate-500">
                        <span className="px-3 py-1 rounded-full bg-slate-100">India</span>
                        <span className="px-3 py-1 rounded-full bg-slate-100">RBAC</span>
                        <span className="px-3 py-1 rounded-full bg-slate-100">Audit Trail</span>
                    </div>
                </div>
            </Card>

            <Card className="p-6 border-slate-100 shadow-sm bg-white">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="space-y-4">
                        <h3 className="text-sm font-black text-slate-600 uppercase tracking-widest">Personal Details</h3>
                        <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="Full Name *" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
                        <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="Email *" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
                        <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="Phone *" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
                        <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="Date of Birth (YYYY-MM-DD) *" value={form.dob} onChange={(e) => setForm({ ...form, dob: e.target.value })} />
                        <div className="grid grid-cols-2 gap-3">
                            <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="PAN *" value={form.pan} onChange={(e) => setForm({ ...form, pan: e.target.value.toUpperCase() })} />
                            <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="Aadhaar Last 4" value={form.aadhaar_last4} onChange={(e) => setForm({ ...form, aadhaar_last4: e.target.value })} />
                        </div>
                    </div>

                    <div className="space-y-4">
                        <h3 className="text-sm font-black text-slate-600 uppercase tracking-widest">Address</h3>
                        <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="Address Line 1 *" value={form.address_line1} onChange={(e) => setForm({ ...form, address_line1: e.target.value })} />
                        <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="Address Line 2" value={form.address_line2} onChange={(e) => setForm({ ...form, address_line2: e.target.value })} />
                        <div className="grid grid-cols-2 gap-3">
                            <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="City *" value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} />
                            <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="State *" value={form.state} onChange={(e) => setForm({ ...form, state: e.target.value })} />
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                            <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="Pincode *" value={form.pincode} onChange={(e) => setForm({ ...form, pincode: e.target.value })} />
                            <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="Country" value={form.country} onChange={(e) => setForm({ ...form, country: e.target.value })} />
                        </div>
                    </div>
                </div>
            </Card>

            <Card className="p-6 border-slate-100 shadow-sm bg-white">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div className="space-y-4">
                        <h3 className="text-sm font-black text-slate-600 uppercase tracking-widest">Financial Profile</h3>
                        <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="Occupation" value={form.occupation} onChange={(e) => setForm({ ...form, occupation: e.target.value })} />
                        <select className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" value={form.income_range} onChange={(e) => setForm({ ...form, income_range: e.target.value })}>
                            <option value="0-5L">0-5L</option>
                            <option value="5L-10L">5L-10L</option>
                            <option value="10L-25L">10L-25L</option>
                            <option value="25L+">25L+</option>
                        </select>
                        <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="Source of Funds" value={form.source_of_funds} onChange={(e) => setForm({ ...form, source_of_funds: e.target.value })} />
                        <div className="grid grid-cols-2 gap-3">
                            <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="Bank Account Last 4" value={form.bank_account_last4} onChange={(e) => setForm({ ...form, bank_account_last4: e.target.value })} />
                            <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="IFSC" value={form.ifsc} onChange={(e) => setForm({ ...form, ifsc: e.target.value.toUpperCase() })} />
                        </div>
                    </div>
                    <div className="space-y-4">
                        <h3 className="text-sm font-black text-slate-600 uppercase tracking-widest">Role & Trading Access</h3>
                        <select className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" value={form.desired_role} onChange={(e) => setForm({ ...form, desired_role: e.target.value })}>
                            <option value="TRADER">TRADER</option>
                            <option value="BUSINESS_OWNER">BUSINESS_OWNER</option>
                            <option value="AUDITOR">AUDITOR</option>
                        </select>
                        <select className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" value={form.requested_trading_mode} onChange={(e) => setForm({ ...form, requested_trading_mode: e.target.value })}>
                            <option value="AUTO">AUTO</option>
                            <option value="MANUAL">MANUAL</option>
                        </select>
                        <select className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" value={form.risk_tolerance} onChange={(e) => setForm({ ...form, risk_tolerance: e.target.value })}>
                            <option value="LOW">LOW</option>
                            <option value="MODERATE">MODERATE</option>
                            <option value="HIGH">HIGH</option>
                        </select>
                        <div className="flex items-center gap-4 text-xs text-slate-500">
                            <label className="flex items-center gap-2">
                                <input type="checkbox" checked={form.pep} onChange={(e) => setForm({ ...form, pep: e.target.checked })} />
                                Politically Exposed Person
                            </label>
                            <label className="flex items-center gap-2">
                                <input type="checkbox" checked={form.sanctions} onChange={(e) => setForm({ ...form, sanctions: e.target.checked })} />
                                Sanctions Flag
                            </label>
                        </div>
                        <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="Tax Residency" value={form.tax_residency} onChange={(e) => setForm({ ...form, tax_residency: e.target.value })} />
                    </div>
                </div>
            </Card>

            <Card className="p-6 border-slate-100 shadow-sm bg-white">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-black text-slate-600 uppercase tracking-widest">Documents</h3>
                    <button onClick={addDocument} className="text-xs font-black text-emerald-600 flex items-center gap-2">
                        <UserPlus size={14} />
                        Add Document
                    </button>
                </div>
                <div className="space-y-3">
                    {documents.map((doc, index) => (
                        <div key={`${doc.type}-${index}`} className="grid grid-cols-1 md:grid-cols-[200px_1fr_40px] gap-3 items-center">
                            <select className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" value={doc.type} onChange={(e) => handleDocChange(index, "type", e.target.value)}>
                                <option value="PAN">PAN</option>
                                <option value="AADHAAR">AADHAAR</option>
                                <option value="ADDRESS_PROOF">ADDRESS_PROOF</option>
                                <option value="BANK_PROOF">BANK_PROOF</option>
                                <option value="PHOTO">PHOTO</option>
                            </select>
                            <input className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200" placeholder="Document reference or URL" value={doc.ref} onChange={(e) => handleDocChange(index, "ref", e.target.value)} />
                            <button onClick={() => removeDocument(index)} className="h-10 w-10 rounded-xl border border-slate-200 text-slate-400 hover:text-red-500 hover:border-red-200 transition-colors">
                                <XCircle size={16} />
                            </button>
                        </div>
                    ))}
                </div>
            </Card>

            <Card className="p-6 border-slate-100 shadow-sm bg-white">
                <h3 className="text-sm font-black text-slate-600 uppercase tracking-widest mb-4">Declarations</h3>
                <div className="space-y-3 text-xs text-slate-600">
                    <label className="flex items-center gap-2">
                        <input type="checkbox" checked={consents.accuracy} onChange={(e) => setConsents({ ...consents, accuracy: e.target.checked })} />
                        I confirm the information provided is accurate and complete.
                    </label>
                    <label className="flex items-center gap-2">
                        <input type="checkbox" checked={consents.privacy} onChange={(e) => setConsents({ ...consents, privacy: e.target.checked })} />
                        I consent to KYC verification and data processing as per privacy policy.
                    </label>
                    <label className="flex items-center gap-2">
                        <input type="checkbox" checked={consents.trading} onChange={(e) => setConsents({ ...consents, trading: e.target.checked })} />
                        I understand trading access is granted only after compliance approval.
                    </label>
                </div>
                {error && <div className="mt-4 text-xs font-black text-red-600 bg-red-50 border border-red-100 px-3 py-2 rounded-lg">{error}</div>}
                {submitResult && (
                    <div className="mt-4 text-xs font-black text-emerald-700 bg-emerald-50 border border-emerald-100 px-3 py-2 rounded-lg flex items-center gap-2">
                        <CheckCircle2 size={14} />
                        Application submitted. Reference ID: {submitResult.id}
                    </div>
                )}
                <button onClick={handleSubmit} disabled={submitting || !canSubmit} className="mt-6 w-full md:w-auto px-6 py-3 rounded-xl bg-emerald-600 text-white text-xs font-black uppercase tracking-widest shadow-lg shadow-emerald-500/20 disabled:opacity-50">
                    {submitting ? "Submitting..." : "Submit KYC Application"}
                </button>
            </Card>

            {isAdmin && (
                <Card className="p-6 border-slate-100 shadow-sm bg-white">
                    <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-6">
                        <div>
                            <h3 className="text-lg font-black text-slate-900">Compliance Review Desk</h3>
                            <p className="text-xs text-slate-500">Approve, reject, or request more info for KYC submissions.</p>
                        </div>
                        <div className="flex items-center gap-3">
                            <select className="text-xs p-2 rounded-xl bg-slate-50 border border-slate-200" value={filter} onChange={(e) => setFilter(e.target.value)}>
                                <option value="ALL">All</option>
                                <option value="SUBMITTED">Submitted</option>
                                <option value="UNDER_REVIEW">Under Review</option>
                                <option value="APPROVED">Approved</option>
                                <option value="REJECTED">Rejected</option>
                            </select>
                            <button onClick={loadApplications} className="text-xs font-black px-3 py-2 rounded-xl bg-slate-900 text-white flex items-center gap-2">
                                <RefreshCw size={14} />
                                Refresh
                            </button>
                        </div>
                    </div>

                    {loadingApps ? (
                        <div className="text-xs text-slate-400 font-bold">Loading applications...</div>
                    ) : (
                        <div className="grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-6">
                            <div className="space-y-3">
                                {filteredApplications.map(app => (
                                    <button
                                        key={app.id}
                                        onClick={() => setSelectedId(app.id)}
                                        className={`w-full text-left p-4 rounded-2xl border transition-all ${selectedId === app.id ? "border-emerald-300 bg-emerald-50" : "border-slate-100 bg-white"}`}
                                    >
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="text-sm font-black text-slate-800">{app.full_name}</p>
                                                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">{app.email}</p>
                                            </div>
                                            <span className={`text-[9px] font-black uppercase tracking-widest px-2 py-1 rounded-full ${statusStyles[app.status] || "bg-slate-100 text-slate-500"}`}>
                                                {app.status}
                                            </span>
                                        </div>
                                        <div className="mt-3 flex items-center gap-2 text-[10px] text-slate-500 font-bold">
                                            <FileText size={12} />
                                            {app.desired_role} · {app.requested_trading_mode}
                                        </div>
                                    </button>
                                ))}
                                {!filteredApplications.length && (
                                    <div className="text-xs text-slate-400 font-bold">No applications available.</div>
                                )}
                            </div>

                            <div className="border border-slate-100 rounded-2xl p-6">
                                {selectedApp ? (
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <h4 className="text-lg font-black text-slate-900">{selectedApp.full_name}</h4>
                                                <p className="text-xs text-slate-500">{selectedApp.email} · {selectedApp.phone}</p>
                                            </div>
                                            <span className={`text-[10px] font-black uppercase tracking-widest px-3 py-1 rounded-full ${statusStyles[selectedApp.status] || "bg-slate-100 text-slate-500"}`}>
                                                {selectedApp.status}
                                            </span>
                                        </div>
                                        <div className="grid grid-cols-2 gap-4 text-xs text-slate-600">
                                            <div><span className="font-black uppercase text-[10px]">PAN</span><div>{selectedApp.pan || "-"}</div></div>
                                            <div><span className="font-black uppercase text-[10px]">DOB</span><div>{selectedApp.dob || "-"}</div></div>
                                            <div><span className="font-black uppercase text-[10px]">Address</span><div>{selectedApp.address_line1}, {selectedApp.city}</div></div>
                                            <div><span className="font-black uppercase text-[10px]">Role</span><div>{selectedApp.desired_role}</div></div>
                                        </div>
                                        <textarea
                                            value={reviewNote}
                                            onChange={(e) => setReviewNote(e.target.value)}
                                            placeholder="Reviewer notes / deficiencies"
                                            className="w-full text-xs p-3 rounded-xl bg-slate-50 border border-slate-200 min-h-[80px]"
                                        />
                                        <div className="flex flex-wrap gap-3">
                                            <button onClick={() => handleReview("UNDER_REVIEW")} className="px-4 py-2 rounded-xl bg-blue-600 text-white text-xs font-black uppercase tracking-widest flex items-center gap-2">
                                                <FileText size={14} />
                                                Mark Under Review
                                            </button>
                                            <button onClick={handleApprove} className="px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-black uppercase tracking-widest flex items-center gap-2">
                                                <BadgeCheck size={14} />
                                                Approve + Create User
                                            </button>
                                            <button onClick={handleReject} className="px-4 py-2 rounded-xl bg-red-600 text-white text-xs font-black uppercase tracking-widest flex items-center gap-2">
                                                <XCircle size={14} />
                                                Reject
                                            </button>
                                        </div>
                                        {approvalResult && approvalResult.kyc_id === selectedApp.id && (
                                            <div className="text-xs font-black text-emerald-700 bg-emerald-50 border border-emerald-100 px-3 py-2 rounded-lg flex items-center gap-2">
                                                <CheckCircle2 size={14} />
                                                User created: ID {approvalResult.user_id}. Temp password: {approvalResult.temp_password || "N/A"}.
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <div className="text-xs text-slate-400 font-bold">Select an application to review.</div>
                                )}
                            </div>
                        </div>
                    )}
                </Card>
            )}
        </div>
    );
}
