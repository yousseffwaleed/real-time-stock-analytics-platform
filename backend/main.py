from fastapi import FastAPI, HTTPException
import psycopg2
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
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