export default function Navbar({ wsConnected }) {
  return (
    <nav className="border-b border-white/5 bg-black/50 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-[1560px] mx-auto px-4 md:px-6 py-3 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-lime-400 to-lime-600">
            FraudShield
          </span>
          <span className="text-gray-500 text-sm hidden md:inline">| AI Command Center</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full animate-pulse ${wsConnected ? 'bg-lime-500 shadow-[0_0_8px_rgba(163,230,53,0.8)]' : 'bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.5)]'}`}></div>
            <span className="text-xs text-gray-400 font-medium hidden sm:inline">
              {wsConnected ? "WebSocket Live" : "HTTP Polling"}
            </span>
          </div>
          <div className="bg-white/5 px-2 py-1 rounded-full border border-white/10 hidden md:block">
            <span className="text-[9px] text-gray-400 font-mono uppercase">v3.0 • Ensemble</span>
          </div>
          <button className="bg-white/5 hover:bg-white/10 border border-white/10 px-4 py-1.5 rounded-xl text-xs font-semibold transition-all text-white">
            Deploy Rules
          </button>
        </div>
      </div>
    </nav>
  );
}

