import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { motion } from "framer-motion";
import { TrendingUp, AlertCircle } from "lucide-react";

export default function AnomalyTimeline({ data }) {
  // Ensure we have enough points
  const displayData = data.length < 2 ? [
    { score: 0, timestamp: '00:00:00' },
    { score: 0, timestamp: '00:00:01' }
  ] : [...data].reverse();

  const maxScore = Math.max(...displayData.map(d => d.score), 0);
  const isAnomalous = maxScore > 70;

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl h-full flex flex-col justify-between glass-card shadow-2xl relative overflow-hidden">
      {/* Decorative gradient for the background */}
      <div className={`absolute top-0 right-0 w-64 h-64 rounded-full blur-[100px] pointer-events-none transition-colors duration-1000 ${isAnomalous ? 'bg-red-500/10' : 'bg-lime-500/10'}`}></div>

      <div className="flex justify-between items-start mb-4 relative z-10">
        <div>
          <h2 className="text-white font-bold text-xl flex items-center gap-2">
            <TrendingUp size={20} className={isAnomalous ? "text-red-500" : "text-lime-400"} />
            Anomaly Timeline
          </h2>
          <p className="text-gray-500 text-[10px] font-bold uppercase tracking-widest mt-1">Live Threat Propagation</p>
        </div>
        {isAnomalous && (
          <motion.div 
            animate={{ opacity: [0, 1, 0] }}
            transition={{ duration: 1, repeat: Infinity }}
            className="flex items-center gap-1 bg-red-500/20 text-red-500 px-3 py-1 rounded-full text-[10px] font-black border border-red-500/30 shadow-[0_0_15px_rgba(239,68,68,0.3)]"
          >
            <AlertCircle size={12} /> SPIKE DETECTED
          </motion.div>
        )}
      </div>

      <div className="flex-1 w-full mt-2 relative z-10" style={{ minHeight: 0 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={displayData}>
            <defs>
              <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={isAnomalous ? "#ef4444" : "#a3e635"} stopOpacity={0.6}/>
                <stop offset="95%" stopColor={isAnomalous ? "#ef4444" : "#a3e635"} stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.03)" vertical={false} />
            <XAxis 
              dataKey="timestamp" 
              hide={true}
            />
            <YAxis 
              domain={[0, 100]} 
              stroke="rgba(255,255,255,0.1)" 
              fontSize={10}
              tickFormatter={(val) => `${val}%`}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#000', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px' }}
              itemStyle={{ color: '#fff', fontSize: '12px' }}
              labelStyle={{ display: 'none' }}
            />
            <Area 
              type="monotone" 
              dataKey="score" 
              stroke={isAnomalous ? "#ef4444" : "#a3e635"} 
              strokeWidth={3}
              fillOpacity={1} 
              fill="url(#colorRisk)" 
              animationDuration={1000}
              isAnimationActive={true}
            />
            {/* Anomaly Reference Line */}
            <ReferenceLine y={70} stroke="rgba(239,68,68,0.3)" strokeDasharray="5 5" label={{ position: 'right', value: 'ALERT', fill: 'rgba(239,68,68,0.5)', fontSize: 8 }} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 flex justify-between items-center relative z-10">
        <div className="flex gap-4">
          <div className="flex flex-col">
            <span className="text-[8px] text-gray-500 uppercase font-black">Current Spike</span>
            <span className={`text-sm font-black ${isAnomalous ? 'text-red-500' : 'text-white'}`}>
              {Math.round(displayData[displayData.length - 1]?.score || 0)}%
            </span>
          </div>
          <div className="flex flex-col">
            <span className="text-[8px] text-gray-500 uppercase font-black">Volatility</span>
            <span className="text-sm font-black text-white">±14.2%</span>
          </div>
        </div>
        <div className="bg-white/5 px-3 py-1 rounded-full border border-white/10">
          <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Node: 0xA4...12</span>
        </div>
      </div>
    </div>
  );
}
