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

What happens if your model file becomes corrupted?

What's a realistic load for a penguin classification service?

How would you optimize if response times are too slow?

What metrics matter most for ML inference APIs?

Why is Docker layer caching important for build speed? (Did you leverage it?)

What security risks exist with running containers as root?

How does cloud auto-scaling affect your load test results?

What would happen with 10x more traffic?

How would you monitor performance in production?

How would you implement blue-green deployment?

What would you do if deployment fails in production?

What happens if your container uses too much memory?
