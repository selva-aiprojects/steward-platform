import React from 'react';
import { NavLink } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import { Sun, Moon, LayoutDashboard, Briefcase, ExternalLink, ShieldCheck } from 'lucide-react';

const Navbar: React.FC = () => {
    const { theme, toggleTheme } = useTheme();

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
                <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="nav-item">
                    <ExternalLink size={18} />
                    <span>API Docs</span>
                </a>
            </div>

            <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle Theme">
                {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
            </button>

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
