import { useEffect, useState } from "react";

interface Stock {
  symbol: string;
  price: number;
  event_timestamp: number;
}

function App() {
  const [stocks, setStocks] = useState<Stock[]>([]);

  useEffect(() => {
  const loadStocks = () => {
    fetch("http://localhost:8000/market/latest")
      .then(res => res.json())
      .then(data => setStocks(data));
  };

  loadStocks();

  const interval = setInterval(loadStocks, 5000);

  return () => clearInterval(interval);
}, []);

  return (
    <div style={{ padding: "20px" }}>
      <h1>Real-Time Stock Analytics Dashboard</h1>

      <table>
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Price</th>
          </tr>
        </thead>

        <tbody>
          {stocks.map((stock) => (
            <tr key={stock.symbol}>
              <td>{stock.symbol}</td>
              <td>${stock.price.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;