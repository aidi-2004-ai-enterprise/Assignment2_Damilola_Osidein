# Assignment2_DamilolaOsidein

# README.md

## Project overview

This repository contains a RESTful service that exposes a machine learning model for predicting vehicle CO₂ emissions. The service is implemented as a Python web app (Flask/FastAPI — replace with your chosen framework) and packaged as a container for deployment to Google Cloud Run.

Key responsibilities:

* Accept prediction requests (JSON) and return CO₂ estimates.
* Validate inputs and handle edge cases gracefully.
* Provide health and readiness endpoints for platform orchestration.
* Log predictions for observability and retraining.

---

## Features

* **/predict** endpoint: accepts vehicle parameters, returns predicted CO₂ and confidence.
* **/health** endpoint: simple health probe.
* Configurable model and preprocessing loaded at startup.
* Docker-ready, ready for Cloud Run deployment.

# README — Production Q\&A

This README answers common production questions for the ML inference service (concise, actionable, and ready to include in your repository).

---

## What edge cases might break your model in production that aren't in your training data?

* **Distribution / concept drift:** new vehicle types, fuel or feature distributions not seen during training.

  * *Mitigation:* monitor input/prediction distributions, alert on drift, schedule retraining and canary evaluations.
* **Unseen categorical values:** new makes, trims, locale-specific tokens.

  * *Mitigation:* map unknowns to `__UNKNOWN__`, return clear validation warnings, and capture samples for labeling.
* **Unit and formatting mismatches:** cc vs liters, kg vs lb, string vs numeric.

  * *Mitigation:* strict schema + unit normalization, and explicit examples in API docs.
* **Missing / null / malformed fields:** incomplete payloads or wrongly typed fields.

  * *Mitigation:* schema validation (JSON Schema, pydantic), clear error messages (400/422), and logging of missingness.
* **Adversarial or extremely out-of-range inputs:** intentionally crafted values, extremely large numbers or payloads.

  * *Mitigation:* payload size limits, input sanitization, rate limiting, anomaly detection.
* **Time-dependent mismatches:** future years, daylight savings/timezone issues, discontinuities.

  * *Mitigation:* validate date ranges, use canonical UTC handling, and add business rules.

---

## What happens if your model file becomes corrupted?

* **Startup:** a corrupted model should cause the service to fail-fast and exit non-zero so orchestration notices a bad image.
* **Runtime:** if loading on-demand, the service must return `503 Service Unavailable` for inference and log the failure.

**How to prevent and recover:**

1. Use checksums/signatures (SHA256) and validate before loading.
2. Keep a versioned model registry and a fallback model to load automatically.
3. Run CI smoke tests on artifacts before deployment.
4. Alert on model load or repeated `5xx` responses and enable an automated rollback if necessary.

---

## What's a realistic load for a penguin classification service?

Depends on the input type and user base:

* **Small demo / research:** 0.1–5 RPS.
* **Moderate mobile app usage:** 10–200 RPS.
* **High-traffic public API:** 1k+ RPS (requires GPU/optimized infra for image work).

**Example (image classification on CPU):** if each image takes 150 ms to infer on 1 vCPU, that’s \~6 RPS per vCPU. With concurrency 10 you might reach \~60 RPS per 4‑vCPU instance (very approximate). Always run a real load test in-region.

---

## How would you optimize if response times are too slow?

1. **Measure & profile:** break down time into preprocessing, inference, serialization.
2. **Model optimizations:** quantization, pruning, smaller model, ONNX conversion, TensorRT.
3. **Serving optimizations:** use TF‑Serving/ONNX Runtime or a compiled runtime, switch to gRPC.
4. **Hardware:** switch to GPU or larger CPU instances.
5. **Concurrency & batching:** tune concurrency, implement request batching where acceptable.
6. **Caching:** short TTL cache for identical requests.
7. **Warm instances:** increase `min-instances` to reduce cold starts.

---

## What metrics matter most for ML inference APIs?

* **Latency percentiles (p50/p95/p99)** — tail latency matters most.
* **Throughput (RPS)** and **error rate** (4xx/5xx).
* **CPU & memory usage**, instance counts, and cold-start rate.
* **Inference time vs preprocessing time** (breakdown).
* **Model metrics:** prediction/confidence distributions, input feature drift, label delay/error rate.
* **Business metrics:** cost per inference, SLA compliance.

---

## Why is Docker layer caching important for build speed? (Did you leverage it?)

* **Importance:** caching avoids reinstalling dependencies and rebuilding unchanged layers — dramatically speeds up iterative builds and CI.
* **How to leverage:** put stable steps (install dependencies) before copying frequently changed source files; keep `.dockerignore` small; use BuildKit or CI caching features.
* **Our repo:** the example Dockerfile installs requirements before copying the app — this allows the dependency layer to be cached.

---

## What security risks exist with running containers as root?

* **Higher impact on compromise:** container escape or exploit is more damaging with root privileges.
* **Potential host damage:** easier to modify mounted volumes or sensitive files.

**Mitigations:** run as a non-root user, drop capabilities, use read-only filesystem where possible, apply seccomp/AppArmor, and scan images.

---

## How does cloud auto-scaling affect your load test results?

* **Cold starts inflate tail latency** during scale-up.
* **Autoscaler reaction time** can cause transient errors/latency during short tests.
* **Test design:** run sustained stages long enough for autoscaler to stabilize and test from the same region to minimize network noise.

---

## What would happen with 10x more traffic?

* **If autoscaling and quotas allow:** more instances will be created; costs rise and latency may remain stable if the system scales horizontally.
* **If you hit limits:** requests will queue or be rate-limited, leading to `429`/`503` and increased tail latency.

**Plan:** increase `max-instances` or instance size, add caching, offload async work, and run targeted load tests to validate scaling behavior.

---

## How would you monitor performance in production?

* **Dashboards:** p50/p95/p99 latency, RPS, errors, CPU/memory, instance count.
* **Tracing:** OpenTelemetry to see time spent in each stage.
* **Logging:** structured logs with request\_id, inference\_ms, model\_version, and non-sensitive input hashes.
* **Model monitoring:** prediction distributions, confidence changes, and data drift alerts.
* **Synthetic tests & canaries:** automated smoke checks and canary traffic for each release.

---

## How would you implement blue-green deployment?

1. Deploy green revision alongside blue.
2. Run smoke/integration tests against green.
3. Gradually shift traffic (percentage-based) from blue to green while monitoring.
4. Roll back instantly by shifting traffic back to blue if problems appear.

*Cloud Run supports traffic splitting between revisions, making this straightforward.*

---

## What would you do if deployment fails in production?

* **Rollback traffic** to the last healthy revision immediately.
* **Alert on-call** and gather logs/traces for root-cause analysis.
* **Fix & re-deploy** after CI smoke tests.
* **Postmortem** and preventive actions (tests, guardrails).

---

## What happens if your container uses too much memory?

* The runtime will OOM‑kill the container; Cloud Run will restart it, creating `5xx` errors and potential downtime.

**Mitigations:** increase memory allocation, profile and reduce memory usage (lazy-loading, memory-mapped models), or split work across multiple processes.

---

