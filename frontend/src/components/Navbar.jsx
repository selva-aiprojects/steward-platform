import React from 'react';
import { NavLink, Link, useLocation } from 'react-router-dom';
import { useUser } from '../context/UserContext';
import { useTheme } from '../context/ThemeContext';
import {
  Sun, Moon, LayoutDashboard, Briefcase,
  ExternalLink, ShieldCheck, LogOut, Users,
  BarChart2, Zap
} from 'lucide-react';

const Navbar = () => {
  const { theme, toggleTheme } = useTheme();
  const { user, logout, isAdmin } = useUser();

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <ShieldCheck className="brand-icon" size={24} />
        <span>StockSteward AI</span>
      </div>

      <div className="nav-links">
        <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
          <LayoutDashboard size={18} />
          <span>Dashboard</span>
        </NavLink>
        <NavLink to="/portfolio" className={({ isActive }) => isActive ? 'nav-item active' : 'nav-item'}>
          <Briefcase size={18} />
          <span>Portfolio</span>
        </NavLink>
        <Link to="/reports" className={`nav-item ${location.pathname === '/reports' ? 'active' : ''}`}>
          <BarChart2 size={20} />
          <span className="font-bold">Reports</span>
        </Link>

        <div className="my-2 border-t border-white/10 mx-4" />

        <Link to="/subscription" className={`nav-item ${location.pathname === '/subscription' ? 'active' : ''} text-amber-400 hover:text-amber-300 hover:bg-amber-400/10`}>
          <Zap size={20} className="fill-amber-400/20" />
          <span className="font-black tracking-wide">UPGRADE</span>
        </Link>

        {isAdmin && (
          <Link to="/users" className={`nav-item ${location.pathname === '/users' ? 'active' : ''}`}>
            <Users size={18} />
            <span>User Mgmt</span>
          </Link>
        )}

        <a href={`${process.env.REACT_APP_API_URL ? process.env.REACT_APP_API_URL.replace('/api/v1', '') : 'http://localhost:8000'}/docs`} target="_blank" rel="noopener noreferrer" className="nav-item">
          <ExternalLink size={18} />
          <span>API Docs</span>
        </a>
      </div>

      <div className="mt-auto flex flex-col gap-2">
        {user && (
          <div className="p-3 rounded-lg bg-white/5 border border-white/10 mb-2">
            <div className="flex items-center gap-2 mb-1">
              <div className="h-8 w-8 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 flex items-center justify-center font-bold text-xs">
                {user.avatar || 'U'}
              </div>
              <div className="overflow-hidden">
                <p className="text-xs font-bold text-white truncate">{user.name}</p>
                <p className="text-[10px] text-slate-400 font-mono">{user.role}</p>
              </div>
            </div>
          </div>
        )}

        <div className="flex gap-2">
          <button className="theme-toggle flex-1" onClick={toggleTheme} aria-label="Toggle Theme">
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
          </button>
          <button className="theme-toggle flex-[2] bg-red-500/10 hover:bg-red-500/20 border-red-500/20 text-red-400 gap-2" onClick={logout} aria-label="Logout">
            <LogOut size={16} />
            <span className="text-xs font-bold uppercase tracking-wider">Logout</span>
          </button>
        </div>
      </div>

      <style>{`
        .navbar {
          height: 100vh;
          width: 240px;
          background-color: var(--bg-sidebar);
          color: var(--text-on-dark);
          padding: var(--space-6) var(--space-4);
          display: flex;
          flex-direction: column;
          position: fixed;
          left: 0;
          top: 0;
          border-right: 1px solid var(--border-subtle);
        }

        .nav-brand {
          display: flex;
          align-items: center;
          gap: var(--space-3);
          font-size: 1.25rem;
          font-weight: 800;
          color: var(--brand-primary-light);
          margin-bottom: var(--space-8);
        }

        .nav-links {
          display: flex;
          flex-direction: column;
          gap: var(--space-2);
          flex: 1;
        }

        .nav-item {
          display: flex;
          align-items: center;
          gap: var(--space-3);
          padding: var(--space-3) var(--space-4);
          border-radius: 0.75rem;
          text-decoration: none;
          color: var(--text-muted);
          transition: var(--transition-fast);
          font-weight: 500;
        }

        .nav-item:hover {
          background-color: rgba(255, 255, 255, 0.05);
          color: var(--text-on-dark);
        }

        .nav-item.active {
          background-color: var(--brand-primary);
          color: white;
        }

        .theme-toggle {
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid var(--border-subtle);
          color: var(--text-on-dark);
          padding: var(--space-3);
          border-radius: 0.75rem;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: var(--transition-fast);
          margin-top: auto;
        }

        .theme-toggle:hover {
          background: rgba(255, 255, 255, 0.1);
        }
      `}</style>
    </nav>
  );
};

export default Navbar;
