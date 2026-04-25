import { motion } from "framer-motion";
import { BrainCircuit, AlertTriangle, ShieldCheck, Info, Cpu, Sparkles, BarChart2 } from "lucide-react";

const ModelBar = ({ name, score, color, delay }) => (
  <motion.div
    initial={{ opacity: 0, x: -10 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay, duration: 0.4 }}
    className="flex items-center gap-3"
  >
    <span className="text-[9px] text-gray-400 font-mono w-[60px] truncate uppercase">{name}</span>
    <div className="flex-1 bg-black/50 rounded-full h-2 overflow-hidden">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${Math.min(score * 100, 100)}%` }}
        transition={{ duration: 1.2, delay: delay + 0.2, ease: "circOut" }}
        className="h-full rounded-full"
        style={{ backgroundColor: color }}
      />
    </div>
    <span className="text-[10px] text-white font-mono font-bold w-[40px] text-right">
      {(score * 100).toFixed(1)}%
    </span>
  </motion.div>
);

export default function AIDecisionPanel({ latestTx }) {
  const isHighRisk = latestTx?.risk === "High";
  const isMedRisk = latestTx?.risk === "Medium";
  const confidence = latestTx?.confidence || 0.92;
  const agreement = latestTx?.model_agreement ?? true;
  const severity = latestTx?.severity || "low";
  const reasons = latestTx?.reasons || [];
  const modelScores = latestTx?.model_scores || {};
  const isLLM = latestTx?.is_llm_generated || false;

  const sevColor = severity === "critical" ? "text-red-500" : severity === "medium" ? "text-orange-400" : "text-lime-400";
  const sevBg = severity === "critical" ? "bg-red-500/15 border-red-500/30" : severity === "medium" ? "bg-orange-500/15 border-orange-500/30" : "bg-lime-500/10 border-lime-500/20";
  const sevDot = severity === "critical" ? "bg-red-500" : severity === "medium" ? "bg-orange-500" : "bg-lime-500";

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl h-full flex flex-col glass-card group shadow-2xl relative overflow-hidden">
      {/* Glow Effect */}
      <div className={`absolute -top-24 -right-24 w-48 h-48 rounded-full blur-[80px] transition-colors duration-500 ${isHighRisk ? 'bg-red-500/20' : 'bg-lime-500/10'}`}></div>

      {/* Header */}
      <div className="flex justify-between items-start mb-4 relative z-10">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg transition-all duration-500 ${isHighRisk ? 'bg-red-500/20 text-red-500 shadow-[0_0_15px_rgba(239,68,68,0.3)]' : 'bg-lime-500/20 text-lime-400'}`}>
            <BrainCircuit size={22} />
          </div>
          <div>
            <h2 className="text-white font-bold text-lg">AI Decision Engine</h2>
            <div className="flex items-center gap-3 mt-0.5">
              <div className="flex items-center gap-1">
                <span className="text-[9px] text-gray-500 uppercase font-bold">Confidence:</span>
                <span className={`text-[10px] font-mono font-bold ${confidence > 0.9 ? 'text-lime-400' : 'text-yellow-400'}`}>
                  {(confidence * 100).toFixed(1)}%
                </span>
              </div>
              <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full border ${sevBg}`}>
                <div className={`w-1.5 h-1.5 rounded-full ${sevDot} ${severity === 'critical' ? 'animate-pulse' : ''}`} />
                <span className={`text-[8px] font-black uppercase ${sevColor}`}>{severity}</span>
              </div>
            </div>
          </div>
        </div>
        <div className="flex flex-col items-end gap-1">
          <div className="flex gap-1">
            <div className={`w-1.5 h-1.5 rounded-full ${agreement ? 'bg-lime-500 shadow-[0_0_5px_rgba(163,230,53,0.8)]' : 'bg-yellow-500'}`} />
            <div className={`w-1.5 h-1.5 rounded-full ${agreement ? 'bg-lime-500 shadow-[0_0_5px_rgba(163,230,53,0.8)]' : 'bg-red-500 animate-pulse'}`} />
            <div className={`w-1.5 h-1.5 rounded-full ${agreement ? 'bg-lime-500 shadow-[0_0_5px_rgba(163,230,53,0.8)]' : 'bg-orange-500'}`} />
          </div>
          <p className="text-[8px] text-gray-500 uppercase font-bold">3-Model Agreement</p>
        </div>
      </div>

      {/* Reasoning Section */}
      <div className="relative z-10 flex-1 flex flex-col gap-3 overflow-y-auto">
        {/* LLM / Contextual Explanation */}
        <div className="bg-black/40 border border-white/5 p-4 rounded-xl backdrop-blur-md">
          <h3 className="text-[10px] font-bold text-gray-500 uppercase mb-2 flex items-center gap-1">
            {isLLM ? <Sparkles size={11} className="text-violet-400" /> : <Info size={11} className="text-lime-400" />}
            {isLLM ? "AI-Generated Explanation" : "Contextual Verdict"}
          </h3>
          <p className="text-sm text-gray-200 leading-relaxed font-medium">
            {latestTx?.reasoning || "Analyzing live transaction data stream..."}
          </p>
        </div>

        {/* Specific Reasons */}
        {reasons.length > 0 && (
          <div className="space-y-1.5">
            <h3 className="text-[9px] font-bold text-gray-500 uppercase tracking-widest flex items-center gap-1">
              <AlertTriangle size={10} className={isHighRisk ? "text-red-500" : "text-gray-500"} />
              Flagged Reasons ({reasons.length})
            </h3>
            {reasons.slice(0, 4).map((reason, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1, duration: 0.3 }}
                className="flex items-start gap-2 py-1.5 px-3 bg-white/[0.02] border border-white/5 rounded-lg"
              >
                <div className={`w-1 h-1 rounded-full mt-1.5 flex-shrink-0 ${isHighRisk ? 'bg-red-500' : isMedRisk ? 'bg-orange-500' : 'bg-lime-500'}`} />
                <span className="text-[11px] text-gray-300 leading-snug">{reason}</span>
              </motion.div>
            ))}
          </div>
        )}

        {/* Multi-Model Comparison */}
        {Object.keys(modelScores).length > 0 && (
          <div className="mt-auto pt-3">
            <h3 className="text-[9px] font-bold text-gray-500 uppercase tracking-widest mb-3 flex items-center gap-1">
              <BarChart2 size={10} className="text-violet-400" /> Multi-Model Scores
            </h3>
            <div className="space-y-2">
              {modelScores.isolation_forest_score !== undefined && (
                <ModelBar name="IF" score={modelScores.isolation_forest_score} color="#f97316" delay={0} />
              )}
              {modelScores.logistic_regression_score !== undefined && (
                <ModelBar name="LR" score={modelScores.logistic_regression_score} color="#a78bfa" delay={0.1} />
              )}
              {modelScores.xgboost_score !== undefined && (
                <ModelBar name="XGB" score={modelScores.xgboost_score} color="#34d399" delay={0.2} />
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between relative z-10">
        <div className="flex flex-col">
          <span className="text-[8px] text-gray-500 uppercase font-bold">Engine Mode</span>
          <span className="text-[10px] text-lime-400 font-mono">ENSEMBLE-V3 • {isLLM ? 'LLM-ACTIVE' : 'TEMPLATE'}</span>
        </div>
        {isHighRisk ? (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-1 text-red-500 text-xs font-bold bg-red-500/10 px-4 py-2 rounded-xl border border-red-500/20 shadow-[0_0_15px_rgba(239,68,68,0.1)]"
          >
            <AlertTriangle size={13} /> FLAG
          </motion.button>
        ) : (
          <div className="flex items-center gap-1 text-lime-400 text-xs font-bold bg-lime-500/10 px-3 py-1.5 rounded-xl border border-lime-500/20">
            <ShieldCheck size={13} /> STABLE
          </div>
        )}
      </div>
    </div>
  );
}
