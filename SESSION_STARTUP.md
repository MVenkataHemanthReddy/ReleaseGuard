# Session Startup Instructions

## ⚠️ REQUIRED: Load Context at Session Start

**Every new session must begin by reading `CHAT_CONTEXT.md`**

```bash
# At session start, run:
cat CHAT_CONTEXT.md
```

## Quick Start Commands
```powershell
cd "D:\Release Guard"
.venv\Scripts\Activate.ps1
python manage.py runserver 127.0.0.1:8000
# Terminal 2:
python manage.py runworker --interval 5
```

## Key Verification
```bash
# Verify tests pass
pytest apps/ -q

# Test API
curl http://127.0.0.1:8000/api/v1/
curl http://127.0.0.1:8000/api/v1/health/
```

## Key Paths
- **Main project**: `D:\Release Guard`
- **ShopAPI demo**: `D:\Release Guard\shopapi_project` (run tests from original location due to path issues)
- **Virtual env**: `D:\Release Guard\.venv`

## Test Commands
```bash
# ReleaseGuard tests (97 tests)
pytest apps/ -q

# ShopAPI tests (run from original location due to path issues)
cd C:\Users\mitta\OneDrive\Documents\Default Project\shopapi_project
.venv\Scripts\python.exe -m pytest shop/tests/ -q
```

## Key Files to Remember
- `CHAT_CONTEXT.md` - Full project context (read at session start)
- `README.md` - Full documentation
- `docs/DECISIONS.md` - Architecture Decision Records
- `docs/LEARNING_NOTES.md` - Concepts learned
- `docs/ARCHITECTURE.md` - System architecture
- `pytest.ini` - Test configuration