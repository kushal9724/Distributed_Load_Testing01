# orchestrator.py

from flask import Flask, request
from confluent_kafka import Producer
import json
import uuid

app = Flask(__name__)

class Orchestrator:
    def __init__(self, kafka_bootstrap_servers):
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.orchestrator_id = str(uuid.uuid4())
        self.orchestrator_ip = "127.0.0.1"  # Replace with the actual IP

    def register_node(self, node_id, node_ip, message_type):
        registration_message = {
            "node_id": node_id,
            "node_ip": node_ip,
            "message_type": message_type
        }
        print(f"Node registered: {registration_message}")

    def publish_test_config(self, test_type, test_message_delay):
        test_id = str(uuid.uuid4())
        test_config_message = {
            "test_id": test_id,
            "test_type": test_type,
            "test_message_delay": test_message_delay
        }
        producer = Producer({"bootstrap.servers": self.kafka_bootstrap_servers})
        producer.produce("test_config", json.dumps(test_config_message).encode("utf-8"))
        producer.flush()
        return test_id

    def publish_trigger_message(self, test_id):
        trigger_message = {
            "test_id": test_id,
            "trigger": "YES"
        }
        producer = Producer({"bootstrap.servers": self.kafka_bootstrap_servers})
        producer.produce("trigger", json.dumps(trigger_message).encode("utf-8"))
        producer.flush()
        return f"Trigger message published for Test ID: {test_id}"

    def start_load_test(self):
        delay_interval = float(request.form.get("delay_interval", 0))
        target_throughput = int(request.form.get("target_throughput", 1))

        self.register_node(self.orchestrator_id, self.orchestrator_ip, "ORCHESTRATOR_NODE_REGISTER")

        test_id = self.publish_test_config("AVALANCHE" if delay_interval == 0 else "TSUNAMI", delay_interval)
        self.publish_trigger_message(test_id)

        if delay_interval > 0:
            self.tsunami_test(delay_interval, target_throughput)
        else:
            self.avalanche_test(target_throughput)

        return f"Load test started with Test ID: {test_id}"

    def tsunami_test(self, delay_interval, target_throughput):
        # Implement Tsunami test logic
        pass

    def avalanche_test(self, target_throughput):
        # Implement Avalanche test logic
        pass

orchestrator = Orchestrator("localhost:9092")

@app.route("/start_load_test", methods=["POST"])
def start_load_test():
    return orchestrator.start_load_test()

@app.route("/")
def home():
    return "Welcome to the Orchestrator Node!"


if __name__ == "__main__":
    app.run(port=5000)
