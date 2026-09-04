import { useEffect, useMemo, useState } from "react";
import "./App.css";

interface Stock {
  symbol: string;
  price: number;
  event_timestamp: number;
  created_at?: string;
}

interface SearchResult {
  symbol: string;
  description: string;
  type: string;
}

interface NewsItem {
  headline: string;
  source: string;
  url: string;
  datetime: number;
  image?: string;
}

const API_BASE = "http://localhost:8000";

function formatTime(value?: number | string) {
  if (!value) return "--";
  const date = new Date(typeof value === "number" ? value * 1000 : value);
  return Number.isNaN(date.getTime()) ? "--" : date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function App() {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [history, setHistory] = useState<Stock[]>([]);
  const [selectedSymbol, setSelectedSymbol] = useState("ALL");
  const [isOnline, setIsOnline] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [news, setNews] = useState<NewsItem[]>([]);

  useEffect(() => {
    let isMounted = true;
    const loadDashboard = async () => {
      try {
        const [marketResponse, historyResponse, healthResponse] = await Promise.all([
          fetch(`${API_BASE}/market/latest`),
          fetch(`${API_BASE}/stocks/history?limit=80`),
          fetch(`${API_BASE}/health`),
        ]);
        if (!marketResponse.ok || !historyResponse.ok || !healthResponse.ok) throw new Error("The API returned an error");
        const [market, recentHistory] = await Promise.all([
          marketResponse.json() as Promise<Stock[]>,
          historyResponse.json() as Promise<Stock[]>,
        ]);
        if (isMounted) {
          setStocks(market);
          setHistory(recentHistory);
          setIsOnline(true);
          setLastUpdated(new Date());
          setError("");
        }
      } catch {
        if (isMounted) {
          setIsOnline(false);
          setError("Unable to reach the market data service.");
        }
      }
    };
    loadDashboard();
    const interval = window.setInterval(loadDashboard, 5000);
    return () => { isMounted = false; window.clearInterval(interval); };
  }, []);

  useEffect(() => {
    if (searchQuery.trim().length < 2) {
      setSearchResults([]);
      return;
    }
    const timeout = window.setTimeout(async () => {
      try {
        const response = await fetch(`${API_BASE}/stocks/search?query=${encodeURIComponent(searchQuery.trim())}`);
        if (response.ok) setSearchResults(await response.json() as SearchResult[]);
      } catch { setSearchResults([]); }
    }, 300);
    return () => window.clearTimeout(timeout);
  }, [searchQuery]);

  useEffect(() => {
    const loadNews = async () => {
      try {
        const query = selectedSymbol === "ALL" ? "" : `?symbol=${encodeURIComponent(selectedSymbol)}`;
        const response = await fetch(`${API_BASE}/news${query}`);
        if (response.ok) setNews(await response.json() as NewsItem[]);
      } catch { setNews([]); }
    };
    loadNews();
  }, [selectedSymbol]);

  const visibleStocks = useMemo(
    () => selectedSymbol === "ALL" ? stocks : stocks.filter((stock) => stock.symbol === selectedSymbol),
    [selectedSymbol, stocks],
  );
  const visibleHistory = useMemo(
    () => selectedSymbol === "ALL" ? history : history.filter((stock) => stock.symbol === selectedSymbol),
    [history, selectedSymbol],
  );
  const averagePrice = visibleStocks.length ? visibleStocks.reduce((total, stock) => total + stock.price, 0) / visibleStocks.length : 0;
  const latestTrade = visibleHistory[0];

  return (
    <main className="dashboard-shell">
      <nav className="topbar">
        <a className="brand" href="/" aria-label="Market Pulse home"><span className="brand-mark">MP</span><span>Market Pulse</span></a>
        <div className="topbar-meta"><span className={`connection-dot ${isOnline ? "online" : "offline"}`} /><span>{isOnline ? "Live connection" : "Service offline"}</span><span className="refresh-label">5s refresh</span></div>
      </nav>
      <section className="intro">
        <div><p className="eyebrow">REAL-TIME MARKET INTELLIGENCE</p><h1>Today in the market</h1><p className="intro-copy">A clear view of the latest prices flowing through your analytics platform.</p></div>
        <div className="intro-side">
          <div className="update-stamp"><span className="pulse-ring" />Updated {lastUpdated ? lastUpdated.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "--"}</div>
          <section className="news-panel panel news-panel-top">
            <div className="compact-news-heading"><div><p className="eyebrow">MARKET NEWS</p><h2>{selectedSymbol === "ALL" ? "Latest headlines" : `${selectedSymbol} news`}</h2></div><span className="activity-count">Finnhub</span></div>
            <div className="news-grid">{news.slice(0, 2).map((item) => <a className="news-item" href={item.url} target="_blank" rel="noreferrer" key={`${item.url}-${item.datetime}`}><span>{item.source} · {formatTime(item.datetime)}</span><strong>{item.headline}</strong></a>)}{!news.length && <p className="empty-state">No news available right now.</p>}</div>
          </section>
        </div>
      </section>
      {error && <div className="error-banner" role="alert">{error} Check that the backend is running on port 8000.</div>}
      <section className="search-section">
        <label className="search-label" htmlFor="stock-search">Find any listed stock</label>
        <div className="search-box"><span>⌕</span><input id="stock-search" value={searchQuery} onChange={(event) => setSearchQuery(event.target.value)} placeholder="Search by symbol or company name" /></div>
        {searchResults.length > 0 && <div className="search-results">{searchResults.map((result) => <button type="button" key={result.symbol} onClick={() => { setSelectedSymbol(result.symbol); setSearchQuery(result.symbol); setSearchResults([]); }}><b>{result.symbol}</b><span>{result.description}</span></button>)}</div>}
      </section>
      <section className="metric-grid" aria-label="Market summary">
        <article className="metric-card metric-card-dark"><span className="metric-label">Tracked symbols</span><strong>{visibleStocks.length}</strong><span className="metric-detail">Across the latest market snapshot</span></article>
        <article className="metric-card"><span className="metric-label">Average price</span><strong>${averagePrice.toFixed(2)}</strong><span className="metric-detail">Current filtered average</span></article>
        <article className="metric-card metric-card-accent"><span className="metric-label">Latest trade</span><strong>{latestTrade ? `$${latestTrade.price.toFixed(2)}` : "--"}</strong><span className="metric-detail">{latestTrade ? `${latestTrade.symbol} at ${formatTime(latestTrade.event_timestamp)}` : "Waiting for data"}</span></article>
      </section>
      <section className="content-grid">
        <div className="panel watchlist-panel">
          <div className="panel-heading"><div><p className="eyebrow">LIVE SNAPSHOT</p><h2>Market watchlist</h2></div><label className="select-wrap"><span className="sr-only">Filter symbol</span><select value={selectedSymbol} onChange={(event) => setSelectedSymbol(event.target.value)}><option value="ALL">All symbols</option>{stocks.map((stock) => <option key={stock.symbol} value={stock.symbol}>{stock.symbol}</option>)}</select></label></div>
          <div className="table-scroll"><table><thead><tr><th>Symbol</th><th>Last price</th><th>Event time</th><th>Signal</th></tr></thead><tbody>
            {visibleStocks.map((stock) => <tr key={stock.symbol}><td><span className="symbol-badge">{stock.symbol.slice(0, 1)}</span><b>{stock.symbol}</b></td><td className="price-cell">${stock.price.toFixed(2)}</td><td>{formatTime(stock.event_timestamp)}</td><td><span className="signal">Streaming</span></td></tr>)}
            {!visibleStocks.length && <tr><td className="empty-state" colSpan={4}>No market data available yet.</td></tr>}
          </tbody></table></div>
        </div>
        <div className="panel activity-panel">
          <div className="panel-heading"><div><p className="eyebrow">RECENT ACTIVITY</p><h2>Price flow</h2></div><span className="activity-count">{visibleHistory.length} events</span></div>
          <div className="activity-list">{visibleHistory.slice(0, 7).map((stock, index) => <div className="activity-row" key={`${stock.symbol}-${stock.event_timestamp}-${index}`}><span className="activity-line" /><div><b>{stock.symbol}</b><span>{formatTime(stock.event_timestamp)}</span></div><strong>${stock.price.toFixed(2)}</strong></div>)}{!visibleHistory.length && <p className="empty-state">No recent events available.</p>}</div>
        </div>
      </section>
      <footer>Market Pulse <span>•</span> Powered by your real-time stock analytics API</footer>
    </main>
  );
}

export default App;