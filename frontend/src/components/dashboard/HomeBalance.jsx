export default function HomeBalance({ transactions }) {
  // Take last 4 transactions for the mini list
  const recent = [...transactions].reverse().slice(0, 4);

  return (
    <div className="bg-[#0c0c0c] border border-white/5 p-6 rounded-2xl h-full flex flex-col">
      <div className="flex justify-between items-start mb-6">
        <h2 className="text-white font-bold text-xl">Home</h2>
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-pink-500 to-orange-400 overflow-hidden border border-white/20">
          {/* Avatar placeholder */}
          <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="avatar" />
        </div>
      </div>

      <div className="mb-8">
        <p className="text-gray-500 text-sm mb-1">Main Account</p>
        <h1 className="text-4xl font-bold text-white">5,654.32</h1>
      </div>

      <div className="flex-1 space-y-3">
        {recent.map((tx, i) => (
          <div key={i} className="flex justify-between items-center bg-white/5 p-3 rounded-xl">
            <div className="flex items-center gap-3">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs ${
                tx.risk === 'High' ? 'bg-red-500/20 text-red-500' :
                tx.risk === 'Medium' ? 'bg-yellow-500/20 text-yellow-500' :
                'bg-blue-500/20 text-blue-500'
              }`}>
                {tx.risk[0]}
              </div>
              <div>
                <p className="text-white text-sm font-medium">Txn {tx.id.substring(0,4)}</p>
              </div>
            </div>
            <span className="text-white font-semibold">-${tx.score.toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
