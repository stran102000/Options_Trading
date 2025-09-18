# Web Frontend & API Guide

This document complements the root `README.md` by focusing specifically on the integrated Flask API + HTML/JS frontend for the Options Trading Analysis Tool.

## Overview
The system provides a browser interface to analyze equity options. Core logic (pricing, signal generation, VaR) lives in `backend/analysis.py`. The server (`api_server.py`) exposes a JSON API consumed by the frontend (`frontend/`).

```
User Browser ──HTTP──> Flask (`api_server.py`) ──> Analysis Layer (`backend/analysis.py`) ──> yfinance API
                           │
                           └── Serves static files (HTML/CSS/JS)
```

## Key Components
| Path | Purpose |
|------|---------|
| `api_server.py` | Flask app; serves UI + `/api/analyze` endpoint |
| `backend/analysis.py` | Expiration selection, SMA, signals, QMC pricing, VaR, trade advice |
| `frontend/index.html` | Single-page UI markup |
| `frontend/styles.css` | UI styling |
| `frontend/app.js` | Fetch logic, DOM rendering, Chart.js usage |

## Endpoint Spec
### POST `/api/analyze`
Request Body (JSON):
```json
{
  "tickers": "AAPL,MSFT,TSLA",  // string (comma separated) or list
  "expiration": "2025-01-17"     // optional; blank/omitted = auto-select
}
```
Response:
```json
{
  "results": [
    {
      "ticker": "AAPL",
      "expiration": "2025-01-17",
      "underlying_price": 195.32,
      "calls": [
        {"strike": 195, "lastPrice": 4.1, "SMA": 4.2, "Signal": false, "mc_price": 4.35, "var": 0.88, "advice": "Not recommended: Call not significantly undervalued."}
      ],
      "puts": [
        {"strike": 195, "lastPrice": 3.9, "SMA": 3.8, "Signal": true, "mc_price": 3.70, "var": 0.75, "advice": "Good trade: Put appears undervalued."}
      ]
    }
  ]
}
```

## Data Fields
| Field | Meaning |
|-------|---------|
| `strike` | Option strike price |
| `lastPrice` | Latest traded option price from yfinance chain |
| `SMA` | Simple Moving Average (window=5) of `lastPrice` (in-chain ordering) |
| `Signal` | For calls: `lastPrice > SMA`; for puts: `lastPrice < SMA` |
| `mc_price` | Quasi Monte Carlo (Sobol) discounted expected payoff |
| `var` | 95% Value-at-Risk (5th percentile of discounted payoff) |
| `advice` | Heuristic undervaluation suggestion |

## Pricing Methodology
- Uses risk-neutral simulation: \( S_T = S_0 e^{(r - \frac{1}{2}\sigma^2)T + \sigma \sqrt{T} Z} \)
- Sobol low-discrepancy sequence (dimension 1) for variance reduction.
- 2^14 samples by default (16,384 paths) for a balance of speed and stability.
- VaR = 5th percentile of discounted payoff distribution.

## Heuristic Trade Evaluation
```
if (mc_price - market_price)/market_price >= 0.05 → "Good trade" else not recommended
```
Optionally extend with:
- Implied vol comparison
- Bid/ask midpoint instead of last trade
- Greeks (delta, vega) for additional filters

## Frontend Behavior
1. User submits ticker list & optional expiration
2. JS sends POST `/api/analyze`
3. Renders each ticker block with tables (calls & puts)
4. Plots call Last Price vs SMA using Chart.js (first ticker)

## Local Development
```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1
pip install -r requirements.txt
python api_server.py
```
Visit: http://localhost:5000

## Error Handling
| Case | Response |
|------|----------|
| No tickers provided | 400 with `{ "error": "No tickers provided" }` |
| yfinance failure / empty chain | Empty arrays for that side |
| Underlying price missing | Result object contains `error` key |

## Architecture Notes
- Separation of concerns: Flask only orchestrates I/O; computations in `backend/analysis.py`.
- Stateless: Each request performs fresh yfinance queries (add caching if needed).
- Near-the-money filtering: 12 closest strikes to underlying to reduce payload size.

## Extensibility Ideas
| Improvement | Approach |
|-------------|----------|
| Implied Vol | Scrape IV from chain (if available) or compute via BS inversion. |
| Configurable params | Add query/body fields for `sigma`, `r`, SMA window, threshold. |
| Refresh loop | Frontend `setInterval` + diff highlighting. |
| Caching | LRU cache keyed by (ticker, expiration, timestamp bucket). |
| Persistence | Store snapshots in SQLite/Postgres for historical analytics. |
| Auth | Add API keys / JWT if exposing publicly. |
| Docker | Create a Dockerfile + compose for reproducible deployment. |
| Tests | Add unit tests for `analyze_ticker` and pricing functions. |

## Minimal Test Snippet
```python
from backend.analysis import analyze
print(analyze(["AAPL", "MSFT"], None))
```

## Security Considerations
- yfinance is unauthenticated; guard against rate limiting with backoff.
- Validate user inputs (tickers length, allowed chars A-Z). Current implementation is lenient.
- Add timeout wrappers for external calls if deploying at scale.

## License
Internal prototype; add a LICENSE file if distributing.

---
Questions or want new features? Extend `backend/analysis.py` and the UI will reflect new JSON fields with minimal JS tweaks.
