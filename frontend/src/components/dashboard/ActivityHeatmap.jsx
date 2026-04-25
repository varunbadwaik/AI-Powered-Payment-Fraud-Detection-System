export default function ActivityHeatmap() {
  // Generate a mock 5x7 grid of dots for the heatmap
  const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
  const rows = [1, 2, 3, 4, 5];

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl h-full flex flex-col justify-between glass-card shadow-lg">
      <div>
        <h2 className="text-white font-bold text-xl">System Activity</h2>
        <p className="text-gray-500 text-sm">Real-time model inferences</p>
      </div>

      <div className="flex flex-col gap-3 mt-6">
        {rows.map((row) => (
          <div key={row} className="flex justify-between">
            {days.map((day, i) => {
              // Randomly light up some dots
              const isLit = Math.random() > 0.6;
              return (
                <div 
                  key={`${row}-${i}`} 
                  className={`w-1.5 h-1.5 rounded-full ${isLit ? 'bg-lime-500 shadow-[0_0_8px_rgba(163,230,53,0.8)]' : 'bg-gray-800'}`}
                />
              );
            })}
          </div>
        ))}
        
        <div className="flex justify-between mt-2">
          {days.map((day, i) => (
            <span key={i} className="text-[10px] text-gray-600 font-medium">{day}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
