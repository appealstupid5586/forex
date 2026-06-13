Portfolio API examples

Demo để gọi endpoint `/api/v1/portfolio/analyze`:

1. Chạy server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Gửi request (shell script có sẵn):

```bash
bash backend/app/api/examples/portfolio_demo.sh
```

Script dùng `backend/app/skills/portfolio_analysis/examples/healthy_portfolio.json` làm payload.
