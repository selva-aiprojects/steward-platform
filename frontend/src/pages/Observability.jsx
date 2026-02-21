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

  const grafanaBase = process.env.REACT_APP_GRAFANA_URL || DEFAULT_GRAFANA;
  const supersetBase = process.env.REACT_APP_SUPERSET_URL || DEFAULT_SUPERSET;
  const grafanaUid = process.env.REACT_APP_GRAFANA_DASHBOARD_UID || DEFAULT_GRAFANA_UID;
  const grafanaUrl = useMemo(
    () => `${grafanaBase}/d/${grafanaUid}/${grafanaUid}?orgId=1&kiosk&refresh=5s`,
    [grafanaBase, grafanaUid]
  );
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
      <div className="p-6 rounded-2xl bg-white border border-slate-100 shadow-sm">
        <h2 className="text-sm font-black text-slate-400 uppercase tracking-[0.2em] mb-2">
          Superadmin Only
        </h2>
        <p className="text-slate-600 text-sm">
          Observability dashboards are restricted to superadmin access.
        </p>
      </div>
    );
  }

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
              className={`px-4 py-2 text-xs font-black uppercase tracking-widest rounded-xl transition-all ${
                tab === "grafana"
                  ? "bg-white text-slate-900"
                  : "text-white/70 hover:text-white"
              }`}
            >
              Live System
            </button>
            <button
              onClick={() => setTab("superset")}
              className={`px-4 py-2 text-xs font-black uppercase tracking-widest rounded-xl transition-all ${
                tab === "superset"
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
