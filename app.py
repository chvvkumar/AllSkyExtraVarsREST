import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

JSON_DIR = Path(os.environ.get("ALLSKY_JSON_DIR", "/home/pi/allsky/config/overlay/extra"))

app = FastAPI(title="AllSky Data API", version="1.0.0")

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


@app.get("/")
def index():
    files = list_json_files()
    return {
        "endpoints": {
            "/": "This index",
            "/all": "All data combined",
            "/data/{name}": "Single data file",
        },
        "available": {name: f"/data/{name}" for name in files},
    }


@app.get("/files")
def files():
    return list_json_files()


@app.get("/all")
def all_data():
    result = {}
    for path in sorted(JSON_DIR.glob("*.json")):
        try:
            result[path.stem] = read_json_file(path)
        except (json.JSONDecodeError, OSError):
            result[path.stem] = {"error": "failed to read"}
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
