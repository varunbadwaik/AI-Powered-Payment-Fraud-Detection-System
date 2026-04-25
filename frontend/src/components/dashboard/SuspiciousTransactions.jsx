import { motion } from "framer-motion";
import { ShieldAlert, CheckCircle2, XCircle, Clock, AlertTriangle } from "lucide-react";
import axios from "axios";

const SEVERITY_CONFIG = {
  critical: {
    dot: "bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)]",
    badge: "bg-red-500/15 text-red-500 border-red-500/30",
    label: "🔴 CRITICAL",
    icon: <AlertTriangle size={12} />,
  },
  medium: {
    dot: "bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.8)]",
    badge: "bg-orange-500/15 text-orange-400 border-orange-500/30",
    label: "🟠 MEDIUM",
    icon: <Clock size={12} />,
  },
  low: {
    dot: "bg-lime-500/50",
    badge: "bg-lime-500/10 text-lime-400 border-lime-500/20",
    label: "🟢 LOW",
    icon: <CheckCircle2 size={12} />,
  },
};

export default function SuspiciousTransactions({ transactions, onFeedback }) {
  // Show high/medium risk transactions with severity
  const alerts = transactions.filter(tx => tx.risk !== "Low").slice(0, 5);

  const handleFeedback = async (txId, action) => {
    try {
      await axios.post(`${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/v1/feedback`, {
        transaction_id: txId,
        action: action,
      });
      if (onFeedback) onFeedback(txId, action);
    } catch (err) {
      console.error("Feedback failed:", err);
    }
  };

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl h-full overflow-hidden glass-card relative">
      <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-red-500/5 via-transparent to-transparent pointer-events-none"></div>

      <div className="flex items-center justify-between mb-4 relative z-10">
        <h2 className="text-white font-bold text-lg flex items-center gap-2">
          <ShieldAlert className="text-red-500" size={18} /> Action Required
        </h2>
        <span className="bg-red-500/20 text-red-500 text-[10px] px-2 py-0.5 rounded-md font-bold border border-red-500/20">
          {alerts.length} Pending
        </span>
      </div>

      <div className="space-y-2 relative z-10 overflow-y-auto" style={{ maxHeight: "calc(100% - 50px)" }}>
        {alerts.length === 0 && (
          <div className="text-center py-6 text-gray-500 text-sm">
            No suspicious activity detected.
          </div>
        )}

        {alerts.map((tx, i) => {
          const sev = SEVERITY_CONFIG[tx.severity || "medium"];
          return (
            <motion.div
              key={tx.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05, duration: 0.3 }}
              className="flex justify-between items-center py-2.5 px-3 bg-black/40 border border-white/5 rounded-xl hover:border-white/10 transition-colors"
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <div className={`w-2 h-2 rounded-full flex-shrink-0 ${sev.dot}`} />
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-white font-semibold text-xs">TXN-{tx.id.substring(0, 8)}</p>
                    <span className={`text-[8px] font-black px-1.5 py-0.5 rounded border ${sev.badge}`}>
                      {sev.label}
                    </span>
                  </div>
                  <p className="text-gray-500 text-[10px] truncate mt-0.5">
                    {tx.reasons?.[0] || `Score: ${tx.score.toFixed(1)}%`}
                  </p>
                </div>
              </div>

              <div className="flex gap-1.5 flex-shrink-0 ml-2">
                <button
                  onClick={() => handleFeedback(tx.id, "block")}
                  className="flex items-center gap-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 px-2.5 py-1 rounded-lg text-[10px] font-semibold transition-colors"
                >
                  <XCircle size={12} /> Block
                </button>
                <button
                  onClick={() => handleFeedback(tx.id, "allow")}
                  className="flex items-center gap-1 bg-lime-500/10 hover:bg-lime-500/20 text-lime-400 border border-lime-500/20 px-2.5 py-1 rounded-lg text-[10px] font-semibold transition-colors"
                >
                  <CheckCircle2 size={12} /> Allow
                </button>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
