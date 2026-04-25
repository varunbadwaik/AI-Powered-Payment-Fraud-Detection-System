import { motion, useMotionValue, useTransform } from "framer-motion";
import { Cpu, ShieldCheck, Zap, Activity } from "lucide-react";

export default function CardStack3D() {
  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const rotateX = useTransform(y, [-100, 100], [15, -15]);
  const rotateY = useTransform(x, [-100, 100], [-15, 15]);

  function handleMouse(event) {
    const rect = event.currentTarget.getBoundingClientRect();
    x.set(event.clientX - rect.left - rect.width / 2);
    y.set(event.clientY - rect.top - rect.height / 2);
  }

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl h-full flex flex-col items-center justify-center relative overflow-hidden glass-card shadow-lg"
         style={{ perspective: 1000 }}
         onMouseMove={handleMouse}
         onMouseLeave={() => { x.set(0); y.set(0); }}>
      
      <div className="absolute top-4 left-6">
        <h2 className="text-white font-semibold text-lg flex items-center gap-2">
          <Activity size={18} className="text-lime-400 animate-pulse"/> 
          Intelligence Hub
        </h2>
        <p className="text-xs text-gray-500">Neural Network Active</p>
      </div>

      <motion.div 
        style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
        className="relative w-72 h-44 mt-8"
      >
        {/* Layer 3 - Deep Shadow/Glow */}
        <div className="absolute inset-0 bg-lime-500/5 rounded-2xl blur-2xl transform translate-z-[-20px]" />

        {/* Layer 2 - Secondary Node (Glass) */}
        <div className="absolute inset-0 bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl shadow-xl transform translate-x-4 -translate-y-4 translate-z-[-10px] opacity-40">
           <div className="p-4">
             <Zap size={20} className="text-lime-500/30" />
           </div>
        </div>
        
        {/* Layer 1 - Primary Node (Cyber Glass) */}
        <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent backdrop-blur-2xl rounded-2xl shadow-2xl border border-white/20 flex flex-col justify-between p-6 transform translate-z-20 overflow-hidden">
          
          {/* Scanning Animation */}
          <motion.div 
            animate={{ y: [0, 180, 0] }}
            transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
            className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-lime-500/40 to-transparent shadow-[0_0_15px_rgba(163,230,53,0.5)] z-0"
          />

          <div className="flex justify-between items-start relative z-10">
            <div className="bg-lime-500/20 p-2 rounded-lg border border-lime-500/30 shadow-[0_0_10px_rgba(163,230,53,0.2)]">
              <Cpu className="text-lime-400" size={24} />
            </div>
            <ShieldCheck className="text-lime-400/50" size={24} />
          </div>

          <div className="relative z-10">
            <p className="text-[10px] text-gray-500 uppercase tracking-widest mb-1 font-bold">Node Confidence</p>
            <div className="flex items-baseline gap-2">
              <h3 className="text-3xl font-black text-white tracking-tighter">99.8<span className="text-lg text-lime-400">%</span></h3>
              <div className="bg-lime-500/20 px-2 py-0.5 rounded border border-lime-500/30">
                <p className="text-[8px] text-lime-400 font-bold uppercase">Optimal</p>
              </div>
            </div>
          </div>

          <div className="flex justify-between items-end relative z-10">
            <div>
              <p className="text-[8px] text-gray-500 uppercase font-bold">Instruction Set</p>
              <p className="text-xs text-gray-300 font-mono tracking-widest uppercase">IF-XGB-ENSEMBLE-V2</p>
            </div>
            <div className="flex gap-1">
              {[1,2,3].map(i => (
                <motion.div 
                  key={i}
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                  className="w-1 h-3 bg-lime-500/50 rounded-full"
                />
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
