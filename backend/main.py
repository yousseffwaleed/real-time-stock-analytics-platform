import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
import psycopg2
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="stock_analytics",
        user="postgres",
        password="postgres"
    )


@app.get("/")
def root():
    return {"message": "Stock Analytics API"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/stocks/search")
def search_stocks(query: str = Query(min_length=1, max_length=40)):
    if not FINNHUB_API_KEY:
        raise HTTPException(status_code=500, detail="FINNHUB_API_KEY is missing")

    response = requests.get(
        "https://finnhub.io/api/v1/search",
        params={"q": query, "token": FINNHUB_API_KEY},
        timeout=10,
    )
    response.raise_for_status()
    return [
        {"symbol": item["symbol"], "description": item.get("description", ""), "type": item.get("type", "")}
        for item in response.json().get("result", [])[:10]
    ]


@app.get("/news")
def market_news(symbol: str | None = Query(default=None, max_length=20)):
    if not FINNHUB_API_KEY:
        raise HTTPException(status_code=500, detail="FINNHUB_API_KEY is missing")

    endpoint = "company-news" if symbol else "news"
    params = {"token": FINNHUB_API_KEY}
    if symbol:
        from datetime import date, timedelta
        today = date.today()
        params.update({"symbol": symbol.upper(), "from": str(today - timedelta(days=7)), "to": str(today)})
    else:
        params["category"] = "general"

    response = requests.get(f"https://finnhub.io/api/v1/{endpoint}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()[:10]


@app.get("/stocks/latest")
def latest_price():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT symbol,
               price,
               event_timestamp,
               created_at
        FROM stock_prices
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="No stock data found")

    return {
        "symbol": row[0],
        "price": float(row[1]),
        "event_timestamp": row[2],
        "created_at": str(row[3])
    }


@app.get("/stocks/history")
def stock_history(limit: int = 100):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT symbol,
               price,
               event_timestamp,
               created_at
        FROM stock_prices
        ORDER BY id DESC
        LIMIT %s
    """, (limit,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "symbol": row[0],
            "price": float(row[1]),
            "event_timestamp": row[2],
            "created_at": str(row[3])
        }
        for row in rows
    ]


@app.get("/stocks/symbols")
def symbols():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT symbol
        FROM stock_prices
        ORDER BY symbol
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [row[0] for row in rows]


@app.get("/stocks")
def recent_stocks(limit: int = 50):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id,
               symbol,
               price,
               event_timestamp,
               created_at
        FROM stock_prices
        ORDER BY id DESC
        LIMIT %s
    """, (limit,))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": row[0],
            "symbol": row[1],
            "price": float(row[2]),
            "event_timestamp": row[3],
            "created_at": str(row[4])
        }
        for row in rows
    ]


@app.get("/stocks/{symbol}")
def stock_by_symbol(symbol: str):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT symbol,
               price,
               event_timestamp,
               created_at
        FROM stock_prices
        WHERE symbol = %s
        ORDER BY id DESC
        LIMIT 1
    """, (symbol.upper(),))

    row = cur.fetchone()

    cur.close()
    conn.close()

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for symbol {symbol}"
        )

    return {
        "symbol": row[0],
        "price": float(row[1]),
        "event_timestamp": row[2],
        "created_at": str(row[3])
    }


@app.get("/market/latest")
def latest_market():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT ON (symbol)
            symbol,
            price,
            event_timestamp
        FROM stock_prices
        ORDER BY symbol, id DESC
    """)

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "symbol": row[0],
            "price": float(row[1]),
            "event_timestamp": row[2]
        }
        for row in rows
    ]