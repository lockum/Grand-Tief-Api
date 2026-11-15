# Operational Instructions for AI Agents

Follow these directives when modifying, extending, or maintaining this codebase:

---

## 1. Environment & Execution
- **Virtual Environment**: Located at `.venv/`. Run commands using `./.venv/bin/<command>` or activate with `source .venv/bin/activate`.
- **Database**: Local SQLite database resides at `./gta_news.db`. In tests, it uses `./test_gta_news.db` and is cleaned up automatically.
- **Dependencies**: Managed via `requirements.txt`. Do not introduce large, unnecessary frameworks. Keep the service lightweight and fast.

---

## 2. Code Modifications Checklist
Whenever adding or updating an endpoint or service:

1. **Schema First**: Define or update Pydantic models in `app/models/schemas.py`.
2. **Async Everywhere**: Every database query, network call, and background job must be fully asynchronous (`async` / `await`).
3. **Database Access**: Always use the async context manager:
   ```python
   async with get_db() as conn:
       cursor = await conn.execute("...")
       rows = await cursor.fetchall()
   ```
4. **Security Boundaries**:
   - Query endpoints (`GET /api/v1/...`): protect with `dependencies=[Depends(require_readonly_user)]`.
   - Mutation / Management endpoints (`POST /api/v1/...`): protect with `dependencies=[Depends(require_admin_user)]`.
5. **No Verbatim Copyrighted Transcriptions**: Never hardcode long proprietary synopses or marketing blurbs into source code or test fixtures.
6. **Timezone Handling**: Always use `datetime.now(timezone.utc)` for UTC timestamps; never use deprecated `datetime.utcnow()`.

---

## 3. Verification & Testing
Before finishing any task, run the test suite:
```bash
./.venv/bin/pytest tests/
```
All tests must pass with 0 errors and 0 unhandled warnings.
