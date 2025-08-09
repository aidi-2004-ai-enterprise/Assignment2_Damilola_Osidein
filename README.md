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

---

## Architecture (high level)

1. Client -> REST API (Cloud Run)
2. API validates input -> preprocessing -> model inference -> postprocessing
3. Results returned to client; logs emitted to stdout for Stackdriver/Cloud Logging

---

## Prerequisites

* Python 3.10+ (or the version your app requires)
* Docker (for local container build)
* Google Cloud SDK (`gcloud`) configured with your project and authenticated
* (Optional) Google Cloud Build and Artifact Registry access

---

## Setup (local development)

```bash
# create and activate virtualenv
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate     # Windows

# install
pip install -r requirements.txt

# set env vars (example)
export FLASK_APP=app.py
export MODEL_PATH=./models/model.joblib
export PORT=8080

# run locally
flask run --host=0.0.0.0 --port=${PORT}
# OR (FastAPI + uvicorn)
uvicorn app:app --host 0.0.0.0 --port ${PORT} --reload
```

---

## Environment variables (recommended)

* `MODEL_PATH` — local path or cloud storage path to model artifact
* `LOG_LEVEL` — INFO/DEBUG
* `PORT` — port to listen on (Cloud Run uses 8080 by default)
* `BATCH_SIZE` — optional inference batching
* `CACHE_ENABLED` — enable in-memory cache for identical requests

---

## API documentation

### 1) Health

```
GET /health
200 OK
{ "status": "ok" }
```

### 2) Predict

```
POST /predict
Content-Type: application/json

Request body (example):
{
  "make": "Toyota",
  "model": "Corolla",
  "year": 2018,
  "engine_displacement": 1.8,
  "fuel_type": "gasoline",
  "curb_weight_kg": 1250,
  "drivetrain": "FWD"
}

Response (200):
{
  "co2_g_per_km": 128.4,
  "confidence": 0.87,
  "model_version": "v2025-07-30",
  "input_hash": "..."
}

Error responses:
- 400 Bad Request — missing/invalid parameters
- 422 Unprocessable Entity — semantic errors in inputs
- 500 Internal Server Error — model or server error
```

---

## Logging & observability

* Log JSON lines to stdout with request\_id, input\_hash, model\_version, inference\_time\_ms, and status.
* Export metrics to Cloud Monitoring (e.g. custom metric for inference latency and error rate).

Example log line:

```json
{"ts":"2025-08-08T22:00:00Z","request_id":"abc123","model_version":"v2025-07-30","inference_ms":43,"input_hash":"...","status":"ok"}
```

---

## Tests

* Unit tests for preprocessing, postprocessing, and model wrapper (pytest)
* Integration tests: run the server in test mode and hit endpoints (use pytest + requests or httpx)

Example pytest run:

```bash
pytest tests/ -q
```

---

## Answers to provided questions

### Edge cases

1. **Missing fields** — return 400 with field-level messages. Provide a sample JSON of required fields in the error response.
2. **Invalid numeric ranges** — return 422. For example, year outside \[1900, current\_year+1] is invalid.
3. **Unknown categorical levels** — options:

   * Map unknown categories to an `__UNKNOWN__` token used during model training.
   * Return 422 if the domain requires strict validation.
4. **Extremely large batch sizes or long payloads** — enforce a payload size limit (e.g., 1 MB) and a max batch size env var. Return 413 Payload Too Large.
5. **Model file missing or corrupt at startup** — fail-fast with a clear startup log and nonzero exit code so platform can restart. Expose a rationale in logs.

### Load estimates (how I derived them)

Assumptions (example app using a lightweight scikit-learn model):

* Average inference time (single request): 40 ms CPU time
* Additional request overhead (HTTP + preprocessing): 60 ms
* Total p95 latency under light CPU: 100 ms

**RPS per instance at concurrency 1** = 1000 ms / 100 ms = **10 RPS**

Cloud Run supports concurrency >1. If you set `--concurrency=10`, an instance can handle \~100 RPS (idealized). Real-world numbers will be lower due to GC, bursts, CPU limits, and network.

**Recommended starting point**:

* Set container CPU = 1 vCPU, memory = 512Mi
* Concurrency = 10
* Set `min-instances=1` (or higher if latency-sensitive) and `max-instances` according to budget.

To estimate capacity: `Estimated_RPS = instances * concurrency * (1000 / median_latency_ms)`

Example: 5 instances \* concurrency 10 \* (1000 / 100 ms) = 500 RPS

Note: for heavy models (TF, PyTorch), inference latency may be 200–1000 ms — do the math using measured latencies.

### Security risks and mitigations

1. **Model poisoning / malicious input** — validate and sanitize inputs, apply rate limiting, and monitor for anomalous inputs.
2. **Sensitive data leakage (PII)** — avoid logging raw inputs; log only hashed input or a subset of non-sensitive fields.
3. **Unrestricted uploads** — if the API accepts file uploads, scan and validate file types and size, and store in secure buckets with limited access.
4. **Container image vulnerabilities** — use minimal base images (e.g., `python:slim` or distroless), run security scans (e.g., Container Analysis, Trivy) and pin dependencies.
5. **Excess privileges** — run with least privilege service account; use IAM roles scoped to only required APIs.
6. **Secrets in environment variables** — prefer Secret Manager and grant Cloud Run service account access to retrieve secrets at startup.
7. **Denial of service / high request volume** — configure Cloud Run concurrency and autoscaling, set max-instances, enable Cloud Armor in front of HTTPS Load Balancer if necessary.
8. **Insecure dependencies** — keep requirements up-to-date, use dependabot-like tooling and CI checks.

---

## Maintenance & retraining

* Track model drift via error rates and prediction distributions.
* Periodically retrain and version models; use a CI/CD pipeline to promote new model artifacts.
* Maintain a model registry with versions and rollbacks supported.

---

# DEPLOYMENT.md

## Containerization

### Example Dockerfile (Python app)

```dockerfile
FROM python:3.11-slim
WORKDIR /app

# system dependencies (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Create a non-root user
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

ENV PORT=8080
EXPOSE ${PORT}

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "app:app"]
```

Notes:

* Use `gunicorn` (or `uvicorn` + `gunicorn` for FastAPI) in production.
* Consider using distroless or slim images for smaller attack surface.

---

## Build & push (Artifact Registry) — recommended

```bash
# configure
gcloud config set project PROJECT_ID
gcloud auth configure-docker REGION-docker.pkg.dev

# build and push using docker
docker build -t REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/service-name:tag .
docker push REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/service-name:tag
```

Or using Cloud Build:

```bash
gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/service-name:tag
```

---

## Deploy to Cloud Run

```bash
gcloud run deploy SERVICE_NAME \
  --image REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/service-name:tag \
  --region REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --concurrency 10 \
  --min-instances 1 \
  --max-instances 50 \
  --set-env-vars MODEL_PATH=gs://my-bucket/models/model.joblib,LOG_LEVEL=INFO
```

To get the service URL after deployment:

```bash
gcloud run services describe SERVICE_NAME --platform managed --region REGION --format 'value(status.url)'
```

**Important**: replace `PROJECT_ID`, `REGION`, `REPOSITORY`, `SERVICE_NAME`, and `tag` with your values.

---

## CI/CD notes

* Trigger Cloud Build on merges to `main`. Cloud Build will build, run tests, push image, and deploy to Cloud Run (or create a manual promotion step).
* Use separate projects for staging and prod.

---

## Commands used (example session)

1. `gcloud auth login`
2. `gcloud config set project my-project`
3. `gcloud builds submit --tag REGION-docker.pkg.dev/my-project/my-repo/co2-service:v1`
4. `gcloud run deploy co2-service --image REGION-docker.pkg.dev/my-project/my-repo/co2-service:v1 --region us-central1 --platform managed --allow-unauthenticated --memory 512Mi --concurrency 10 --min-instances 1`
5. \`gcloud run services describe co2-service --platform managed --region us-central1 --format 'value(status.url)'

---

## Issues encountered & solutions (common)

1. **App not starting: port mismatch**

   * *Problem*: Container listens on a port other than \$PORT. Cloud Run expects the container to listen on the configured \$PORT.
   * *Solution*: Read `PORT` env var (or default 8080) and bind server to that port.

2. **Model artifact missing in container**

   * *Problem*: Model path points to local path not available in container.
   * *Solution*: Upload model to Cloud Storage and set `MODEL_PATH=gs://...`; grant service account `roles/storage.objectViewer`.

3. **Permission denied when pushing image**

   * *Problem*: No Artifact Registry permissions
   * *Solution*: Enable Artifact Registry API and grant `roles/artifactregistry.writer` to the CI/service account.

4. **Cold starts hurting latency**

   * *Problem*: Cold starts for infrequent traffic
   * *Solution*: Set `min-instances` > 0; consider keeping at least 1 warm instance or use Cloud Run for Anthos (different pricing) or move to GKE with custom autoscaler.

5. **Container crashes with OOM**

   * *Problem*: Model loading uses more memory than allocated.
   * *Solution*: Increase `--memory` or load a lighter model; use lazy-loading or model quantization.

6. **Health checks failing / readiness**

   * *Problem*: Platform thinks container unhealthy due to slow startup
   * *Solution*: Provide a `/health` endpoint that returns quickly and configure readiness probe (if using other platforms) or increase start-up timeout when possible.

---

# Final Cloud Run URL

Replace the placeholder below with the actual URL returned by the `gcloud run services describe` command after deploying.

**Final Cloud Run URL:** `https://REPLACE_WITH_YOUR_SERVICE-<random>.run.app`

To retrieve it programmatically:

```bash
gcloud run services describe SERVICE_NAME --platform managed --region REGION --format 'value(status.url)'
```

---

# LOAD\_TEST\_REPORT.md

## Objective

Validate service performance and scalability for expected load, identify bottlenecks, and recommend configuration changes.

## Test environment

* Cloud Run service: `co2-service` (configured memory=512Mi, cpu=1, concurrency=10, min=1, max=50)
* Region: `us-central1`
* Model: scikit-learn RandomForest (single-threaded inference)
* Test harness: `k6` (script attached below)

---

## Test plan & k6 script (example)

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 50 },  // ramp to 50 VUs
    { duration: '3m', target: 50 },  // stay at 50 VUs
    { duration: '1m', target: 200 }, // ramp to 200 VUs
    { duration: '3m', target: 200 }, // stay at 200 VUs
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    'http_req_duration{type:predict}': ['p(95) < 500'],
  }
};

const payload = JSON.stringify({
  make: 'Honda',
  model: 'Civic',
  year: 2015,
  engine_displaceme
```
