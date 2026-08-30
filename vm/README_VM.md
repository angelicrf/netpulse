# VM-based setup

This is the secondary path if you do not want to run Docker on Windows.

## Option A: run the stack inside a Linux VM

1. Create a Linux VM with Ubuntu or Debian.
2. Install PostgreSQL and Grafana in the VM.
3. Keep the same project structure and point the environment file to the VM IP address.
4. Use a database and Grafana UI exposed on the VM network.

Example `.env` for VM:

```env
POSTGRES_HOST=10.0.2.15
POSTGRES_PORT=5432
POSTGRES_DB=netpulse
POSTGRES_USER=netpulse
POSTGRES_PASSWORD=netpulse

GRAFANA_URL=http://10.0.2.15:3000
GRAFANA_USER=admin
GRAFANA_PASSWORD=admin
```

## Option B: run Docker only on the VM

The compose file remains a Linux/VM reference, but Windows does not need it.

```bash
cd /path/to/netpulse
docker compose up -d
python backend/scripts/run_pipeline.py
```

## No Grafana API key required

For local or VM-based usage, the dashboard is configured with the default admin credentials and no API token is needed.
