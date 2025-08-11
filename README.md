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

# Production & Deployment Q&A — Penguin Classification Service

Below are concise, actionable answers based on the `Assignment2_Damilola_Osidein` repository.

---

## What edge cases might break your model in production that aren't in your training data?
- Distribution / concept drift (new penguin types or features)
- Unseen categorical values
- Unit/format mismatches (e.g., cc vs L, kg vs lb)
- Missing/null/malformed fields
- Adversarial or extreme out-of-range inputs
- Time-dependent mismatches

**Mitigations:** schema validation (pydantic/JSON Schema), map unknowns to a sentinel (e.g., `__UNKNOWN__`), unit normalization, input size/rate limits, drift monitoring, scheduled retraining, and logging samples for labeling.

## What happens if your model file becomes corrupted?
Fail fast at startup with a non-zero exit so the orchestrator notices. If loading at runtime, return HTTP `503` and log the error.

**Prevent/mitigate:** checksums (SHA256), a versioned model registry, a fallback model, CI smoke tests on artifacts, and automated rollback if model-load errors spike.

## What's a realistic load for a penguin classification service?
- Demo/internal testing: **0.1–5 RPS**  
- Moderate mobile/web clients: **10–200 RPS**  
- Public high-traffic service: **1k+ RPS** (image models typically need GPU/optimized infra)

Measure actual throughput per instance (e.g., RPS per vCPU) and run in-region load tests to get realistic numbers.

## How would you optimize if response times are too slow?
1. Profile to locate hotspots (preprocessing vs inference vs serialization).  
2. Options: quantize/prune or use a smaller model, convert to ONNX/TensorRT, serve with optimized runtimes (ONNX Runtime / TF-Serving), enable batching, increase instance size or GPUs, add caching, and tune concurrency and warm instances (`min-instances`).

## What metrics matter most for ML inference APIs?
- Tail latencies (p50 / p95 / p99)  
- Throughput (RPS)  
- Error rates (4xx / 5xx / 429)  
- CPU & memory usage  
- Cold-start rate  
- Time breakdown (preprocessing vs inference)  
- Model outputs / confidence distributions  
- Business metrics (cost per inference, SLA compliance)

## Why is Docker layer caching important for build speed? (Did you leverage it?)
Docker layer caching avoids re-installing dependencies and rebuilding unchanged layers. To maximize cache hits, place stable steps (install dependencies) before copying frequently changing source files. The repository’s Dockerfile orders installs before copying app code to leverage caching; CI should use BuildKit or cache mounts for faster builds.

## What security risks exist with running containers as root?
If an attacker escapes the container, running as root makes host compromise and manipulation of mounted volumes easier.

**Mitigations:** run as a non-root user, drop Linux capabilities, use read-only filesystem mounts, apply seccomp/AppArmor profiles, scan images, and enforce least-privilege IAM.

## How does cloud auto-scaling affect your load test results?
Autoscaling introduces cold starts (inflates tail latency) and autoscaler reaction time can cause transient errors or latency during ramp-up. Ensure load tests are long enough for the autoscaler to react and stabilize; run tests from in-region clients to reduce network variance.

## What would happen with 10x more traffic?
- If autoscaling and quotas permit: horizontal scaling will increase instance count and costs; latency can remain stable.  
- If limits are reached: queuing, `429` / `503` responses, increased tail latency, and possible throttling.

**Plan:** raise quotas, scale instance size, add caching, or offload async tasks.

## How would you monitor performance in production?
- Dashboards for p50/p95/p99 latency, RPS, error rates, CPU/memory, and instance count.  
- Distributed tracing (OpenTelemetry) to break down time by stage.  
- Structured logs with `request_id` and `inference_ms`.  
- Model monitoring for prediction/confidence drift.  
- Synthetic canaries and health checks.

## How would you implement blue-green deployment?
1. Deploy the new revision (green) alongside current (blue).  
2. Run smoke and integration tests on green.  
3. Shift traffic gradually (percent-based splits) while monitoring.  
4. If issues appear, revert traffic instantly to blue.

Many cloud platforms support revision traffic-splitting to simplify this.

## What would you do if deployment fails in production?
- Immediately roll traffic back to the last healthy revision and alert on-call.  
- Collect logs and traces for root cause analysis, fix the issue, and redeploy after passing CI smoke tests.  
- Run a postmortem and add guardrails to prevent recurrence.

## What happens if your container uses too much memory?
The platform will OOM-kill the container, causing restarts and 5xx errors.

**Mitigations:** increase memory allocation, profile and reduce memory usage (lazy-load or memory-map models), split workloads across processes, or scale horizontally to reduce per-instance memory pressure.
