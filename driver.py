# driver.py

from confluent_kafka import Consumer, Producer, KafkaError
from flask import Flask, request
import json
import uuid
import random

app = Flask(__name__)

class Driver:
    def __init__(self, kafka_bootstrap_servers):
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.driver_id = str(uuid.uuid4())
        self.orchestrator_ip = "127.0.0.1"  # Replace with the actual Orchestrator IP
        self.request_count = 0

    def register_node(self, node_id, node_ip, message_type):
        registration_message = {
            "node_id": node_id,
            "node_ip": node_ip,
            "message_type": message_type
        }
        print(f"Node registered: {registration_message}")

    def publish_metrics(self, test_id, report_id, metrics):
        metrics_message = {
            "node_id": self.driver_id,
            "test_id": test_id,
            "report_id": report_id,
            "metrics": metrics
        }
        producer = Producer({"bootstrap.servers": self.kafka_bootstrap_servers})
        producer.produce("metrics", json.dumps(metrics_message).encode("utf-8"))
        producer.flush()

    def publish_heartbeat(self):
        heartbeat_message = {
            "node_id": self.driver_id,
            "heartbeat": "YES"
        }
        producer = Producer({"bootstrap.servers": self.kafka_bootstrap_servers})
        producer.produce("heartbeat", json.dumps(heartbeat_message).encode("utf-8"))
        producer.flush()

    def consume_metrics(self):
        consumer = Consumer({
            'bootstrap.servers': self.kafka_bootstrap_servers,
            'group.id': 'my-group',
            'auto.offset.reset': 'earliest'
        })
        consumer.subscribe(['metrics'])

        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break

            metrics = json.loads(msg.value().decode('utf-8'))
            print(f"Driver {self.driver_id} received metrics from Orchestrator:", metrics)

            self.request_count = metrics.get("requests_sent", 0)

            if self.request_count % 10 == 0:
                report_id = str(uuid.uuid4())
                aggregate_metrics = {
                    "mean_latency": random.uniform(10, 25),
                    "median_latency": random.uniform(8, 20),
                    "min_latency": random.uniform(5, 15),
                    "max_latency": random.uniform(30, 50),
                }

                self.publish_metrics(metrics["test_id"], report_id, aggregate_metrics)

            if self.request_count % 5 == 0:
                self.publish_heartbeat()

driver = Driver("localhost:9092")

@app.route("/")
def home():
    return "Welcome to the Driver Node!"

@app.route("/register", methods=["POST"])
def register_node():
    driver.register_node(driver.driver_id, "127.0.0.1", "DRIVER_NODE_REGISTER")
    return "Node registered successfully"

@app.route("/consume_metrics", methods=["POST"])
def consume_metrics():
    driver.consume_metrics()
    return "Metrics consumption started"

if __name__ == "__main__":
    app.run(port=5001)
