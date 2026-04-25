import { ArrowUpDown } from "lucide-react";

export default function ExchangeWidget() {
  return (
    <div className="bg-[#0c0c0c] border border-white/5 p-6 rounded-2xl h-full flex flex-col">
      <h2 className="text-white font-bold text-xl mb-6 text-center">Exchange</h2>
      
      <div className="flex-1 flex flex-col gap-4 relative">
        {/* Send */}
        <div className="border border-white/5 rounded-xl p-4">
          <div className="flex justify-between text-xs text-gray-500 mb-2">
            <span>Your Send</span>
            <span>Available $3,544.45</span>
          </div>
          <div className="flex justify-between items-center">
            <input 
              type="text" 
              defaultValue="654.65" 
              className="bg-transparent text-white text-2xl font-semibold w-1/2 outline-none"
            />
            <div className="flex items-center gap-2 bg-white/5 px-3 py-1.5 rounded-lg text-white">
              <span className="text-xl">🇺🇸</span>
              <span className="font-semibold">USD</span>
            </div>
          </div>
        </div>

        {/* Swap Icon */}
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 -mt-16">
          <div className="bg-lime-500 p-2 rounded-full text-black shadow-[0_0_15px_rgba(163,230,53,0.5)]">
            <ArrowUpDown size={16} />
          </div>
        </div>

        {/* Receive */}
        <div className="border border-white/5 rounded-xl p-4">
          <div className="flex justify-between text-xs text-gray-500 mb-2">
            <span>Your received</span>
            <span>Available 5.32451 ETH</span>
          </div>
          <div className="flex justify-between items-center">
            <input 
              type="text" 
              defaultValue="0.52654" 
              className="bg-transparent text-white text-2xl font-semibold w-1/2 outline-none"
            />
            <div className="flex items-center gap-2 bg-white/5 px-3 py-1.5 rounded-lg text-white">
              <span className="text-blue-400">♦</span>
              <span className="font-semibold">ETH</span>
            </div>
          </div>
        </div>
        
        {/* Rates */}
        <div className="mt-4 space-y-2 text-xs text-gray-500">
          <div className="flex justify-between">
            <span>Rate</span>
            <span className="text-gray-300">1 ETH = 32,454.5241 USD</span>
          </div>
          <div className="flex justify-between">
            <span>Service free</span>
            <span className="text-gray-300">11.22 USD</span>
          </div>
          <div className="flex justify-between">
            <span>Gas free</span>
            <span className="text-gray-300">1.23 USD</span>
          </div>
        </div>
      </div>

      <button className="w-full bg-gradient-to-r from-lime-500 to-lime-600 hover:from-lime-400 hover:to-lime-500 text-black font-bold py-4 rounded-xl mt-6 transition-all shadow-[0_0_20px_rgba(163,230,53,0.3)]">
        Exchange
      </button>
    </div>
  );
}
