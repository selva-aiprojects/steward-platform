// frontend/src/components/TransactionStatement.jsx
import React, { useState } from 'react';

export function TransactionStatement({ transactions = [] }) {
  const [filter, setFilter] = useState('all'); // all, algo, manual
  const [sortField, setSortField] = useState('date');
  const [sortDirection, setSortDirection] = useState('desc');

  // Filter transactions
  const filteredTransactions = transactions.filter(transaction => {
    if (filter === 'all') return true;
    return transaction.strategy.toLowerCase() === filter;
  });

  // Sort transactions
  const sortedTransactions = [...filteredTransactions].sort((a, b) => {
    let aValue = a[sortField];
    let bValue = b[sortField];

    // Handle date sorting
    if (sortField === 'date') {
      aValue = new Date(aValue);
      bValue = new Date(bValue);
    }

    if (typeof aValue === 'string') {
      aValue = aValue.toLowerCase();
      bValue = bValue.toLowerCase();
    }

    if (sortDirection === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  // Calculate summary stats
  const summaryStats = {
    totalTrades: sortedTransactions.length,
    algoTrades: sortedTransactions.filter(t => t.strategy === 'ALGO').length,
    manualTrades: sortedTransactions.filter(t => t.strategy === 'MANUAL').length,
    totalPnL: sortedTransactions.reduce((sum, t) => sum + (t.pnl || 0), 0),
    avgPnL: sortedTransactions.length > 0 
      ? sortedTransactions.reduce((sum, t) => sum + (t.pnl || 0), 0) / sortedTransactions.length 
      : 0,
    winningTrades: sortedTransactions.filter(t => (t.pnl || 0) > 0).length,
    losingTrades: sortedTransactions.filter(t => (t.pnl || 0) < 0).length
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
          <p className="text-xs font-black text-slate-500 uppercase tracking-widest">Total Trades</p>
          <p className="text-xl font-black text-slate-900">{summaryStats.totalTrades}</p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <p className="text-xs font-black text-green-600 uppercase tracking-widest">Algo Trades</p>
          <p className="text-xl font-black text-green-700">{summaryStats.algoTrades}</p>
        </div>
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <p className="text-xs font-black text-blue-600 uppercase tracking-widest">Manual Trades</p>
          <p className="text-xl font-black text-blue-700">{summaryStats.manualTrades}</p>
        </div>
        <div className={`p-4 rounded-lg border ${summaryStats.totalPnL >= 0 ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
          <p className="text-xs font-black text-slate-500 uppercase tracking-widest">Total P&L</p>
          <p className={`text-xl font-black ${summaryStats.totalPnL >= 0 ? 'text-green-700' : 'text-red-700'}`}>
            {formatCurrency(summaryStats.totalPnL)}
          </p>
        </div>
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
          <p className="text-xs font-black text-slate-500 uppercase tracking-widest">Avg P&L</p>
          <p className="text-xl font-black text-slate-900">{formatCurrency(summaryStats.avgPnL)}</p>
        </div>
        <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
          <p className="text-xs font-black text-slate-500 uppercase tracking-widest">Win Rate</p>
          <p className="text-xl font-black text-slate-900">
            {summaryStats.totalTrades > 0 
              ? `${Math.round((summaryStats.winningTrades / summaryStats.totalTrades) * 100)}%` 
              : '0%'}
          </p>
        </div>
      </div>

      {/* Filters and Sorting */}
      <div className="flex flex-wrap gap-4 items-center justify-between">
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm font-black transition-all ${
              filter === 'all' 
                ? 'bg-primary text-white' 
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            All Trades
          </button>
          <button
            onClick={() => setFilter('ALGO')}
            className={`px-4 py-2 rounded-lg text-sm font-black transition-all ${
              filter === 'ALGO' 
                ? 'bg-green-100 text-green-700 border border-green-200' 
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Algorithmic
          </button>
          <button
            onClick={() => setFilter('MANUAL')}
            className={`px-4 py-2 rounded-lg text-sm font-black transition-all ${
              filter === 'MANUAL' 
                ? 'bg-blue-100 text-blue-700 border border-blue-200' 
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            Manual
          </button>
        </div>

        <div className="flex gap-2">
          <select
            value={sortField}
            onChange={(e) => setSortField(e.target.value)}
            className="bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm font-black text-slate-700 focus:ring-2 focus:ring-primary/20 transition-all outline-none"
          >
            <option value="date">Date</option>
            <option value="symbol">Symbol</option>
            <option value="pnl">P&L</option>
            <option value="price">Price</option>
          </select>
          <button
            onClick={() => setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')}
            className="bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm font-black text-slate-700 hover:bg-slate-50 transition-all"
          >
            {sortDirection === 'asc' ? '↑' : '↓'}
          </button>
        </div>
      </div>

      {/* Transaction Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-50">
            <tr>
              <th className="text-left py-3 px-4 font-black text-slate-400 uppercase tracking-widest text-xs">Date</th>
              <th className="text-left py-3 px-4 font-black text-slate-400 uppercase tracking-widest text-xs">Symbol</th>
              <th className="text-left py-3 px-4 font-black text-slate-400 uppercase tracking-widest text-xs">Action</th>
              <th className="text-left py-3 px-4 font-black text-slate-400 uppercase tracking-widest text-xs">Quantity</th>
              <th className="text-left py-3 px-4 font-black text-slate-400 uppercase tracking-widest text-xs">Price</th>
              <th className="text-left py-3 px-4 font-black text-slate-400 uppercase tracking-widest text-xs">Strategy</th>
              <th className="text-left py-3 px-4 font-black text-slate-400 uppercase tracking-widest text-xs">P&L</th>
              <th className="text-left py-3 px-4 font-black text-slate-400 uppercase tracking-widest text-xs">Status</th>
            </tr>
          </thead>
          <tbody>
            {sortedTransactions.length === 0 ? (
              <tr>
                <td colSpan="8" className="py-8 px-4 text-center text-slate-500">
                  No transactions found
                </td>
              </tr>
            ) : (
              sortedTransactions.map((transaction) => (
                <tr key={transaction.id} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="py-3 px-4 font-black text-slate-700">{formatDate(transaction.date)}</td>
                  <td className="py-3 px-4 font-black text-slate-900">{transaction.symbol}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-black ${
                      transaction.action === 'BUY' 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {transaction.action}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-black text-slate-700">{transaction.quantity}</td>
                  <td className="py-3 px-4 font-black text-slate-700">{formatCurrency(transaction.price)}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-black ${
                      transaction.strategy === 'ALGO' 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-blue-100 text-blue-700'
                    }`}>
                      {transaction.strategy}
                    </span>
                  </td>
                  <td className={`py-3 px-4 font-black ${
                    transaction.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatCurrency(transaction.pnl)}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-black ${
                      transaction.status === 'COMPLETED' 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-yellow-100 text-yellow-700'
                    }`}>
                      {transaction.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Performance Insights */}
      {sortedTransactions.length > 0 && (
        <div className="mt-8 p-6 bg-gradient-to-r from-green-50 to-blue-50 rounded-xl border border-green-100">
          <h4 className="text-lg font-black text-slate-900 mb-4">Performance Insights</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white p-4 rounded-lg border border-slate-200">
              <p className="text-sm font-black text-slate-700 mb-2">Algorithmic vs Manual Performance</p>
              <p className="text-lg font-black text-green-600">
                {summaryStats.algoTrades > 0 && summaryStats.manualTrades > 0
                  ? `Algo trades: ${summaryStats.algoTrades}, Manual trades: ${summaryStats.manualTrades}`
                  : 'More data needed for comparison'}
              </p>
            </div>
            <div className="bg-white p-4 rounded-lg border border-slate-200">
              <p className="text-sm font-black text-slate-700 mb-2">Winning vs Losing Trades</p>
              <p className="text-lg font-black text-slate-900">
                {summaryStats.winningTrades} wins / {summaryStats.losingTrades} losses
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default TransactionStatement;