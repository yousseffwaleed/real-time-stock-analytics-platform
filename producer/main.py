from kafka import KafkaProducer
import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("FINNHUB_API_KEY")

symbols = [
    "AAPL",
    "MSFT",
    "NVDA",
    "GOOGL",
    "AMZN",
    "META",
    "TSLA",
    "AMD",
    "NFLX",
    "PLTR"
]

if not api_key:
    raise ValueError("FINNHUB_API_KEY is missing")

producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

while True:
    try:
        for symbol in symbols:
            response = requests.get(
                f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}",
                timeout=10,
            )

            response.raise_for_status()

            data = response.json()

            event = {
                "symbol": symbol,
                "price": data["c"],
                "timestamp": data["t"]
            }

            producer.send("stock-prices", event).get(timeout=10)

            print("Sent:", event)

    except Exception as exc:
        print("Producer error:", exc)

        time.sleep(10)