import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, MapPin, DollarSign, Clock, ShieldAlert } from "lucide-react";

export default function RiskAlertFeed({ transactions }) {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    if (transactions.length > 0) {
      const latest = transactions[0];
      const timeStr = latest.timestamp || new Date().toLocaleTimeString();
      
      let newAlert = null;
      if (latest.risk === "High") {
        newAlert = { 
          id: latest.id,
          time: timeStr, 
          text: latest.reasoning || "Critical anomaly detected", 
          icon: <ShieldAlert size={14}/>, 
          color: "text-red-400",
          bg: "bg-red-500/10"
        };
      } else if (latest.score > 40) {
        newAlert = { 
          id: latest.id,
          time: timeStr, 
          text: latest.reasoning || "Moderate deviation flagged", 
          icon: <Activity size={14}/>, 
          color: "text-orange-400",
          bg: "bg-orange-500/10"
        };
      } else {
        newAlert = { 
          id: latest.id,
          time: timeStr, 
          text: "Secure transaction validated", 
          icon: <DollarSign size={14}/>, 
          color: "text-lime-400",
          bg: "bg-lime-500/5"
        };
      }

      setAlerts(prev => [newAlert, ...prev].slice(0, 5));
    }
  }, [transactions]);

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl h-full flex flex-col glass-card shadow-2xl overflow-hidden relative">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h2 className="text-white font-bold text-lg leading-tight">Live Intelligence</h2>
          <p className="text-[8px] text-gray-500 uppercase font-black tracking-widest mt-1">Real-time Stream</p>
        </div>
        <div className="flex gap-1 items-center bg-black/40 px-2 py-1 rounded-full border border-white/5">
          <div className="w-1.5 h-1.5 rounded-full bg-lime-500 animate-pulse shadow-[0_0_5px_#a3e635]"></div>
          <span className="text-[8px] text-lime-500 font-bold uppercase">Active</span>
        </div>
      </div>

      <div className="flex-1 space-y-3 overflow-hidden">
        <AnimatePresence mode="popLayout">
          {alerts.map((alert, i) => (
            <motion.div 
              key={alert.id || i}
              initial={{ opacity: 0, x: -20, filter: "blur(10px)" }}
              animate={{ opacity: 1 - (i * 0.15), x: 0, filter: "blur(0px)" }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
              className={`flex gap-3 items-start p-3 rounded-xl border border-white/5 ${alert.bg} backdrop-blur-sm`}
            >
              <div className={`mt-0.5 ${alert.color}`}>
                {alert.icon}
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-center mb-1">
                  <p className="text-[9px] text-gray-500 font-mono font-bold tracking-tighter">[{alert.time}]</p>
                  <div className="w-1 h-1 rounded-full bg-white/20" />
                </div>
                <p className="text-xs text-gray-100 font-medium leading-relaxed">{alert.text}</p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {alerts.length === 0 && (
          <p className="text-gray-500 text-sm text-center mt-10 animate-pulse">Initializing neural stream...</p>
        )}
      </div>
    </div>
  );
}
