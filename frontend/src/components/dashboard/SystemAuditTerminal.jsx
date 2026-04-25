import { useEffect, useState, useRef } from "react";
import { Terminal, Cpu } from "lucide-react";

export default function SystemAuditTerminal() {
  const [logs, setLogs] = useState([
    "[SYSTEM] Kernel initialized. IF-XGB Ensemble online.",
    "[AUTH] Secure connection established with Node_0x88",
    "[MODEL] Pre-loading weights for IsolationForest...",
  ]);
  const scrollRef = useRef(null);

  const logPool = [
    "Analyzing vector distance in hyper-dimensional space...",
    "XGBoost weight shift detected: feature_04 significance +12%",
    "Isolation Forest identifying anomalous branch at depth 14",
    "RuleEngine R-004 triggered: Night_Intl combo detected",
    "Cross-referencing historical user baseline (μ=$1200)",
    "LLM Explainer generating human-readable reasoning...",
    "Database persistency check: Success [TXN_COMMIT]",
    "Security check: PCI-DSS compliance validated.",
    "Anomaly detected in velocity pattern (5 req/sec)",
    "Neural weights re-calibrated. Confidence: 99.8%",
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      const newLog = `[${new Date().toLocaleTimeString()}] ${logPool[Math.floor(Math.random() * logPool.length)]}`;
      setLogs(prev => [...prev, newLog].slice(-50));
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl h-full flex flex-col glass-card shadow-2xl relative overflow-hidden group">
      <div className="flex justify-between items-start mb-4 relative z-10">
        <div>
          <h2 className="text-white font-bold text-xl flex items-center gap-2">
            <Terminal size={20} className="text-lime-400" />
            System Audit
          </h2>
          <p className="text-gray-500 text-[10px] font-black uppercase tracking-widest mt-1">Internal AI Reasonings</p>
        </div>
        <Cpu size={16} className="text-gray-600 animate-pulse" />
      </div>

      <div 
        ref={scrollRef}
        className="flex-1 mt-2 bg-black/60 rounded-xl border border-white/5 p-4 font-mono text-[10px] overflow-y-auto scrollbar-hide"
      >
        <div className="space-y-1">
          {logs.map((log, i) => (
            <div key={i} className="flex gap-2">
              <span className="text-lime-500/50">λ</span>
              <span className={log.includes("detected") || log.includes("triggered") ? "text-orange-400" : "text-gray-300"}>
                {log}
              </span>
            </div>
          ))}
          <div className="w-2 h-4 bg-lime-500 animate-pulse inline-block"></div>
        </div>
      </div>
    </div>
  );
}
