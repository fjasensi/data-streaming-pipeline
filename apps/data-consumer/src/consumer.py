import json
import os
from kafka import KafkaConsumer


KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC', 'events-aggregated')

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset='latest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def main():
    print(f"Starting Kafka consumer - Connecting to {KAFKA_BOOTSTRAP_SERVERS} - Topic: {KAFKA_TOPIC}")

    try:
            for message in consumer:
                data = message.value
                print(f"Received data: {data}")

                # TODO: Options
                # 1. Store data in a database
                # 2. Update a dashboard
                # 3. Trigger alerts based on thresholds
                # 4. etc.

    except KeyboardInterrupt:
        print("Consumer stopped by user")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()
