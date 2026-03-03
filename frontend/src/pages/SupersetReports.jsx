import React, { useEffect, useMemo, useState } from "react";
import { useUser } from "../context/UserContext";
import { fetchSupersetEmbedUrl } from "../services/api";
import { Link } from "react-router-dom";

const DEFAULT_SUPERSET = "http://localhost:8088";
const DEFAULT_DASHBOARD = "stocksteward-executive-overview";

export default function SupersetReports() {
  const { user, isSuperAdmin } = useUser();
  const [embedUrl, setEmbedUrl] = useState(null);
  const supersetBase = process.env.REACT_APP_SUPERSET_URL || DEFAULT_SUPERSET;
  const supersetUrl = useMemo(() => {
    if (embedUrl) return embedUrl;
    return `${supersetBase}/superset/dashboard/${DEFAULT_DASHBOARD}/`;
  }, [embedUrl, supersetBase]);

  useEffect(() => {
    let mounted = true;
    const loadEmbedUrl = async () => {
      const data = await fetchSupersetEmbedUrl();
      if (!mounted) return;
      if (data?.url) {
        setEmbedUrl(data.url);
      }
    };
    loadEmbedUrl();
    return () => {
      mounted = false;
    };
  }, []);

  if (!user) return null;

  if (!isSuperAdmin) {
    return (
      <div className="p-12 text-center bg-white rounded-3xl border border-slate-200 shadow-xl max-w-2xl mx-auto mt-12">
        <div className="h-20 w-20 bg-emerald-50 text-emerald-500 rounded-3xl flex items-center justify-center mx-auto mb-6">
          <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>
        </div>
        <h2 className="text-2xl font-black text-slate-900 mb-2">Cleared Personnel Only</h2>
        <p className="text-slate-500 mb-6">
          Superset reports contain proprietary execution logic data reserved for the <span className="font-bold text-slate-900">SUPERADMIN</span> role.
          Your role: <span className="text-rose-600 font-bold">{user?.role}</span>.
        </p>
      </div>
    );
  }

  const isLocalOnProd = (window.location.hostname !== 'localhost' && supersetUrl.includes('localhost'));

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-200 bg-gradient-to-br from-slate-900 via-slate-900 to-emerald-900 text-white p-8 shadow-2xl">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div>
            <h2 className="text-xs font-black uppercase tracking-[0.4em] text-emerald-200">
              Superadmin Reports
            </h2>
            <h1 className="text-3xl md:text-4xl font-black leading-tight mt-2">
              Superset Executive Intelligence
            </h1>
            <p className="text-sm text-emerald-100/80 mt-2 max-w-2xl">
              Business intelligence dashboards sourced from the live application database.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to="/admin/observability"
              className="px-4 py-2 text-xs font-black uppercase tracking-widest rounded-xl bg-white text-slate-900"
            >
              Open Observability
            </Link>
            <a
              href={supersetBase}
              className="px-4 py-2 text-xs font-black uppercase tracking-widest rounded-xl bg-white/10 text-white border border-white/20"
              target="_blank"
              rel="noreferrer"
            >
              Superset Console
            </a>
          </div>
        </div>
      </div>

      {isLocalOnProd && (
        <div className="p-6 rounded-2xl bg-amber-50 border border-amber-200 text-amber-800 animate-pulse">
          <div className="flex items-center gap-3">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" /><path d="M12 9v4" /><path d="M12 17h.01" /></svg>
            <h3 className="font-black uppercase text-xs tracking-widest">Superset Local URL Detected</h3>
          </div>
          <p className="text-xs mt-2 font-medium opacity-80">
            The Superset dashboard URL currently points to <span className="font-bold underline">localhost</span>.
            When using the platform on Render, you must configure <span className="font-mono bg-white/50 px-1">REACT_APP_SUPERSET_URL</span>
            in your environment variables to point to your live Superset instance.
          </p>
        </div>
      )}

      <div className="rounded-2xl border border-slate-100 bg-white shadow-sm overflow-hidden">
        <div className="h-[80vh]">
          <iframe
            title="Superset Executive Reports"
            src={supersetUrl}
            className="w-full h-full"
            frameBorder="0"
            allow="fullscreen"
          />
        </div>
      </div>

      <div className="text-xs text-slate-500">
        To pin a different Superset dashboard, set
        <span className="font-mono"> REACT_APP_SUPERSET_URL</span>.
      </div>
    </div>
  );
}
