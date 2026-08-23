# Server Side Backend

Python backend template using FastAPI with a clean folder structure.

## Run

```bash
cd server_side
python -m pip install -r requirements.txt
uvicorn server_side.main:app --app-dir src --reload
```

Open http://127.0.0.1:8000/docs for API docs.

## Structure

- `src/server_side/api/routes`: API route modules
- `src/server_side/core`: app settings and shared config
- `src/server_side/services`: business rules
- `src/server_side/repositories`: data access layer
- `src/server_side/models`: domain/data models
- `src/server_side/schemas`: request/response schemas
- `tests/unit`: unit tests
- `tests/integration`: integration tests
