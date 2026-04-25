import { useState, useEffect, useCallback, useRef } from "react";
import axios from "axios";
import Particles from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import Navbar from "../components/Navbar";
import CardStack3D from "../components/dashboard/CardStack3D";
import NeonDonut from "../components/dashboard/NeonDonut";
import AnomalyTimeline from "../components/dashboard/AnomalyTimeline";
import AIDecisionPanel from "../components/dashboard/AIDecisionPanel";
import RiskAlertFeed from "../components/dashboard/RiskAlertFeed";
import SuspiciousTransactions from "../components/dashboard/SuspiciousTransactions";
import UserContextCard from "../components/dashboard/UserContextCard";
import GeoThreatMap from "../components/dashboard/GeoThreatMap";
import SystemAuditTerminal from "../components/dashboard/SystemAuditTerminal";
import ModelMetricsPanel from "../components/dashboard/ModelMetricsPanel";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws/predictions";

const MERCHANT_CATS = ["online_retail", "electronics", "grocery", "restaurant", "travel", "gas_station", "entertainment"];

export default function Dashboard3D() {
  const [transactions, setTransactions] = useState([]);
  const [latestScore, setLatestScore] = useState(0);
  const [modelMetrics, setModelMetrics] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);

  const particlesInit = useCallback(async (engine) => {
    await loadSlim(engine);
  }, []);

  // ── Fetch model metrics on mount ────────────────────────────────
  useEffect(() => {
    axios.get(`${API_BASE}/api/v1/model-metrics`)
      .then(res => setModelMetrics(res.data))
      .catch(() => {}); // Silently fallback to defaults
  }, []);

  // ── WebSocket Connection ────────────────────────────────────────
  useEffect(() => {
    let ws;
    let reconnectTimer;

    const connect = () => {
      try {
        ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
          setWsConnected(true);
          console.log("[WS] Connected to prediction stream");
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            processIncoming(data);
          } catch (e) {
            console.error("[WS] Parse error:", e);
          }
        };

        ws.onclose = () => {
          setWsConnected(false);
          // Auto-reconnect after 3s
          reconnectTimer = setTimeout(connect, 3000);
        };

        ws.onerror = () => {
          ws.close();
        };
      } catch (e) {
        // WebSocket not available, fall back to polling
        reconnectTimer = setTimeout(connect, 5000);
      }
    };

    connect();

    return () => {
      if (ws) ws.close();
      if (reconnectTimer) clearTimeout(reconnectTimer);
    };
  }, []);

  // ── Process incoming prediction (from WS or HTTP) ───────────────
  const processIncoming = (apiData) => {
    const score = (apiData.fraud_probability || 0) * 100;
    const processedData = {
      score,
      risk: apiData.risk_level || "Low",
      id: apiData.transaction_id || `TXN-${Date.now()}`,
      amount: apiData.amount || 0,
      user_baseline: apiData.avg_amount_30d || 1200,
      confidence: 0.85 + Math.random() * 0.12,
      model_agreement: apiData.model_scores
        ? Object.values(apiData.model_scores).every(s => (s > 0.5) === (score > 50))
        : score > 80 || score < 20,
      reasoning: apiData.explanation || apiData.reasons?.[0] || "Transaction patterns appear standard.",
      reasons: apiData.reasons || [],
      severity: apiData.severity || "low",
      model_scores: apiData.model_scores || {},
      is_llm_generated: apiData.is_llm_generated || false,
      decision: apiData.decision || "REVIEW",
      timestamp: new Date().toLocaleTimeString(),
    };

    setLatestScore(score);
    setTransactions(prev => [processedData, ...prev].slice(0, 20));
  };

  // ── HTTP Polling Fallback (if WebSocket not connected) ──────────
  const fetchPrediction = async () => {
    try {
      const amount = Math.random() * 5000;
      const user_avg = 800 + Math.random() * 800;
      const hour = Math.floor(Math.random() * 24);
      const velocity = Math.floor(Math.random() * 8);
      const distance = Math.random() * 500;
      const isIntl = Math.random() > 0.8;

      const res = await axios.post(`${API_BASE}/api/v1/predict`, {
        amount,
        merchant_category: MERCHANT_CATS[Math.floor(Math.random() * MERCHANT_CATS.length)],
        transaction_hour: hour,
        day_of_week: Math.floor(Math.random() * 7),
        location_distance_km: distance,
        is_international: isIntl,
        card_present: Math.random() > 0.4,
        velocity_last_1h: velocity,
        avg_amount_30d: user_avg,
      });

      processIncoming({ ...res.data, amount, avg_amount_30d: user_avg });
    } catch (err) {
      console.error("[HTTP] Prediction fetch failed:", err.message);
    }
  };

  // ── Start polling (works alongside WS as primary data source) ───
  useEffect(() => {
    fetchPrediction(); // Initial fetch
    const interval = setInterval(fetchPrediction, 4000);
    return () => clearInterval(interval);
  }, []);

  // ── Feedback handler ────────────────────────────────────────────
  const handleFeedback = (txId, action) => {
    console.log(`[FEEDBACK] ${action.toUpperCase()} → ${txId}`);
    // The SuspiciousTransactions component handles the API call
  };

  return (
    <div className="bg-black min-h-screen overflow-x-hidden text-white font-sans selection:bg-lime-500/30 pb-12 relative">
      <Particles
        id="tsparticles"
        init={particlesInit}
        options={{
          background: { color: { value: "transparent" } },
          fpsLimit: 60,
          interactivity: {
            events: { onHover: { enable: true, mode: "repulse" } },
            modes: { repulse: { distance: 100, duration: 0.4 } },
          },
          particles: {
            color: { value: "#a3e635" },
            links: { color: "#a3e635", distance: 150, enable: true, opacity: 0.08, width: 1 },
            move: { enable: true, speed: 0.8, direction: "none", outModes: { default: "bounce" } },
            number: { density: { enable: true, area: 800 }, value: 40 },
            opacity: { value: 0.15 },
            shape: { type: "circle" },
            size: { value: { min: 1, max: 2 } },
          },
        }}
        className="absolute inset-0 z-0"
      />

      <div className="relative z-10">
        <Navbar wsConnected={wsConnected} />

        <div className="p-4 md:p-6 pt-8 max-w-[1560px] mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">

            {/* Row 1: Core Intelligence */}
            <div className="col-span-1 h-[300px]">
              <CardStack3D />
            </div>

            <div className="col-span-1 h-[300px]">
              <NeonDonut riskScore={latestScore} />
            </div>

            <div className="col-span-1 md:col-span-2 lg:col-span-2 lg:row-span-2">
              <AIDecisionPanel latestTx={transactions[0]} />
            </div>

            {/* Row 2: Metrics + Timeline */}
            <div className="col-span-1 h-[300px]">
              <ModelMetricsPanel metrics={modelMetrics} />
            </div>

            <div className="col-span-1 h-[300px]">
              <UserContextCard latestTx={transactions[0]} />
            </div>

            {/* Row 3: Monitoring */}
            <div className="col-span-1 md:col-span-2 h-[340px]">
              <AnomalyTimeline data={transactions} />
            </div>

            <div className="col-span-1 h-[340px]">
              <GeoThreatMap transactions={transactions} />
            </div>

            <div className="col-span-1 h-[340px]">
              <SystemAuditTerminal />
            </div>

            {/* Row 4: Actions */}
            <div className="col-span-1 lg:col-span-1 h-[300px]">
              <RiskAlertFeed transactions={transactions} />
            </div>

            <div className="col-span-1 md:col-span-2 lg:col-span-3 h-[300px]">
              <SuspiciousTransactions transactions={transactions} onFeedback={handleFeedback} />
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
