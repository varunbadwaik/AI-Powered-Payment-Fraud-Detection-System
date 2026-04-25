import { Receipt } from "lucide-react";

export default function TransactionTracker({ transactions }) {
  const recent = [...transactions].reverse().slice(0, 4);

  return (
    <div className="relative bg-[#0c0c0c] border border-white/5 p-6 rounded-2xl h-full overflow-hidden">
      {/* Background radial glow matching the reference image */}
      <div className="absolute top-0 left-1/4 w-3/4 h-3/4 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-lime-500/20 via-transparent to-transparent pointer-events-none"></div>
      
      <h2 className="text-white font-bold text-xl mb-6 relative z-10">Billing & invoice</h2>
      
      <div className="space-y-4 relative z-10">
        {recent.length === 0 && (
          <p className="text-gray-500">Waiting for live simulation data...</p>
        )}
        
        {recent.map((tx, i) => (
          <div key={i} className="flex justify-between items-center py-2">
            <div className="flex items-center gap-6">
              <span className="text-gray-500 text-sm w-12">12May</span>
              <div className="flex items-center gap-3">
                <Receipt className="text-lime-400" size={20} />
                <div>
                  <p className="text-gray-400 text-xs">INV-{tx.id.substring(0,6)}</p>
                  <p className="text-white font-semibold text-sm">${(tx.score * 10).toFixed(2)}</p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-8">
              <span className="text-gray-400 text-sm">TechVista</span>
              {tx.risk === "High" ? (
                <span className="px-3 py-1 rounded-full bg-red-500/20 text-red-500 text-xs font-semibold">● Blocked</span>
              ) : tx.risk === "Medium" ? (
                <span className="px-3 py-1 rounded-full bg-yellow-500/20 text-yellow-500 text-xs font-semibold">● Pending</span>
              ) : (
                <span className="px-3 py-1 rounded-full bg-lime-500/20 text-lime-500 text-xs font-semibold">● Paid</span>
              )}
              <span className="text-gray-500 hover:text-white cursor-pointer transition-colors">→</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
