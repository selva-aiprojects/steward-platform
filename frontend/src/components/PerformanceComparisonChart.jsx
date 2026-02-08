// frontend/src/components/PerformanceComparisonChart.jsx
import React from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';

export function PerformanceComparisonChart({ data = [] }) {
  // Default mock data if none provided
  const chartData = data.length > 0 ? data : [
    { date: 'Jan', algo: 100000, manual: 100000 },
    { date: 'Feb', algo: 102500, manual: 101200 },
    { date: 'Mar', algo: 105800, manual: 102800 },
    { date: 'Apr', algo: 108900, manual: 104100 },
    { date: 'May', algo: 112300, manual: 105600 },
    { date: 'Jun', algo: 115200, manual: 106800 },
    { date: 'Jul', algo: 118700, manual: 108200 },
    { date: 'Aug', algo: 122400, manual: 109500 },
    { date: 'Sep', algo: 126800, manual: 111200 },
    { date: 'Oct', algo: 131500, manual: 112800 },
    { date: 'Nov', algo: 136200, manual: 114500 },
    { date: 'Dec', algo: 141800, manual: 116200 }
  ];

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 border border-slate-200 shadow-lg rounded-lg">
          <p className="font-black text-slate-900">{`Date: ${label}`}</p>
          <p className="text-green-600">{`Algorithmic: ₹${payload[0]?.value?.toLocaleString()}`}</p>
          <p className="text-blue-600">{`Manual: ₹${payload[1]?.value?.toLocaleString()}`}</p>
          <p className="text-slate-700">{`Difference: ₹${(payload[0]?.value - payload[1]?.value)?.toLocaleString()}`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-96 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={chartData}
          margin={{
            top: 10,
            right: 30,
            left: 0,
            bottom: 0,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
          <XAxis 
            dataKey="date" 
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: '#64748b' }}
          />
          <YAxis 
            axisLine={false}
            tickLine={false}
            tick={{ fontSize: 12, fill: '#64748b' }}
            tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}K`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Area
            type="monotone"
            dataKey="algo"
            stackId="1"
            stroke="#10b981"
            fill="url(#colorAlgo)"
            strokeWidth={3}
            name="Algorithmic Performance"
          />
          <Area
            type="monotone"
            dataKey="manual"
            stackId="2"
            stroke="#3b82f6"
            fill="url(#colorManual)"
            strokeWidth={3}
            name="Manual Performance"
          />
          <defs>
            <linearGradient id="colorAlgo" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
              <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
            </linearGradient>
            <linearGradient id="colorManual" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
          </defs>
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export default PerformanceComparisonChart;