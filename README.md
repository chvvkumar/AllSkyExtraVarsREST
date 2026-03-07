# AllSky Extra Vars REST API

A lightweight REST API that serves AllSky overlay extra variable JSON files over HTTP using FastAPI.

## Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Index with available endpoints and data files |
| `GET /files` | List all available data file names |
| `GET /all` | All data files combined into one response |
| `GET /data/{name}` | Get a single data file by name |
| `GET /docs` | Swagger UI documentation |

## Installation

Clone the repo and run the install script:

```bash
git clone https://github.com/chvvkumar/AllSkyExtraVarsREST.git
cd AllSkyExtraVarsREST
bash install.sh
```

The install script will:
- Pull the latest changes
- Create a Python virtual environment
- Install dependencies (`fastapi`, `uvicorn`)
- Install and start a systemd service on port 8080

## Configuration

The API reads JSON files from the directory set by the `ALLSKY_JSON_DIR` environment variable. Defaults to `/home/pi/allsky/config/overlay/extra`.

This can be changed in the systemd service file at `/etc/systemd/system/allsky-api.service`.

## Manual Usage

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

The API will be available at `http://localhost:8080`.
