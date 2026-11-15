# AI Agent Conventions & Coding Standards

## 1. Python & Typing
- Python 3.10+ syntax.
- All function signatures must have type annotations (arguments and return types).
- Use Pydantic v2 schemas for all API inputs and outputs.
- Dates should be handled using timezone-aware datetimes (`datetime.now(timezone.utc)`), never deprecated `datetime.utcnow()`.

## 2. Asynchronous Programming
- All I/O operations (HTTP calls, DB queries) must use `async/await`.
- Use `httpx.AsyncClient` for external HTTP requests.
- Use `async with get_db() as conn:` for SQLite operations.
- Avoid blocking calls (`time.sleep()`, synchronous `requests`, synchronous file read in hot paths).

## 3. FastAPI Route Design
- Route functions that call other route functions or share logic must use clean default arguments:
  ```python
  # Preferred:
  page: int = Query(default=1, ge=1)
  ```
- Always return standard Pydantic models for responses (`response_model=...`).
- Mount routes under `/api/v1` prefix.

## 4. Error Handling
- Never silence exceptions silently without logging (`logger.error(..., exc_info=True)`).
- Return HTTP 404 with standard `{"detail": "..."}` for missing resources.
- Return HTTP 500 through the global exception handler in `app/main.py`.

## 5. Verification
- Before finishing any turn or committing, run the test suite:
  ```bash
  ./.venv/bin/pytest tests/
  ```
- Ensure 0 failed tests and 0 unhandled warnings.

