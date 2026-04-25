import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function Charts({ data }) {
  // Process data for charts
  const lineData = [...data].reverse().map(tx => ({
    time: tx.id.substring(8, 13), // mock time from ID
    score: tx.score
  }));

  const riskCounts = data.reduce((acc, tx) => {
    acc[tx.risk] = (acc[tx.risk] || 0) + 1;
    return acc;
  }, { Low: 0, Medium: 0, High: 0 });

  const pieData = [
    { name: 'Low', value: riskCounts.Low, color: '#4ADE80' },
    { name: 'Medium', value: riskCounts.Medium, color: '#FACC15' },
    { name: 'High', value: riskCounts.High, color: '#EF4444' }
  ];

  return (
    <div className="grid grid-cols-3 gap-4 mb-6">
      <div className="col-span-2 bg-[#161B22] p-5 rounded-xl shadow-md h-80">
        <h3 className="text-gray-400 mb-4">Risk Score Trend</h3>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={lineData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="time" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" domain={[0, 100]} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1F2937', border: 'none' }}
              itemStyle={{ color: '#F3F4F6' }}
            />
            <Line 
              type="monotone" 
              dataKey="score" 
              stroke="#60A5FA" 
              strokeWidth={2}
              dot={{ fill: '#60A5FA', r: 4 }}
              activeDot={{ r: 6 }} 
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      <div className="col-span-1 bg-[#161B22] p-5 rounded-xl shadow-md h-80">
        <h3 className="text-gray-400 mb-4">Risk Distribution</h3>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={pieData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
            >
              {pieData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip 
              contentStyle={{ backgroundColor: '#1F2937', border: 'none' }}
              itemStyle={{ color: '#F3F4F6' }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
