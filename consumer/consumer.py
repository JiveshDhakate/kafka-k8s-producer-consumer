from kafka import KafkaConsumer
import os, json

# --------- env-vars with safe defaults ----------
BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC             = os.getenv("TOPIC",             "my_topic")
GROUP_ID          = os.getenv("GROUP_ID",          "new_group_1")

def safe_json_deserializer(x: bytes):
    try:
        return json.loads(x.decode("utf-8"))
    except json.JSONDecodeError:
        print("Skipped non-JSON message"); return None

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id=GROUP_ID,
    value_deserializer=safe_json_deserializer,
)

print(f" Listening on {BOOTSTRAP_SERVERS}/{TOPIC} (group {GROUP_ID})\n", flush=True)

for msg in consumer:
    if msg.value is not None:
        print(f"Received event: {msg.value}", flush=True)
