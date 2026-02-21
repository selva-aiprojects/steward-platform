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
      <div className="p-6 rounded-2xl bg-white border border-slate-100 shadow-sm">
        <h2 className="text-sm font-black text-slate-400 uppercase tracking-[0.2em] mb-2">
          Superadmin Only
        </h2>
        <p className="text-slate-600 text-sm">
          Superset reports are restricted to superadmin access.
        </p>
      </div>
    );
  }

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
