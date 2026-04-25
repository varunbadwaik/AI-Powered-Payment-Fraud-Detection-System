import { motion } from "framer-motion";
import { BarChart3, Target, Crosshair, AlertTriangle, TrendingDown } from "lucide-react";

const MetricRing = ({ value, label, color, icon: Icon, delay }) => {
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="flex flex-col items-center gap-2"
    >
      <div className="relative w-[72px] h-[72px]">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 64 64">
          <circle cx="32" cy="32" r={radius} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="4" />
          <motion.circle
            cx="32" cy="32" r={radius} fill="none"
            stroke={color}
            strokeWidth="4"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.5, delay: delay + 0.3, ease: "circOut" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-white font-black text-sm">{value}%</span>
        </div>
      </div>
      <div className="flex items-center gap-1">
        <Icon size={10} className="opacity-50" style={{ color }} />
        <span className="text-[9px] text-gray-400 font-bold uppercase tracking-wider">{label}</span>
      </div>
    </motion.div>
  );
};

export default function ModelMetricsPanel({ metrics }) {
  const data = metrics || {
    accuracy: 94.2,
    precision: 91.5,
    recall: 88.7,
    fpr: 3.2,
    f1: 90.1,
  };

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl h-full flex flex-col glass-card shadow-2xl relative overflow-hidden group">
      <div className="absolute top-0 left-0 w-40 h-40 bg-violet-500/5 blur-[80px] pointer-events-none"></div>

      <div className="flex justify-between items-start mb-5 relative z-10">
        <div>
          <h2 className="text-white font-bold text-lg flex items-center gap-2">
            <BarChart3 size={18} className="text-violet-400" />
            Model Performance
          </h2>
          <p className="text-gray-500 text-[10px] font-black uppercase tracking-widest mt-1">Ensemble Metrics (IF + LR + XGB)</p>
        </div>
        <div className="bg-violet-500/10 border border-violet-500/20 px-2 py-0.5 rounded-full">
          <span className="text-[9px] text-violet-400 font-bold uppercase">Live</span>
        </div>
      </div>

      <div className="flex-1 flex items-center justify-around relative z-10">
        <MetricRing value={data.accuracy} label="Accuracy" color="#a78bfa" icon={Target} delay={0} />
        <MetricRing value={data.precision} label="Precision" color="#34d399" icon={Crosshair} delay={0.1} />
        <MetricRing value={data.recall} label="Recall" color="#fbbf24" icon={TrendingDown} delay={0.2} />
        <MetricRing value={data.fpr} label="FPR" color="#f87171" icon={AlertTriangle} delay={0.3} />
      </div>

      <div className="mt-4 pt-3 border-t border-white/5 flex justify-between items-center relative z-10">
        <div className="flex gap-4">
          <div className="flex flex-col">
            <span className="text-[8px] text-gray-500 uppercase font-black">F1 Score</span>
            <span className="text-xs font-bold text-violet-400">{data.f1}%</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[8px] text-gray-500 uppercase font-black">AUC-ROC</span>
            <span className="text-xs font-bold text-white">0.967</span>
          </div>
        </div>
        <span className="text-[8px] text-gray-600 font-mono">EVAL_EPOCH: 847</span>
      </div>
    </div>
  );
}
