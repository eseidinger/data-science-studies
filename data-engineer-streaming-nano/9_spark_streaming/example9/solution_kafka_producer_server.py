from kafka import KafkaProducer
import json
import time
from confluent_kafka.admin import AdminClient, NewTopic

BROKER_HOST_PORT = "localhost:9092"
BROKER_URL = f"PLAINTEXT://{BROKER_HOST_PORT}"
TOPIC_NAME = "uber-topic"
INPUT_FILE = "data/uber.json"

class ProducerServer(KafkaProducer):

    def __init__(self, input_file, topic, **kwargs):
        super().__init__(**kwargs)
        self.input_file = input_file
        self.topic = topic

    def generate_data(self):
        with open(self.input_file) as f:
            data = json.loads(f.read())
            for line in data:
                print(line)
                message = self.dict_to_binary(line)
                self.send(self.topic, message)
                time.sleep(1)

    def dict_to_binary(self, json_dict):
        return json.dumps(json_dict).encode('utf-8')


def topic_exists(client, topic_name):
    """Checks if the given topic exists"""
    topic_metadata = client.list_topics(timeout=5)
    return topic_name in set(t.topic for t in iter(topic_metadata.topics.values()))


def create_topic(client, topic_name):
    """Creates the topic with the given topic name"""
    futures = client.create_topics(
        [
            NewTopic(
                topic=topic_name,
                num_partitions=1,
                replication_factor=1,
            )
        ]
    )

    for topic, future in futures.items():
        try:
            future.result()
            print("topic created")
        except Exception as e:
            print(f"failed to create topic {topic_name}: {e}")


def main():
    """Runs the exercise"""
    client = AdminClient({"bootstrap.servers": BROKER_URL})

    exists = topic_exists(client, TOPIC_NAME)
    print(f"Topic {TOPIC_NAME} exists: {exists}")

    if exists is False:
        create_topic(client, TOPIC_NAME)

    producerServer = ProducerServer(INPUT_FILE, TOPIC_NAME, bootstrap_servers = BROKER_HOST_PORT)
    producerServer.generate_data()


if __name__ == "__main__":
    main()
