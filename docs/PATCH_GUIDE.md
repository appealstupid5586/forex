# PATCH GUIDE

## 1. Cài đặt

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp ../.env.example .env
```

## 2. Chạy backend

```bash
PYTHONPATH=. uvicorn app.main:app --reload --port 8000
```

Hoặc:

```bash
../scripts/run_dev.sh
```

## 3. Mở dashboard tĩnh

Mở file:

```text
frontend/index.html
```

## 4. Test nhanh

```bash
PYTHONPATH=backend pytest tests
```

## 5. API chính

- `POST /api/v1/robot/start`
- `POST /api/v1/fsm/tick`
- `POST /api/v1/robot/freeze`
- `GET /api/v1/dashboard/hedge-os`
- `POST /api/v1/backtest/run`
- `GET /api/v1/genes/winners`
