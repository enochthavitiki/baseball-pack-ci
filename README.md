# Baseball Pack CI

A containerized **baseball domain pack** with a **synthetic stand-in decision component**, built and tested automatically by a GitHub Actions pipeline.

This is a personal learning project modeled on my capstone's architecture. It contains **no sponsor code**: the real decision core is protected and unavailable, so every outcome here is scripted and labeled `SYNTHETIC`, and anything that would need the real core returns `BLOCKED` instead of a guess.

## What the pipeline does

On every push and pull request to `main`:

1. **Unit tests** (`pytest`): decision rules, input validation, BLOCKED handling, deterministic receipts.
2. **Synthetic-label gate** (`scripts/check_synthetic.py`): runs every scenario in `fixtures/scenarios.json` and fails the build if any outcome is missing its synthetic label.
3. **Docker build + smoke test**: builds the image, starts the container, waits for `/health`, then calls `/decide` and checks the response.

The Docker job only runs if the test job passes.

## Run it locally

```bash
pip install -r requirements-dev.txt
pytest -v
python scripts/check_synthetic.py

docker build -t baseball-pack .
docker run --rm -p 8080:8080 baseball-pack
curl localhost:8080/health
curl -X POST localhost:8080/decide -H "Content-Type: application/json" \
  -d '{"inning": 8, "outs": 0, "runners": ["first"], "score_diff": -1}'
```

## API

| Method | Path | Body | Returns |
|---|---|---|---|
| GET | `/health` | none | `{"status": "ok", ...}` |
| POST | `/decide` | `inning`, `outs` (0–2), `runners` (list of first/second/third), `score_diff`; optional `"mode": "live"` | recommendation + rationale + receipt, or `BLOCKED` |
