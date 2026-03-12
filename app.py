import json
import os
import shlex
import subprocess
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

JSON_DIR = Path(os.environ.get("ALLSKY_JSON_DIR", "/home/pi/allsky/config/overlay/extra"))
ALLSKY_HOME = Path(os.environ.get("ALLSKY_HOME", "/home/pi/allsky"))

DARK_CSS = (
    'body{background:#1a1a2e;color:#e0e0e0}'
    '.swagger-ui{background:#1a1a2e}'
    '.swagger-ui .topbar{background:#16213e}'
    '.swagger-ui .info .title,.swagger-ui .info li,.swagger-ui .info p,.swagger-ui .info table,'
    '.swagger-ui .info a{color:#e0e0e0}'
    '.swagger-ui .scheme-container{background:#16213e;box-shadow:none}'
    '.swagger-ui .opblock-tag{color:#e0e0e0;border-bottom-color:#2a2a4a}'
    '.swagger-ui .opblock .opblock-summary-description{color:#b0b0b0}'
    '.swagger-ui .opblock .opblock-section-header{background:#16213e}'
    '.swagger-ui .opblock .opblock-section-header h4{color:#e0e0e0}'
    '.swagger-ui table thead tr td,.swagger-ui table thead tr th{color:#e0e0e0;border-bottom-color:#2a2a4a}'
    '.swagger-ui .parameter__name,.swagger-ui .parameter__type{color:#e0e0e0}'
    '.swagger-ui .response-col_status{color:#e0e0e0}'
    '.swagger-ui .response-col_description{color:#b0b0b0}'
    '.swagger-ui .model-title{color:#e0e0e0}'
    '.swagger-ui .model{color:#e0e0e0}'
    '.swagger-ui section.models{border-color:#2a2a4a}'
    '.swagger-ui section.models h4{color:#e0e0e0}'
    '.swagger-ui .model-box{background:#16213e}'
    '.swagger-ui .prop-type{color:#7ec8e3}'
    '.swagger-ui select{background:#16213e;color:#e0e0e0;border-color:#2a2a4a}'
    '.swagger-ui input[type=text]{background:#16213e;color:#e0e0e0;border-color:#2a2a4a}'
    '.swagger-ui textarea{background:#16213e;color:#e0e0e0;border-color:#2a2a4a}'
    '.swagger-ui .btn{border-color:#2a2a4a;color:#e0e0e0}'
    '.swagger-ui .copy-to-clipboard{filter:invert(1)}'
    '.swagger-ui .microlight{background:#0f3460!important;color:#e0e0e0!important}'
)

app = FastAPI(
    title="AllSky Data API",
    version="1.0.0",
    docs_url=None,
    swagger_ui_parameters={"syntaxHighlight.theme": "monokai"},
)


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui():
    resp = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Docs",
        swagger_ui_parameters={"syntaxHighlight.theme": "monokai"},
    )
    body = resp.body.decode()
    body = body.replace("</head>", f"<style>{DARK_CSS}</style></head>")
    return HTMLResponse(body)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def read_json_file(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def list_json_files() -> list[str]:
    return sorted(p.stem for p in JSON_DIR.glob("*.json"))


def get_allsky_env() -> dict:
    """Sources the Allsky variables.sh script and captures ALLSKY_ variables."""
    env_vars = {}
    variables_sh = ALLSKY_HOME / "variables.sh"

    if variables_sh.is_file():
        # ALLSKY_HOME must be exported before sourcing variables.sh
        cmd = f"export ALLSKY_HOME={shlex.quote(str(ALLSKY_HOME))} && source {shlex.quote(str(variables_sh))} && env"
        try:
            proc = subprocess.Popen(
                ["bash", "-c", cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            for line in proc.stdout:
                line = line.decode(encoding='UTF-8').strip('\n').strip('\r')
                if "=" in line:
                    key, _, value = line.partition("=")
                    if key.startswith("ALLSKY_"):
                        env_vars[key] = value
            proc.communicate()
        except Exception as e:
            env_vars["error"] = f"Failed to load variables.sh: {str(e)}"
    else:
        env_vars["error"] = f"Variables file not found at {variables_sh}"

    return env_vars


@app.get("/")
def index():
    files = list_json_files()
    return {
        "endpoints": {
            "/": "This index",
            "/env": "AllSky core environment variables (AS_*)",
            "/all": "All JSON data combined",
            "/data/{name}": "Single data file",
        },
        "available": {name: f"/data/{name}" for name in files},
    }


@app.get("/files")
def files():
    return list_json_files()


@app.get("/env")
def env_data():
    """Returns the core AllSky AS_ environment variables."""
    return get_allsky_env()


@app.get("/all")
def all_data():
    result = {}
    for path in sorted(JSON_DIR.glob("*.json")):
        try:
            result[path.stem] = read_json_file(path)
        except (json.JSONDecodeError, OSError):
            result[path.stem] = {"error": "failed to read"}

    # Include the environment variables inside the "all" payload as well
    result["env"] = get_allsky_env()
    return result


@app.get("/data/{name}")
def get_data(name: str):
    path = JSON_DIR / f"{name}.json"
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"No data file named '{name}'")
    try:
        return read_json_file(path)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"'{name}.json' contains invalid JSON")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
