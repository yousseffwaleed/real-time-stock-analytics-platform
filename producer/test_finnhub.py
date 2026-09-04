# test_producer.py

from confluent_kafka import Producer
import json

p = Producer({
    "bootstrap.servers": "localhost:9092"
})

event = {
    "symbol": "TEST",
    "price": 123
}

p.produce(
    "stock-prices",
    json.dumps(event)
)

p.flush()

print("Sent!")