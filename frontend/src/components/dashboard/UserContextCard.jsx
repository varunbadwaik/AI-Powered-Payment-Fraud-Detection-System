import { motion } from "framer-motion";
import { User, Target, CreditCard, ShieldCheck } from "lucide-react";

export default function UserContextCard({ latestTx }) {
  const amount = latestTx?.amount || 0;
  const baseline = latestTx?.user_baseline || 1200;
  const ratio = amount / baseline;
  const isAnomalous = ratio > 3;

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl h-full flex flex-col justify-between glass-card shadow-2xl relative overflow-hidden">
      <div className="absolute top-0 right-0 p-4 opacity-5">
        <User size={120} />
      </div>

      <div className="relative z-10">
        <div className="flex items-center gap-3 mb-6">
          <div className="relative">
            <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-lime-500 to-lime-200 p-[1px]">
              <div className="w-full h-full rounded-full bg-black flex items-center justify-center overflow-hidden">
                <img src="https://i.pravatar.cc/150?u=fraud-demo" alt="User" className="w-full h-full object-cover opacity-80" />
              </div>
            </div>
            <div className="absolute -bottom-1 -right-1 bg-lime-500 rounded-full p-1 border-2 border-black">
              <ShieldCheck size={10} className="text-black" />
            </div>
          </div>
          <div>
            <h2 className="text-white font-bold text-lg leading-tight">Alex Rivera</h2>
            <p className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">Premium Member • ID: 88219</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-black/30 border border-white/5 p-4 rounded-xl">
            <div className="flex justify-between items-center mb-2">
              <span className="text-[10px] text-gray-500 font-bold uppercase flex items-center gap-1">
                <Target size={12} className="text-lime-400" /> Typical Baseline
              </span>
              <span className="text-white font-mono text-xs">${baseline.toFixed(0)}</span>
            </div>
            <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
              <div className="bg-lime-500/40 h-full w-[40%]" />
            </div>
          </div>

          <div className={`bg-black/30 border p-4 rounded-xl transition-colors duration-500 ${isAnomalous ? 'border-red-500/30' : 'border-white/5'}`}>
            <div className="flex justify-between items-center mb-2">
              <span className="text-[10px] text-gray-500 font-bold uppercase flex items-center gap-1">
                <CreditCard size={12} className={isAnomalous ? "text-red-500" : "text-lime-400"} /> Current Transaction
              </span>
              <span className={`font-mono text-xs ${isAnomalous ? 'text-red-500 font-black' : 'text-white'}`}>
                ${amount.toFixed(0)}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-white/5 h-1 rounded-full overflow-hidden">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: isAnomalous ? '100%' : '60%' }}
                  className={`h-full ${isAnomalous ? 'bg-red-500 shadow-[0_0_8px_#ef4444]' : 'bg-white/40'}`} 
                />
              </div>
              <span className={`text-[10px] font-bold ${isAnomalous ? 'text-red-500' : 'text-gray-400'}`}>
                {ratio.toFixed(1)}x
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-white/5 flex justify-between items-center relative z-10">
        <div className="flex flex-col">
          <span className="text-[8px] text-gray-500 uppercase font-black">Trust Score</span>
          <span className="text-xs font-bold text-lime-400">98/100</span>
        </div>
        <button className="text-[10px] font-bold text-gray-400 hover:text-white transition-colors uppercase tracking-widest">
          View Profile →
        </button>
      </div>
    </div>
  );
}
