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

# README — Production Questions

This README answers common production questions for the ML inference service (concise, actionable, and ready to include in your repository).

---

What edge cases might break your model in production that aren't in your training data?

Distribution / concept drift (new vehicle/penguin types or features), unseen categorical values (new makes/species), unit/format mismatches (cc vs L, kg vs lb), missing/null/malformed fields, adversarial or extreme out-of-range inputs, and time-dependent mismatches.

Mitigations: schema validation (pydantic/JSON Schema), map unknowns to a sentinel (__UNKNOWN__), unit normalization, input size/rate limits, drift monitoring and scheduled retraining, and logging of samples for labeling. 
GitHub

What happens if your model file becomes corrupted?

Best practice: fail fast at startup (non-zero exit so orchestrator notices). If loading at runtime, return 503 and log the error. Prevent/mitigate with checksums (SHA256), a versioned model registry, a fallback model, CI smoke tests on artifacts, and automated rollback if model-load errors spike. 
GitHub

What's a realistic load for a penguin classification service?

Range depends on use: demo 0.1–5 RPS, moderate mobile use 10–200 RPS, public high-traffic 1k+ RPS (image models need GPU/optimized infra). Example cpu throughput: ~6 RPS per vCPU for a 150 ms inference; measure with a real in-region load test. (See repo locustfile for tests.) 
GitHub
+1

How would you optimize if response times are too slow?

Measure & profile (preprocessing vs inference vs serialization). Then: quantize/prune or use a smaller model, convert to ONNX/TensorRT, serve with an optimized runtime (ONNX Runtime / TF-Serving), enable batching, increase instance size or GPUs, add caching, tune concurrency and warm instances (min-instances). 
GitHub

What metrics matter most for ML inference APIs?

Tail latencies (p50/p95/p99), throughput (RPS), error rates (4xx/5xx/429), CPU & memory, cold-start rate, breakdown of inference vs preprocessing time, model outputs/confidence distributions, and business metrics (cost per inference & SLA compliance). 
GitHub

Why is Docker layer caching important for build speed? (Did you leverage it?)

Caching avoids re-installing dependencies and rebuilding unchanged layers; place stable steps (install deps) before copying frequently changing sources to maximize cache hits. The repo’s Dockerfile orders installs before copying app code to leverage that cache. Use BuildKit/CI cache for faster CI. 
GitHub
+1

What security risks exist with running containers as root?

If an attacker escapes the container, running as root makes host compromise and manipulation of mounted volumes easier. Mitigations: run as non-root user, drop Linux capabilities, use read-only filesystem mounts, apply seccomp/AppArmor, image scanning, and least-privilege IAM. 
GitHub

How does cloud auto-scaling affect your load test results?

Autoscaling introduces cold starts (inflates tail latency) and autoscaler reaction time can cause transient errors or latency during ramping. Make load tests long enough for the autoscaler to stabilize and test from the same region to reduce noise. 
GitHub

What would happen with 10x more traffic?

If autoscaling and quotas permit: horizontally scale out, cost increases, latency can stay stable. If you hit limits/quotas: queuing, 429/503, and increased tail latency. Plan to increase max-instances or instance size, add caching, and offload async tasks. 
GitHub

How would you monitor performance in production?

Dashboards for p50/p95/p99 latency, RPS, error rates, CPU/memory, instance count; distributed tracing (OpenTelemetry) for stage breakdown; structured logs with request_id, inference_ms, model_version; model monitoring for prediction/confidence drift; and synthetic canaries/smoke checks. 
GitHub

How would you implement blue-green deployment?

Deploy new revision (green) alongside current (blue), run smoke tests on green, gradually shift traffic (percent splits) while monitoring, and instantly flip traffic back if issues arise. Cloud Run supports revision traffic splitting which makes this straightforward. 
GitHub

What would you do if deployment fails in production?

Immediately roll traffic back to the last healthy revision, alert on-call, collect logs/traces for root cause, fix and redeploy after CI smoke tests, then run a postmortem and add preventive guardrails. 
GitHub

What happens if your container uses too much memory?

Platform will OOM-kill the container; it will restart (causing 5xx errors and downtime). Mitigations: increase memory allocation, profile and reduce memory (lazy-load, memory-map models), split workload across processes, or scale horizontally. 
GitHub
