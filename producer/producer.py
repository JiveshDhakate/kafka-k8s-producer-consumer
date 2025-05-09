from kafka import KafkaProducer
import os, json, time, sys

# --------------------------------------------------------------------
# Env-vars (defaults let it run in Docker Compose / K8s demo clusters)
# --------------------------------------------------------------------
BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC             = os.getenv("TOPIC",             "my_topic")
COUNT             = int(os.getenv("COUNT", "5"))        

# --------------------------------------------------------------------
# Producer instance
# --------------------------------------------------------------------
producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    acks="all",                 # wait for broker ack
    linger_ms=20,               # tiny batch for demo
)

print(f"🚀  Producer started → {BOOTSTRAP_SERVERS}/{TOPIC}", flush=True)

# --------------------------------------------------------------------
# Send N demo events
# --------------------------------------------------------------------
for i in range(COUNT):
    event = {
        "event_id": i,
        "status": "success",
        "message": f"Event {i} processed"
    }
    try:
        fut = producer.send(TOPIC, value=event)   
        meta = fut.get(timeout=10)
        print(
            f"Sent {event} → partition {meta.partition}, offset {meta.offset}",
            flush=True
        )
    except Exception as e:
        print(f"Failed to send {event}: {e}", file=sys.stderr, flush=True)
    time.sleep(1)

producer.flush()
producer.close()
print("Done, exiting.", flush=True)
