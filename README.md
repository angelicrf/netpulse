# NetPulse AI Network Monitoring Project

This project demonstrates a small Python monitoring stack that follows the workflow below:

Grafana / PostgreSQL -> Anomaly detected -> AI Agent -> root-cause analysis

## Architecture

- PostgreSQL stores latency, packet loss, and POP status history
- Grafana visualizes the data with a free dashboard
- A Python automation script simulates metric collection and anomaly detection
- An AI agent reviews the telemetry and highlights likely root causes

## Project structure

- `backend/src/` - Python backend application code
- `backend/scripts/` - backend execution helpers
- `requirements.txt` - Python dependencies
- `postgres/` - database initialization SQL
- `grafana/` - Grafana provisioning and dashboard configuration
- `frontend/` - Streamlit web UI for AI narrative
- `docker-compose.yml` - runs PostgreSQL and Grafana locally

## Runtime modes

This project supports three execution paths:

1. Docker compose (Linux / VM reference)
2. Windows native services (no Docker Desktop needed)
3. VM-hosted services (PostgreSQL + Grafana running on a Linux VM)

### Option 1: Docker compose (reference setup)

```bash
cp .env.example .env
docker compose up -d
python -m pip install -r requirements.txt
python backend/scripts/run_pipeline.py
```

### Option 2: Windows native services

Use the PowerShell entry point in the project root:

```powershell
.\start_windows.ps1
```

This starts or verifies PostgreSQL and Grafana as Windows services without requiring Docker Desktop.

Detailed instructions are in [windows/README_WINDOWS.md](windows/README_WINDOWS.md).

### Option 3: VM-based services

Use the VM instructions in [vm/README_VM.md](vm/README_VM.md).

For VM environments, set the connection values in `.env` to the VM IP address instead of `localhost`.

## Common requirements

- PostgreSQL 16 or compatible database service
- Grafana installed locally or in a VM
- No Grafana API key required for local dashboard usage

## Run the Python automation

```powershell
.\.venv\Scripts\python.exe backend\scripts\run_pipeline.py
```

## Open Grafana

- URL: http://localhost:3000
- Username: `admin`
- Password: `admin`

## Open Streamlit AI UI

If the Grafana narrative panels are hard to read, use the dedicated Streamlit frontend:

```bash
/home/angelique/Desktop/netpulse/.venv/bin/python -m pip install -r requirements.txt
/home/angelique/Desktop/netpulse/.venv/bin/python -m streamlit run frontend/streamlit_app.py
```

Then open:

- URL: http://localhost:8501

This page shows the latest OpenAI summary, prediction, and workaround in large readable sections.

## Dockerfiles for backend and frontend

You do not need Dockerfiles to run the current default stack (PostgreSQL + Grafana + local Python).
They are only needed if you want backend and frontend to run as containers too.

Available Dockerfiles:

- [backend/Dockerfile](backend/Dockerfile)
- [frontend/Dockerfile](frontend/Dockerfile)

Run infra only (default):

```bash
docker compose up -d
```

Run infra + app containers (optional profile):

```bash
docker compose --profile apps up -d --build
```

Notes:

- backend-runner executes [backend/scripts/run_pipeline.py](backend/scripts/run_pipeline.py).
- frontend-ui serves Streamlit at http://localhost:8501.

## Example AI finding

The agent is designed to identify issues like:

> Nairobi latency increased 180% during the last 10 minutes.

This is aligned with the workflow in your diagram.
