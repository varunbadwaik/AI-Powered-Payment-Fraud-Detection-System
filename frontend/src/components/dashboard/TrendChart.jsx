import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';

export default function TrendChart({ data }) {
  // Use recent transactions for the trend line
  const chartData = [...data].reverse().map((tx, i) => ({
    time: i,
    score: tx.score
  }));

  // Dummy data if empty
  const defaultData = [
    { time: 1, score: 20 }, { time: 2, score: 40 }, { time: 3, score: 30 },
    { time: 4, score: 70 }, { time: 5, score: 50 }, { time: 6, score: 90 },
    { time: 7, score: 40 }, { time: 8, score: 60 }
  ];

  const finalData = chartData.length > 0 ? chartData : defaultData;
  const currentScore = finalData[finalData.length - 1]?.score || 0;

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl h-full flex flex-col justify-between glass-card shadow-lg relative overflow-hidden">
      {/* Decorative gradient */}
      <div className="absolute top-0 right-0 w-64 h-64 bg-lime-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="flex justify-between items-start mb-4 relative z-10">
        <div>
          <h2 className="text-white font-bold text-xl">Risk Index</h2>
          <p className="text-gray-500 text-sm">System Wide</p>
        </div>
        <div className="flex gap-4 text-xs font-medium text-gray-500">
          <span className="hover:text-white cursor-pointer">1D</span>
          <span className="hover:text-white cursor-pointer">3M</span>
          <span className="text-white bg-white/10 px-2 py-1 rounded-md">6M</span>
          <span className="hover:text-white cursor-pointer">1Y</span>
          <span className="hover:text-white cursor-pointer">5Y</span>
        </div>
      </div>

      <div className="w-full h-32 -ml-2">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={finalData}>
            <defs>
              <linearGradient id="colorGreen" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#A3E635" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#A3E635" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <Tooltip 
              contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }}
              itemStyle={{ color: '#A3E635' }}
            />
            <Area 
              type="monotone" 
              dataKey="score" 
              stroke="#A3E635" 
              strokeWidth={3}
              fillOpacity={1} 
              fill="url(#colorGreen)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="flex justify-between items-end mt-4">
        <div className="flex items-baseline gap-2">
          <h2 className="text-3xl font-bold text-white">{currentScore.toFixed(2)}</h2>
          <span className="text-lime-400 text-sm font-semibold">↑ 6.25%</span>
        </div>
        <div className="flex gap-2">
          <button className="bg-lime-500 hover:bg-lime-400 text-black px-6 py-2 rounded-xl font-semibold transition-colors">
            Buy
          </button>
          <button className="bg-white/10 hover:bg-white/20 text-white px-6 py-2 rounded-xl font-semibold transition-colors">
            Sell
          </button>
        </div>
      </div>
    </div>
  );
}
