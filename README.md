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
- `netpulse-stack.yml` - Kubernetes deployment for Minikube / cluster runtime
- `docker-compose.yml` - runs PostgreSQL and Grafana locally

## Runtime modes

This project supports four execution paths:

1. Kubernetes / Minikube (current default stack)
2. Docker compose (Linux / VM reference)
3. Windows native services (no Docker Desktop needed)
4. VM-hosted services (PostgreSQL + Grafana running on a Linux VM)

### Option 1: Kubernetes / Minikube (recommended)

This project now ships a Kubernetes deployment manifest at [netpulse-stack.yml](netpulse-stack.yml). It replaces the broken local host-directory mounts with Kubernetes `ConfigMap` objects so Grafana can find its datasource and dashboard definitions inside the cluster.

Start the stack in Minikube:

```bash
minikube start
kubectl apply -f netpulse-stack.yml
kubectl get pods
kubectl get svc
kubectl rollout status deployment/netpulse-postgres --timeout=180s
kubectl rollout status deployment/netpulse-grafana --timeout=180s
kubectl rollout status deployment/netpulse-backend --timeout=180s
kubectl rollout status deployment/netpulse-frontend --timeout=180s
```

Open the exposed services:

```bash
minikube service grafana
minikube service frontend
```

Useful Kubernetes checks:

```bash
kubectl describe deployment netpulse-grafana
kubectl get configmap
kubectl get secret
kubectl logs deployment/netpulse-grafana
kubectl logs deployment/netpulse-backend
```

If you want to reload configuration after a manifest change:

```bash
kubectl apply -f netpulse-stack.yml
kubectl rollout restart deployment/netpulse-grafana
kubectl rollout restart deployment/netpulse-backend
```

The Grafana files are mounted from ConfigMaps at:

- `/etc/grafana/provisioning/datasources`
- `/etc/grafana/provisioning/dashboards`
- `/var/lib/grafana/dashboards`

This keeps the provisioning files portable across Kubernetes nodes and avoids the Docker Compose host-path issue that breaks in Minikube.

### Option 2: Docker compose (reference setup)

```bash
cp .env.example .env
docker compose up -d
python -m pip install -r requirements.txt
python backend/scripts/run_pipeline.py
```

### Option 3: Windows native services

Use the PowerShell entry point in the project root:

```powershell
.\start_windows.ps1
```

This starts or verifies PostgreSQL and Grafana as Windows services without requiring Docker Desktop.

Detailed instructions are in [windows/README_WINDOWS.md](windows/README_WINDOWS.md).

### Option 4: VM-based services

Use the VM instructions in [vm/README_VM.md](vm/README_VM.md).

For VM environments, set the connection values in `.env` to the VM IP address instead of `localhost`.

## Common requirements

- PostgreSQL 16 or compatible database service
- Grafana available locally, in a VM, or in Kubernetes
- Kubernetes / Minikube for the manifest-based deployment
- No Grafana API key required for local dashboard usage

## Run the Python automation

```powershell
.\.venv\Scripts\python.exe backend\scripts\run_pipeline.py
```

## Open Grafana

If you are running the Kubernetes stack:

- use `minikube service grafana`
- or open the NodePort URL printed by Minikube
- default login: `admin` / `admin`

If you are running Docker or a local service:

- URL: http://localhost:3000
- Username: `admin`
- Password: `admin`

To confirm the dashboard is being provisioned correctly in Kubernetes:

```bash
kubectl exec -it deploy/netpulse-grafana -- ls -R /etc/grafana/provisioning /var/lib/grafana/dashboards
```

You should see the `dashboard.yaml`, datasource config, and the dashboard JSON file inside the Grafana container.

## Open Streamlit AI UI

If the Grafana narrative panels are hard to read, use the dedicated Streamlit frontend.

For Kubernetes / Minikube:

```bash
minikube service frontend
```

For local Python runs:

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
