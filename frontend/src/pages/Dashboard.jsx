import { useState, useEffect } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import Navbar from "../components/Navbar";
import RiskCard from "../components/RiskCard";
import Charts from "../components/Charts";
import TransactionTable from "../components/TransactionTable";

export default function Dashboard() {
  const [data, setData] = useState({
    score: 0,
    risk: "Low"
  });

  const [transactions, setTransactions] = useState([]);

  const fetchPrediction = async () => {
    try {
      const res = await axios.post("http://localhost:8000/api/v1/predict", {
        amount: Math.random() * 10000,
        merchant_category: "online_retail",
        transaction_hour: Math.floor(Math.random() * 24),
        day_of_week: 3,
        location_distance_km: 5.0,
        is_international: false,
        card_present: false,
        velocity_last_1h: 1,
        avg_amount_30d: 120.0
      });

      const processedData = {
        score: res.data.fraud_probability * 100,
        risk: res.data.risk_level
      };

      setData(processedData);

      setTransactions(prev => [
        { ...processedData, id: res.data.transaction_id || Date.now().toString() },
        ...prev.slice(0, 9) // Keep last 10 for charts to look good
      ]);

    } catch (err) {
      console.error(err);
    }
  };

  // 🔥 LIVE SIMULATION
  useEffect(() => {
    const interval = setInterval(fetchPrediction, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-[#0E1117] min-h-screen text-white">
      <Navbar />
      
      <div className="px-6 max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">
          💳 Fraud Detection Dashboard
        </h1>

        {/* Risk Cards */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <RiskCard title="Risk Score" value={data.score.toFixed(2)} />
          <RiskCard title="Risk Level" value={data.risk} />
          <RiskCard title="Status" value={data.risk === "High" ? "🔴" : data.risk === "Medium" ? "🟠" : "🟢"} />
        </div>

        {/* Animated Alert */}
        {data.risk === "High" && (
          <motion.div 
            className="bg-red-600/20 border-l-4 border-red-500 p-4 rounded mb-6 flex items-center"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <span className="text-red-400 font-semibold">🚨 HIGH RISK TRANSACTION DETECTED. Immediate block applied.</span>
          </motion.div>
        )}
        {data.risk === "Medium" && (
          <motion.div 
            className="bg-yellow-600/20 border-l-4 border-yellow-500 p-4 rounded mb-6 flex items-center"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <span className="text-yellow-400 font-semibold">⚠️ MEDIUM RISK TRANSACTION. Escalated for manual review.</span>
          </motion.div>
        )}

        {/* Charts */}
        {transactions.length > 0 && <Charts data={transactions} />}

        {/* Transactions */}
        <TransactionTable data={transactions} />
      </div>
    </div>
  );
}
