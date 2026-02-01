import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Briefcase, ArrowUpRight, ArrowDownRight } from 'lucide-react';

const mockHoldings = [
  { symbol: 'AAPL', quantity: 10, avgPrice: 175.50, currentPrice: 182.30, pnl: 68.00, pnlPct: 3.87 },
  { symbol: 'TSLA', quantity: 5, avgPrice: 240.20, currentPrice: 235.10, pnl: -25.50, pnlPct: -2.12 },
  { symbol: 'MSFT', quantity: 15, avgPrice: 380.00, currentPrice: 405.20, pnl: 378.00, pnlPct: 6.63 },
  { symbol: 'NIFTY50', quantity: 100, avgPrice: 2200.00, currentPrice: 2250.40, pnl: 5040.00, pnlPct: 2.29 },
];

const allocationData = [
  { name: 'Technology', value: 65 },
  { name: 'Automotive', value: 15 },
  { name: 'Index Funds', value: 20 },
];

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'];

const Portfolio: React.FC = () => {
  return (
    <div className="portfolio-container">
      <header className="page-header">
        <div className="header-eyebrow">
          <span className="badge-virtual">VIRTUAL HOLDINGS</span>
        </div>
        <h1>Simulated Portfolio</h1>
        <p>Detailed breakdown of your virtual assets and positions.</p>
      </header>

      <div className="portfolio-grid">
        <div className="holdings-section">
          <div className="section-header">
            <Briefcase size={20} />
            <h2>Current Holdings</h2>
          </div>
          <div className="table-wrapper">
            <table className="holdings-table">
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Quantity</th>
                  <th>Avg. Price</th>
                  <th>Current</th>
                  <th>PnL</th>
                  <th>Change</th>
                </tr>
              </thead>
              <tbody>
                {mockHoldings.map((holding) => (
                  <tr key={holding.symbol}>
                    <td className="font-bold">{holding.symbol}</td>
                    <td>{holding.quantity}</td>
                    <td>${holding.avgPrice.toFixed(2)}</td>
                    <td>${holding.currentPrice.toFixed(2)}</td>
                    <td className={holding.pnl >= 0 ? 'text-success' : 'text-danger'}>
                      {holding.pnl >= 0 ? '+' : ''}${Math.abs(holding.pnl).toFixed(2)}
                    </td>
                    <td className={holding.pnlPct >= 0 ? 'text-success-bg' : 'text-danger-bg'}>
                      <div className="pct-badge">
                        {holding.pnlPct >= 0 ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />}
                        {Math.abs(holding.pnlPct)}%
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="allocation-section">
          <h2>Asset Allocation</h2>
          <div className="pie-wrapper">
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={allocationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {allocationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend verticalAlign="bottom" height={36} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <style>{`
        .portfolio-container {
          display: flex;
          flex-direction: column;
          gap: var(--space-6);
        }

        .portfolio-grid {
          display: grid;
          grid-template-columns: 1fr 340px;
          gap: var(--space-6);
        }

        .holdings-section, .allocation-section {
          background-color: var(--bg-surface);
          padding: var(--space-6);
          border-radius: 1rem;
          border: 1px solid var(--border-subtle);
          box-shadow: var(--shadow-sm);
        }

        .section-header {
          display: flex;
          align-items: center;
          gap: var(--space-3);
          margin-bottom: var(--space-4);
          color: var(--brand-primary);
        }

        .section-header h2 {
          color: var(--text-primary);
          font-size: 1.25rem;
        }

        .table-wrapper {
          overflow-x: auto;
        }

        .holdings-table {
          width: 100%;
          border-collapse: collapse;
          text-align: left;
        }

        .holdings-table th {
          padding: var(--space-3) var(--space-4);
          color: var(--text-secondary);
          font-size: 0.75rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          border-bottom: 2px solid var(--border-subtle);
        }

        .holdings-table td {
          padding: var(--space-4);
          border-bottom: 1px solid var(--border-subtle);
          font-size: 0.875rem;
        }

        .font-bold { font-weight: 700; }
        
        .text-success { color: var(--success); }
        .text-danger { color: var(--danger); }

        .pct-badge {
          display: inline-flex;
          align-items: center;
          gap: 2px;
          padding: 2px 8px;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 700;
        }

        .text-success-bg .pct-badge {
          background-color: rgba(16, 185, 129, 0.1);
          color: var(--success);
        }

        .text-danger-bg .pct-badge {
          background-color: rgba(239, 68, 68, 0.1);
          color: var(--danger);
        }

        .pie-wrapper {
          height: 250px;
          display: flex;
          justify-content: center;
          align-items: center;
        }
      `}</style>

      <footer className="compliance-footer">
        <p>
          <strong>Compliance Disclaimer:</strong> StockSteward AI provides a simulated trading environment.
          The data displayed here does not represent real financial transactions.
          No guarantee of profits is implied or provided. Independent financial advice should be sought before
          engaging in real-market activities. All trade signals are generated for educational purposes.
        </p>
      </footer>
    </div>
  );
};

export default Portfolio;
