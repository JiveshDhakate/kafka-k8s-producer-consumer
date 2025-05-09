
# Kafka Producer–Consumer on Kubernetes (Single‑Node KRaft Demo)

This guide walks you from **zero** to a running Kafka pipeline inside Kubernetes:
Python **producer → Kafka (KRaft) → Python consumer**.

---

## 📦 Project layout

```
project/
├─ producer/                 # Python producer (+ Dockerfile)
├─ consumer/                 # Python consumer (+ Dockerfile)
└─ k8s/
    ├─ kafka.yaml            # Broker Deployment + Service (ports 9092/9093)
    ├─ producer-deployment.yaml
    └─ consumer-deployment.yaml
```

---

## 0.  Prerequisites

| Tool | Quick check |
|------|-------------|
| **Docker CLI** | `docker --version` |
| **kubectl** | `kubectl version --client` |
| **Minikube / Kind / Kubernetes cluster** | `kubectl get nodes` |
| Docker registry account | `docker login` |

---

## 1.  Start a local cluster

```bash
minikube start                          # or: kind create cluster
kubectl create namespace kafka-demo
```

---

## 2.  Build & push images

## Optional I have included my docker image from Docker Hub
# consumer-image : jiveshdhakate04/kafka-python-consumer:v1 (Deployment)
# producer-image : jiveshdhakate04/kafka-python-producer:v1 (Deployment)

```bash
# Producer
docker build -t <DOCKER_USER>/kafka-python-producer:v1 ./producer
docker push <DOCKER_USER>/kafka-python-producer:v1

# Consumer
docker build -t <DOCKER_USER>/kafka-python-consumer:v1 ./consumer
docker push <DOCKER_USER>/kafka-python-consumer:v1
```

---

## 3.  Deploy Kafka (single‑node KRaft)

```bash
kubectl apply -f k8s/kafka.yaml
kubectl -n kafka-demo rollout status deploy/kafka
```

> The manifest exposes **9092** (client) and **9093** (controller).

---

## 4.  Create the demo topic (once)

```bash
kubectl -n kafka-demo exec deploy/kafka --   /opt/bitnami/kafka/bin/kafka-topics.sh     --create     --bootstrap-server kafka:9092     --topic my_topic     --partitions 3     --replication-factor 1
```

---

## 5.  Deploy producer & consumer

```bash
kubectl apply -f k8s/producer-deployment.yaml
kubectl apply -f k8s/consumer-deployment.yaml
```

---

## 6.  Verify the pipeline

```bash
kubectl -n kafka-demo logs -f deploy/kafka-python-producer
kubectl -n kafka-demo logs -f deploy/kafka-python-consumer
```

Output should resemble:

```
Producer: Sent {'event_id': 0, ...}
Consumer: Received event: {'event_id': 0, ...}
```

---

## 7.  Quick functional tests

| Action | Command |
|--------|---------|
| List topics | `kubectl exec deploy/kafka -n kafka-demo -- /opt/bitnami/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --list` |
| Replay messages | `kubectl rollout restart deploy/kafka-python-producer -n kafka-demo` |
| Scale consumers | `kubectl scale deploy/kafka-python-consumer -n kafka-demo --replicas=3` |

---

## 8.  Clean‑up

```bash
kubectl delete ns kafka-demo
minikube stop    # or: kind delete cluster
```

---

## Why we **don’t** create a Kubernetes Service for the producer or consumer

| Component | Who initiates the TCP connection? | Needs to be called by others? | Service required? |
|-----------|-----------------------------------|-------------------------------|-------------------|
| **Kafka broker** | Clients (producers / consumers) dial *in* to port 9092 (+ 9093 for KRaft). | Yes — must be reachable 24/7. | **Yes** (`kafka` ClusterIP). |
| **Producer pod** | *It* dials *out* to the Kafka Service, sends a few records, exits. | No — nothing ever calls the producer. | **No** |
| **Consumer pod** | *It* dials *out* to the Kafka Service, pulls records. | No — nothing calls the consumer. | **No** |

### TL;DR

A Kubernetes **Service** is only needed for workloads that must accept **inbound** connections.  
The producer and consumer are *clients* (outbound-only), so exposing them would just create an unused ClusterIP.

Create a Service for them **only** if you later add:

* an HTTP endpoint (e.g. `/metrics` or a REST API),  
* a webhook receiver, or  
* some other feature that other pods or users must call.

