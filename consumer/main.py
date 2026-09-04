from kafka import KafkaConsumer
import json
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="stock_analytics",
    user="postgres",
    password="postgres"
)

cur = conn.cursor()

consumer = KafkaConsumer(
    "stock-prices",
    bootstrap_servers=["localhost:9092"],
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

for message in consumer:
    data = message.value

    cur.execute(
        """
        INSERT INTO stock_prices
        (symbol, price, event_timestamp)
        VALUES (%s, %s, %s)
        """,
        (
            data["symbol"],
            data["price"],
            data["timestamp"]
        )
    )

    conn.commit()

    print("Inserted:", data)