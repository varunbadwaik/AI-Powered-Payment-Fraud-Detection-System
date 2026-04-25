export default function TransactionTable({ data }) {
  return (
    <div className="bg-[#161B22] p-5 rounded-xl">
      <h2 className="text-xl mb-4">Recent Transactions</h2>

      <table className="w-full text-left">
        <thead>
          <tr className="text-gray-400">
            <th>ID</th>
            <th>Score</th>
            <th>Risk</th>
          </tr>
        </thead>

        <tbody>
          {data.map(tx => (
            <tr key={tx.id} className="border-t border-gray-700">
              <td>{tx.id.substring(0, 8)}...</td>
              <td>{tx.score.toFixed(2)}</td>
              <td className={
                tx.risk === "High" ? "text-red-500" :
                tx.risk === "Medium" ? "text-yellow-400" :
                "text-green-400"
              }>
                {tx.risk}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
