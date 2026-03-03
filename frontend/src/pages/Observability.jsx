import React, { useEffect, useMemo, useState } from "react";
import { useUser } from "../context/UserContext";
import { fetchMetricsSummary, fetchSupersetEmbedUrl } from "../services/api";

const DEFAULT_GRAFANA = "http://localhost:3001";
const DEFAULT_SUPERSET = "http://localhost:8088";
const DEFAULT_GRAFANA_UID = "superadmin-observability";

export default function Observability() {
  const { user, isSuperAdmin } = useUser();
  const [tab, setTab] = useState("grafana");
  const [summary, setSummary] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [embedUrl, setEmbedUrl] = useState(null);
  const [grafanaEmbedUrl, setGrafanaEmbedUrl] = useState(null);

  const grafanaBase = process.env.REACT_APP_GRAFANA_URL || DEFAULT_GRAFANA;
  const supersetBase = process.env.REACT_APP_SUPERSET_URL || DEFAULT_SUPERSET;
  const grafanaUid = process.env.REACT_APP_GRAFANA_DASHBOARD_UID || DEFAULT_GRAFANA_UID;

  const grafanaUrl = useMemo(() => {
    if (grafanaEmbedUrl) return grafanaEmbedUrl;
    // If grafanaBase is a full share URL (contains /d/ or is from grafana.net), return it as is
    if (grafanaBase.includes('/d/') || grafanaBase.includes('grafana.net')) {
      return grafanaBase;
    }
    return `${grafanaBase}/d/${grafanaUid}/${grafanaUid}?orgId=1&kiosk&refresh=5s`;
  }, [grafanaBase, grafanaUid, grafanaEmbedUrl]);
  const supersetUrl = useMemo(() => {
    if (embedUrl) return embedUrl;
    return (
      process.env.REACT_APP_SUPERSET_URL ||
      `${supersetBase}/superset/dashboard/stocksteward-executive-overview/`
    );
  }, [embedUrl, supersetBase]);

  useEffect(() => {
    let mounted = true;
    const loadSummary = async () => {
      const data = await fetchMetricsSummary();
      if (!mounted) return;
      if (data) {
        setSummary(data);
        setLastUpdated(new Date());
      }
    };
    loadSummary();
    const interval = setInterval(loadSummary, 10000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    let mounted = true;
    const loadEmbedUrl = async () => {
      const data = await fetchSupersetEmbedUrl();
      if (!mounted) return;
      if (data?.superset_url) {
        setEmbedUrl(data.superset_url);
      }
      if (data?.grafana_url) {
        setGrafanaEmbedUrl(data.grafana_url);
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
        <div className="h-20 w-20 bg-rose-50 text-rose-500 rounded-3xl flex items-center justify-center mx-auto mb-6">
          <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10" /><path d="m9 12 2 2 4-4" /></svg>
        </div>
        <h2 className="text-2xl font-black text-slate-900 mb-2">Access Restrained</h2>
        <p className="text-slate-500 mb-6">
          Your current role (<span className="text-rose-600 font-bold">{user?.role}</span>) does not possess the <span className="font-bold text-slate-900">SUPERADMIN</span> clearance required for the executive control room.
        </p>
        <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 text-left">
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Troubleshooting Information</p>
          <ul className="text-xs text-slate-600 space-y-1 font-medium">
            <li>• User ID: {user?.id}</li>
            <li>• Email: {user?.email}</li>
            <li>• Normalized Role: {user?.role}</li>
          </ul>
        </div>
      </div>
    );
  }

  const isLocalOnProd = (window.location.hostname !== 'localhost' &&
    (grafanaUrl.includes('localhost') || supersetUrl.includes('localhost')));

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-200 bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-900 text-white p-8 shadow-2xl">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
          <div>
            <h2 className="text-xs font-black uppercase tracking-[0.4em] text-indigo-200">Superadmin Control Room</h2>
            <h1 className="text-3xl md:text-4xl font-black leading-tight mt-2">
              System Observability
            </h1>
            <p className="text-sm text-indigo-100/80 mt-2 max-w-2xl">
              Live market pulse, strategy progression, and business intelligence with executive-grade clarity.
            </p>
          </div>
          <div className="flex items-center gap-2 bg-white/10 border border-white/20 rounded-2xl p-2">
            <button
              onClick={() => setTab("grafana")}
              className={`px-4 py-2 text-xs font-black uppercase tracking-widest rounded-xl transition-all ${tab === "grafana"
                ? "bg-white text-slate-900"
                : "text-white/70 hover:text-white"
                }`}
            >
              Live System
            </button>
            <button
              onClick={() => setTab("superset")}
              className={`px-4 py-2 text-xs font-black uppercase tracking-widest rounded-xl transition-all ${tab === "superset"
                ? "bg-white text-slate-900"
                : "text-white/70 hover:text-white"
                }`}
            >
              Business Intel
            </button>
          </div>
        </div>
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          <div className="rounded-2xl bg-white/10 border border-white/15 p-4">
            <p className="text-[10px] uppercase tracking-widest text-indigo-200 font-black">System Status</p>
            <p className="text-2xl font-black mt-2">
              {summary?.overall_status || "CHECKING"}
            </p>
            <p className="text-xs text-indigo-100/70 mt-1">Aggregated health signal</p>
          </div>
          <div className="rounded-2xl bg-white/10 border border-white/15 p-4">
            <p className="text-[10px] uppercase tracking-widest text-indigo-200 font-black">Total Requests</p>
            <p className="text-2xl font-black mt-2">
              {summary?.headline?.total_requests ?? "—"}
            </p>
            <p className="text-xs text-indigo-100/70 mt-1">All API traffic</p>
          </div>
          <div className="rounded-2xl bg-white/10 border border-white/15 p-4">
            <p className="text-[10px] uppercase tracking-widest text-indigo-200 font-black">Provider Failure</p>
            <p className="text-2xl font-black mt-2">
              {summary?.headline?.external_failure_rate_pct != null
                ? `${summary.headline.external_failure_rate_pct}%`
                : "—"}
            </p>
            <p className="text-xs text-indigo-100/70 mt-1">External services</p>
          </div>
          <div className="rounded-2xl bg-white/10 border border-white/15 p-4">
            <p className="text-[10px] uppercase tracking-widest text-indigo-200 font-black">Strategy Success</p>
            <p className="text-2xl font-black mt-2">
              {summary?.headline?.strategy_update_success_rate_pct != null
                ? `${summary.headline.strategy_update_success_rate_pct}%`
                : "—"}
            </p>
            <p className="text-xs text-indigo-100/70 mt-1">LLM-driven updates</p>
          </div>
        </div>
        <div className="mt-4 text-[10px] uppercase tracking-[0.2em] text-indigo-200/70">
          {lastUpdated ? `Updated ${lastUpdated.toLocaleTimeString()}` : "Updating..."}
        </div>
      </div>

      {isLocalOnProd && (
        <div className="p-6 rounded-2xl bg-amber-50 border border-amber-200 text-amber-800 animate-pulse">
          <div className="flex items-center gap-3">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" /><path d="M12 9v4" /><path d="M12 17h.01" /></svg>
            <h3 className="font-black uppercase text-xs tracking-widest">Localhost URL Detected in Production</h3>
          </div>
          <p className="text-xs mt-2 font-medium opacity-80">
            The dashboard URLs current point to <span className="font-bold underline">localhost</span>.
            When using the platform on Render, you must configure <span className="font-mono bg-white/50 px-1">REACT_APP_GRAFANA_URL</span> and <span className="font-mono bg-white/50 px-1">REACT_APP_SUPERSET_URL</span>
            in your environment variables to point to your live observability instances.
          </p>
        </div>
      )}

      <div className="rounded-2xl border border-slate-100 bg-white shadow-sm overflow-hidden">
        {tab === "grafana" ? (
          <div className="h-[80vh]">
            <iframe
              title="Grafana Superadmin Observability"
              src={grafanaUrl}
              className="w-full h-full"
              frameBorder="0"
              allow="fullscreen"
            />
          </div>
        ) : (
          <div className="h-[80vh]">
            <iframe
              title="Superset Business Intelligence"
              src={supersetUrl}
              className="w-full h-full"
              frameBorder="0"
              allow="fullscreen"
            />
          </div>
        )}
      </div>

      <div className="text-xs text-slate-500">
        If you want Superset to open a specific dashboard, set
        <span className="font-mono"> REACT_APP_SUPERSET_URL</span> to that dashboard URL.
      </div>
    </div>
  );
}
