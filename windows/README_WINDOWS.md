# Windows-native setup

This project supports a Windows-only runtime without Docker Desktop.

## Required software

- PostgreSQL 16 installed locally
- Grafana installed locally or running as a Windows service
- Python virtual environment in the project

## Start services

From PowerShell:

```powershell
cd C:\Users\angel\Desktop\netpulse
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\windows\start-local-services.ps1
```

## Configure PostgreSQL

Create the database and user if they do not already exist:

```sql
CREATE DATABASE netpulse;
CREATE USER netpulse WITH PASSWORD 'netpulse';
GRANT ALL PRIVILEGES ON DATABASE netpulse TO netpulse;
```

Then run the schema file in the project:

```powershell
"C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d netpulse -f .\postgres\init\01_create_tables.sql
```

## Grafana

Use the Grafana Windows installer or service manager. The dashboard does not require any Grafana API key for local use.

Access the UI here:

- http://localhost:3000
- username: admin
- password: admin

## Run the Python automation

```powershell
cd C:\Users\angel\Desktop\netpulse
.\.venv\Scripts\python.exe scripts\run_pipeline.py
```
