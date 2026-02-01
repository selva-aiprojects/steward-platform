import React, { useEffect, useState } from 'react';
import {
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area, BarChart, Bar, Cell
} from 'recharts';
import { TrendingUp, ArrowUpRight, ArrowDownRight, Activity, Loader2 } from 'lucide-react';
import { fetchPortfolioHistory, fetchDailyPnL, fetchPortfolioSummary } from '../services/api';

const Dashboard: React.FC = () => {
  const [history, setHistory] = useState<any[]>([]);
  const [pnlData, setPnlData] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setIsLoading(true);
      try {
        const [hist, pnl, summ] = await Promise.all([
          fetchPortfolioHistory(),
          fetchDailyPnL(),
          fetchPortfolioSummary()
        ]);
        setHistory(hist);
        setPnlData(pnl);
        setSummary(summ);
      } catch (error) {
        console.error("Failed to load dashboard data", error);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, []);

  if (isLoading) {
    return (
      <div className="loading-state">
        <Loader2 className="spinner" size={48} />
        <p>Syncing market data...</p>
        <style>{`
          .loading-state {
            height: 80vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
            gap: var(--space-4);
          }
          .spinner {
            animation: spin 1s linear infinite;
            color: var(--brand-primary);
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  const hasData = history.length > 0 || pnlData.length > 0;

  return (
    <div className="dashboard-container">
      <header className="page-header">
        <div className="header-eyebrow">
          <span className="badge-virtual">PAPER TRADING MODE</span>
        </div>
        <h1>Virtual Market Dashboard</h1>
        <p>Real-time oversight of your simulated agentic trading activities.</p>
      </header>

      {!hasData ? (
        <div className="empty-state">
          <h3>No Trading Activity Yet</h3>
          <p>Execute your first agentic trade to see performance metrics here.</p>
        </div>
      ) : (
        <>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-header">
                <span className="metric-label">Total Equity</span>
                <TrendingUp size={20} className="text-success" />
              </div>
              <div className="metric-value">${summary?.total_value?.toLocaleString() || '0.00'}</div>
              <div className="metric-change positive">
                <ArrowUpRight size={16} />
                <span>+5.4% session</span>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <span className="metric-label">Account Balance</span>
                <Activity size={20} className="text-primary" />
              </div>
              <div className="metric-value">${summary?.balance?.toLocaleString() || '0.00'}</div>
              <div className="metric-change">
                <span>Settled Cash</span>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <span className="metric-label">Floating PnL</span>
                <ArrowUpRight size={20} className="text-success" />
              </div>
              <div className="metric-value">+$3,250.00</div>
              <div className="metric-change positive">
                <span>Market Volatility</span>
              </div>
            </div>
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <h3>Equity Curve (Past 7 Days)</h3>
              <div className="chart-wrapper">
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={history}>
                    <defs>
                      <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="var(--brand-primary)" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="var(--brand-primary)" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-subtle)" />
                    <XAxis
                      dataKey="date_label"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                    />
                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                      tickFormatter={(value) => `$${value / 1000}k`}
                      domain={['dataMin - 1000', 'dataMax + 1000']}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--bg-surface)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: '8px',
                        color: 'var(--text-primary)'
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="equity"
                      stroke="var(--brand-primary)"
                      strokeWidth={3}
                      fillOpacity={1}
                      fill="url(#colorEquity)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="chart-card">
              <h3>Daily PnL (Session)</h3>
              <div className="chart-wrapper">
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={pnlData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-subtle)" />
                    <XAxis
                      dataKey="day"
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                    />
                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: 'var(--text-secondary)', fontSize: 12 }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'var(--bg-surface)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: '8px'
                      }}
                      cursor={{ fill: 'var(--bg-app)' }}
                    />
                    <Bar dataKey="pnl" radius={[4, 4, 0, 0]}>
                      {pnlData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.pnl >= 0 ? 'var(--success)' : 'var(--danger)'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </>
      )}

      <style>{`
        .dashboard-container {
          display: flex;
          flex-direction: column;
          gap: var(--space-6);
        }

        .metrics-grid {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: var(--space-4);
        }

        .metric-card {
          background-color: var(--bg-surface);
          padding: var(--space-4);
          border-radius: 1rem;
          border: 1px solid var(--border-subtle);
          box-shadow: var(--shadow-sm);
        }

        .metric-label {
          font-size: 0.875rem;
          font-weight: 600;
          color: var(--text-secondary);
          text-transform: uppercase;
        }

        .metric-value {
          font-size: 1.75rem;
          font-weight: 800;
          color: var(--text-primary);
          margin-top: var(--space-1);
        }

        .metric-change {
          display: flex;
          align-items: center;
          gap: var(--space-1);
          font-size: 0.875rem;
          margin-top: var(--space-2);
          font-weight: 600;
        }

        .positive { color: var(--success); }
        
        .charts-grid {
          display: grid;
          grid-template-columns: 1.5fr 1fr;
          gap: var(--space-6);
        }

        .chart-card {
          background-color: var(--bg-surface);
          padding: var(--space-6);
          border-radius: 1rem;
          border: 1px solid var(--border-subtle);
          box-shadow: var(--shadow-md);
        }

        .chart-card h3 {
          margin-bottom: var(--space-4);
          color: var(--text-primary);
          font-size: 1.1rem;
        }

        .empty-state {
          text-align: center;
          padding: var(--space-8);
          background: var(--bg-surface);
          border-radius: 1rem;
          border: 2px dashed var(--border-subtle);
          color: var(--text-secondary);
        }

        .loading-state {
          height: 80vh;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          color: var(--text-secondary);
          gap: var(--space-4);
        }
        .spinner {
          animation: spin 1s linear infinite;
          color: var(--brand-primary);
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .text-success { color: var(--success); }
        .text-primary { color: var(--brand-primary); }
        .header-eyebrow {
          margin-bottom: var(--space-2);
        }

        .badge-virtual {
          background-color: var(--warning);
          color: #000;
          font-size: 0.65rem;
          font-weight: 900;
          padding: 2px 8px;
          border-radius: 4px;
          letter-spacing: 0.1em;
          box-shadow: 0 0 10px rgba(245, 158, 11, 0.3);
        }

        .dashboard-footer {
          margin-top: var(--space-8);
          padding-top: var(--space-6);
          border-top: 1px solid var(--border-subtle);
          font-size: 0.75rem;
          color: var(--text-secondary);
          line-height: 1.5;
        }

        .dashboard-footer p {
          max-width: 800px;
        }
      `}</style>

      <footer className="dashboard-footer">
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

export default Dashboard;
