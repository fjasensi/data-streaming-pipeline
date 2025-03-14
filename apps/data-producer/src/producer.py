import os
import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer


KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'events-raw')
INTERVAL_SECONDS = int(os.environ.get('INTERVAL_SECONDS', '1'))

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_event():
    products = ["laptop", "smartphone", "tablet", "headphones", "monitor"]
    countries = ["Spain", "USA", "Mexico", "Argentina", "Colombia"]
    
    return {
        "timestamp": datetime.now().isoformat(),
        "product": random.choice(products),
        "price": round(random.uniform(50, 2000), 2),
        "quantity": random.randint(1, 5),
        "country": random.choice(countries),
        "transaction_id": f"tx-{random.randint(10000, 99999)}"
    }

def main():
    print(f"Starting Kafka producer - Sending to {KAFKA_BOOTSTRAP_SERVERS} - Topic: {KAFKA_TOPIC}")
    
    while True:
        event = generate_event()
        producer.send(KAFKA_TOPIC, event)
        print(f"Message sent: {event}")
        time.sleep(INTERVAL_SECONDS)
    
        
if __name__ == "__main__":
    main()
