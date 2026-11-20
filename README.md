# verification-llama

AI-assisted trust and safety telemetry triage and policy compiler.

## Overview

`verification-llama` is a system for processing client session telemetry, extracting anomaly signals, and generating structured risk triage decisions. It includes tools to:

1. Simulate multi-signal passive telemetry payloads and filter out baseline noise into concise feature deltas.
2. Format synthetic training datasets into instruction chat prompts for model fine-tuning.
3. Expose a FastAPI service that validates inputs and returns structured triage hypotheses and policy condition graphs.

## Components

- **`telemetry_generator.py`**: Generates synthetic session signals representing different user and threat profiles (e.g. Sybil accounts, automated bots, account takeover signals, and privacy-oriented users). Extracts relevant anomaly deltas from raw payloads.
- **`prepare_dataset_and_train.py`**: Builds structured examples for triage evaluation and natural language rule compilation, formatting them into chat template prompts.
- **`inference_server.py`**: Provides HTTP endpoints (`/api/v1/triage` and `/api/v1/compile-rule`) using Pydantic models for response schema validation.
- **`requirements.txt`**: Project dependencies including FastAPI, Uvicorn, Pydantic, PyTorch, and Datasets.

## Getting Started

### Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running Telemetry Simulation

```bash
python telemetry_generator.py
```

### Preparing Training Data

```bash
python prepare_dataset_and_train.py
```

### Starting the Inference API

```bash
python inference_server.py
```

The API runs locally at `http://127.0.0.1:8000`.

## API Endpoints

- `POST /api/v1/triage`: Evaluates a compressed feature delta and returns a structured fraud hypothesis, recommended action, and confidence score.
- `POST /api/v1/compile-rule`: Converts plain-text policy statements into structured condition graphs.
