import { motion } from "framer-motion";

export default function NeonDonut({ riskScore }) {
  const isHighRisk = riskScore > 75;
  const isMedRisk = riskScore > 40 && riskScore <= 75;
  
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (riskScore / 100) * circumference;

  // Glow color selection
  const glowColor = isHighRisk ? 'rgba(239,68,68,0.4)' : isMedRisk ? 'rgba(249,115,22,0.4)' : 'rgba(163,230,53,0.3)';
  const strokeColor = isHighRisk ? '#ef4444' : isMedRisk ? '#f97316' : '#a3e635';

  return (
    <div className={`bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl h-full flex flex-col items-center justify-center relative glass-card shadow-2xl transition-all duration-500 overflow-hidden ${isHighRisk ? 'border-red-500/30' : ''}`}>
      
      {/* Dynamic Background Glow */}
      <div 
        className="absolute inset-0 pointer-events-none transition-all duration-500" 
        style={{ background: `radial-gradient(circle at center, ${glowColor} 0%, transparent 70%)` }}
      />

      <div className="absolute top-4 text-center w-full relative z-10">
        <p className="text-gray-500 text-[10px] font-bold uppercase tracking-[0.2em]">Risk Intensity</p>
      </div>

      <div className="relative w-52 h-52 mt-4 flex items-center justify-center relative z-10">
        <svg className="transform -rotate-90 w-40 h-40" viewBox="0 0 140 140">
          {/* Track */}
          <circle
            cx="70"
            cy="70"
            r={radius}
            stroke="rgba(255,255,255,0.05)"
            strokeWidth="10"
            fill="transparent"
          />
          {/* Progress Layer 1 (Outer Glow) */}
          <motion.circle
            cx="70"
            cy="70"
            r={radius}
            stroke={strokeColor}
            strokeWidth="10"
            fill="transparent"
            strokeDasharray={circumference}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "circOut" }}
            strokeLinecap="round"
            className="opacity-20 blur-[6px]"
          />
          {/* Progress Layer 2 (Primary) */}
          <motion.circle
            cx="70"
            cy="70"
            r={radius}
            stroke={strokeColor}
            strokeWidth="8"
            fill="transparent"
            strokeDasharray={circumference}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "circOut" }}
            strokeLinecap="round"
            className={`drop-shadow-[0_0_12px_${strokeColor}]`}
          />
        </svg>

        {/* Center Content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <motion.span 
            animate={isHighRisk ? { scale: [1, 1.1, 1] } : {}}
            transition={{ duration: 0.5, repeat: Infinity }}
            className={`text-5xl font-black tracking-tighter ${isHighRisk ? 'text-red-500' : isMedRisk ? 'text-orange-400' : 'text-lime-400'}`}
          >
            {Math.round(riskScore)}<span className="text-xl opacity-30">%</span>
          </motion.span>
          <div className="flex flex-col items-center mt-1">
            <span className="text-[8px] text-gray-500 uppercase font-black tracking-widest">
              Threat Level
            </span>
            <div className={`mt-1 h-1 w-12 rounded-full ${isHighRisk ? 'bg-red-500 shadow-[0_0_10px_#ef4444]' : isMedRisk ? 'bg-orange-500' : 'bg-lime-500'}`} />
          </div>
        </div>
      </div>

      {/* Micro-Interaction Label */}
      <div className="absolute bottom-4 flex gap-2">
        {['S', 'M', 'H'].map((lvl, idx) => (
          <div key={idx} className={`w-6 h-1 rounded-full ${
            (idx === 0 && !isMedRisk && !isHighRisk) || (idx === 1 && isMedRisk) || (idx === 2 && isHighRisk)
            ? 'bg-white shadow-[0_0_10px_rgba(255,255,255,0.5)]' 
            : 'bg-white/10'
          }`} />
        ))}
      </div>
    </div>
  );
}
