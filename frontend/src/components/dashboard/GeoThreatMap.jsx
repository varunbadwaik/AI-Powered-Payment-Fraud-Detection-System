import { motion } from "framer-motion";
import { Globe, MapPin } from "lucide-react";

// Simplified but recognizable world map SVG path
const WORLD_PATH = "M 12,36 Q 15,33 18,35 Q 20,38 22,36 L 25,37 Q 28,34 30,36 L 28,40 Q 25,43 22,42 L 18,40 Z M 32,28 Q 35,25 38,26 L 42,24 Q 45,22 48,24 L 52,22 Q 55,20 58,22 L 60,26 Q 58,30 55,32 L 52,34 Q 50,36 48,35 L 45,33 Q 42,35 40,33 L 38,30 Q 35,31 32,28 Z M 62,28 Q 65,26 68,28 L 72,26 Q 75,24 78,26 L 82,24 Q 85,22 88,24 L 90,28 Q 88,32 85,34 L 82,36 Q 80,38 78,36 L 75,34 Q 72,36 70,34 L 68,32 Q 65,30 62,28 Z M 50,40 Q 52,38 55,40 L 58,42 Q 56,46 53,48 L 50,46 Q 48,44 50,40 Z M 70,38 Q 73,36 76,38 L 80,40 Q 82,44 80,48 L 76,50 Q 73,48 70,46 L 68,42 Q 69,40 70,38 Z M 15,50 Q 18,48 22,50 L 28,52 Q 32,56 28,60 L 22,62 Q 18,60 15,56 Z M 78,52 Q 82,50 85,52 L 88,56 Q 86,60 82,62 L 78,60 Q 76,56 78,52 Z";

// Simulated city coordinates on our 100x70 viewBox
const CITY_NODES = [
  { name: "NYC", x: 28, y: 30, region: "NA" },
  { name: "LON", x: 48, y: 24, region: "EU" },
  { name: "TKY", x: 85, y: 30, region: "APAC" },
  { name: "SYD", x: 88, y: 56, region: "APAC" },
  { name: "DXB", x: 62, y: 34, region: "ME" },
  { name: "SAO", x: 32, y: 52, region: "SA" },
  { name: "SIN", x: 78, y: 42, region: "APAC" },
  { name: "LAX", x: 15, y: 32, region: "NA" },
];

export default function GeoThreatMap({ transactions }) {
  // Map recent threats to city nodes
  const threats = transactions
    .filter(tx => tx.risk !== "Low")
    .slice(0, 5)
    .map((tx, i) => {
      const city = CITY_NODES[i % CITY_NODES.length];
      return {
        ...city,
        id: tx.id,
        risk: tx.risk,
        severity: tx.severity || "medium",
        score: tx.score,
      };
    });

  // Draw connection lines between threat cities
  const connections = threats.length >= 2 ? threats.slice(0, -1).map((t, i) => ({
    x1: t.x, y1: t.y,
    x2: threats[i + 1].x, y2: threats[i + 1].y,
  })) : [];

  return (
    <div className="bg-white/5 backdrop-blur-xl border border-white/10 p-6 rounded-2xl h-full flex flex-col glass-card shadow-2xl relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-32 h-32 bg-lime-500/5 blur-[60px] pointer-events-none"></div>

      <div className="flex justify-between items-start mb-3 relative z-10">
        <div>
          <h2 className="text-white font-bold text-lg flex items-center gap-2">
            <Globe size={18} className="text-lime-400 group-hover:rotate-180 transition-transform duration-1000" />
            Geo-Intelligence
          </h2>
          <p className="text-gray-500 text-[10px] font-black uppercase tracking-widest mt-1">Global Threat Propagation</p>
        </div>
        <div className="flex flex-col items-end">
          <span className="text-[10px] text-lime-400 font-bold flex items-center gap-1">
            <div className="w-1.5 h-1.5 rounded-full bg-lime-500 animate-pulse"></div> LIVE
          </span>
          <span className="text-[8px] text-gray-600 font-mono">NODES: {CITY_NODES.length}</span>
        </div>
      </div>

      {/* Map Container */}
      <div className="flex-1 relative mt-1 bg-black/40 rounded-xl border border-white/5 overflow-hidden">
        <svg viewBox="0 0 100 70" className="w-full h-full" preserveAspectRatio="xMidYMid meet">
          {/* Grid lines */}
          {[14, 28, 42, 56].map(y => (
            <line key={`h${y}`} x1="0" y1={y} x2="100" y2={y} stroke="rgba(255,255,255,0.03)" strokeWidth="0.2" />
          ))}
          {[20, 40, 60, 80].map(x => (
            <line key={`v${x}`} x1={x} y1="0" x2={x} y2="70" stroke="rgba(255,255,255,0.03)" strokeWidth="0.2" />
          ))}

          {/* World map outline */}
          <path d={WORLD_PATH} fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.1)" strokeWidth="0.3" />

          {/* Connection lines between threats (movement tracking) */}
          {connections.map((c, i) => (
            <motion.line
              key={`conn-${i}`}
              x1={c.x1} y1={c.y1} x2={c.x2} y2={c.y2}
              stroke="rgba(239,68,68,0.3)"
              strokeWidth="0.3"
              strokeDasharray="1 1"
              initial={{ pathLength: 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: 1.5, delay: i * 0.3 }}
            />
          ))}

          {/* Safe city nodes */}
          {CITY_NODES.map((city, i) => (
            <g key={`city-${i}`}>
              <circle cx={city.x} cy={city.y} r="0.8" fill="rgba(163,230,53,0.3)" />
              <text x={city.x} y={city.y - 2} fill="rgba(255,255,255,0.15)" fontSize="2" textAnchor="middle" fontFamily="monospace">{city.name}</text>
            </g>
          ))}

          {/* Threat pulse rings */}
          {threats.map((t, i) => (
            <g key={`threat-${t.id}`}>
              {/* Outer pulse */}
              <motion.circle
                cx={t.x} cy={t.y} r="1"
                fill="none"
                stroke={t.risk === "High" ? "#ef4444" : "#f97316"}
                strokeWidth="0.3"
                initial={{ r: 1, opacity: 0.8 }}
                animate={{ r: 6, opacity: 0 }}
                transition={{ duration: 2, repeat: Infinity, delay: i * 0.4 }}
              />
              {/* Core dot */}
              <circle
                cx={t.x} cy={t.y} r="1.2"
                fill={t.risk === "High" ? "#ef4444" : "#f97316"}
                opacity="0.9"
              />
              {/* Score label */}
              <text
                x={t.x + 2.5} y={t.y + 0.5}
                fill="white" fontSize="2.2" fontFamily="monospace" fontWeight="bold"
              >
                {Math.round(t.score)}%
              </text>
            </g>
          ))}
        </svg>

        {/* Legend */}
        <div className="absolute bottom-2 left-2 flex gap-3">
          <div className="flex items-center gap-1">
            <div className="w-1.5 h-1.5 rounded-full bg-red-500"></div>
            <span className="text-[7px] text-gray-400 font-bold uppercase">Critical</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-1.5 h-1.5 rounded-full bg-orange-500"></div>
            <span className="text-[7px] text-gray-400 font-bold uppercase">Escalated</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-1.5 h-1.5 rounded-full bg-lime-500/50"></div>
            <span className="text-[7px] text-gray-400 font-bold uppercase">Node</span>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="mt-3 grid grid-cols-3 gap-2">
        <div className="bg-white/5 p-2 rounded-lg border border-white/5">
          <p className="text-[7px] text-gray-500 font-black uppercase">Active Threats</p>
          <p className="text-xs font-bold text-red-400">{threats.length}</p>
        </div>
        <div className="bg-white/5 p-2 rounded-lg border border-white/5">
          <p className="text-[7px] text-gray-500 font-black uppercase">Regions</p>
          <p className="text-xs font-bold text-white">{new Set(threats.map(t => t.region)).size || 0}</p>
        </div>
        <div className="bg-white/5 p-2 rounded-lg border border-white/5">
          <p className="text-[7px] text-gray-500 font-black uppercase">Latency</p>
          <p className="text-xs font-bold text-lime-400">14ms</p>
        </div>
      </div>
    </div>
  );
}
