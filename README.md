# EcoThread — Python Efficiency Review

EcoThread is a lightweight Python static-analysis tool by Mallik Group for Humanity. It flags selected code patterns for developer review and can calculate an indicative emissions estimate from measurements supplied by the user.

**Status:** The analyzer, CLI, Flask interface, and Cloudflare Worker are available today. The AI assistant, 3D visualization, live local-grid carbon data, user accounts, and paid subscriptions described below are planned and are not implemented in this release.

**Repository:** <https://github.com/Mallikgroup-for-Humanity/EcoThread> · **GitHub Pages:** <https://mallikgroup-for-humanity.github.io/EcoThread/> · **Deployment details:** [DEPLOYMENT.md](DEPLOYMENT.md) · **License:** MIT ([LICENSE](LICENSE))

## What works today

- **Static Python analysis:** Parses source with Python's AST and reports nested-loop patterns with line numbers and a heuristic score. Submitted code is not executed.
- **Command-line interface:** Analyze a local Python file with `main.py`.
- **Flask interface:** The Vercel app in `api/index.py` provides static source review.
- **Cloudflare Worker API:** `GET /`, `GET /health`, and `POST /analyze` endpoints for health checks and source analysis. The Worker limits request bodies to 64 KiB.
- **Optional CO₂ estimate:** The CLI can estimate savings when before/after runtimes, power, and grid carbon intensity are all supplied.
- **Android build:** The repository contains a WebView app; GitHub Actions builds APKs for `v*` tags.

The root `index.html` and Android's bundled HTML are separate legacy demos, not the Flask interface. Their old key/payment screens are not an account-backed, payment-processor-verified subscription flow. Do not treat a displayed key or submitted payment reference as processor-confirmed payment.

## Requested product direction

These are roadmap goals, not features users can currently access:

- **AI sustainability assistant:** Connect server-side to the owner's own LLM harness. Keep credentials on the server, not in browser JavaScript, and disclose what source or conversation data is sent to the model.
- **3D and live carbon dashboard:** Add an interactive 3D visualization and, with the user's permission, retrieve current grid carbon intensity for a selected location. Show the data source and update time. An emissions estimate also needs an energy or power-and-duration measurement; location alone cannot measure a device's emissions.
- **Accessible experience:** Target WCAG 2.2 AA with keyboard and screen-reader support, reduced-motion behavior, and a non-3D alternative. Accessibility has not yet been audited, so no numeric accessibility score is claimed.
- **Trial and subscriptions:** The requested offer is 30 days free, then US$10/month. It needs account-backed entitlements and a hosted payment provider (for example, Stripe), verified server-side payment webhooks, receipts, and a customer cancellation/billing portal. This repository does not currently process or confirm payments.

## Metrics and limitations

The review score is a heuristic based on static findings. It is not a benchmark, runtime measurement, energy score, or proof that a refactor improves performance.

The optional CO₂ calculation uses the difference between supplied runtimes, a power assumption or measurement, and grid carbon intensity. Measure comparable runs and document the assumptions. The result is an estimate, not a direct emissions measurement. See `calculate_co2_impact` in `ecothread.py` for the formula and input validation.

## Run locally

Install the Flask dependency and start the web interface:

```bash
python -m pip install -r requirements.txt
python api/index.py
```

The local server listens on port `8000` by default (or the `PORT` environment variable). Run the tests with:

```bash
python -m unittest discover -s tests
```

Analyze a Python file from the repository root:

```bash
python main.py analyze path/to/file.py
```

To request an indicative CO₂ estimate, provide all four measurement inputs:

```bash
python main.py analyze path/to/file.py \
  --before-seconds 12.0 \
  --after-seconds 9.5 \
  --power-w 45 \
  --grid-intensity-g-per-kwh 400
```

## Deployments

- **GitHub Pages:** A push to `main` runs the Jekyll workflow and deploys the static root site. This does not run the Python Flask app.
- **Vercel:** Serves the Flask interface through `api/index.py`.
- **Cloudflare Workers:** Serves the separate Python JSON API.

See [DEPLOYMENT.md](DEPLOYMENT.md) for setup and deployment instructions. The current deployments do not include an LLM integration, live carbon-data provider, account system, or payment processor.

## Repository guide

- `ecothread.py` — Python AST analysis and optional CO₂ estimate.
- `main.py` — command-line entry point.
- `api/index.py` — Flask web interface.
- `worker/` and `wrangler.jsonc` — Cloudflare Worker API and configuration.
- `index.html` — standalone legacy demo.
- `android/` — Android WebView app and bundled HTML.
- `tests/` — automated tests.
- `DEPLOYMENT.md` — hosting instructions.
- `requirements.txt` and `pyproject.toml` — runtime and Worker dependency configuration.

## Safety and attribution

Review findings and suggestions before applying them; use project tests and reproducible benchmarks to evaluate changes. Do not treat static findings or estimated emissions as a substitute for measurement. Do not enter payment details into the legacy demo.

Maintained by Niraj Mallik and Mallik Group for Humanity. Released under the MIT License; see [LICENSE](LICENSE) for terms.

## Plans & payments (©Nirajmallik@hub)

| Plan | Price | Daily analyses | Max source |
|------|-------|----------------|-----------|
| Trial | free, 14 days | 25 | 16 KB |
| Pro | $9 / 31 days | 500 | 64 KB |
| Max | $29 / 31 days | 5000 | 256 KB |

API: `POST /api/trial {"email"}` → API key; `POST /api/analyze {"code"}` and `GET /api/account` with `X-API-Key`; `POST /api/checkout {"plan":"pro|max"}` → Stripe Checkout URL; `POST /api/stripe/webhook` (Stripe `checkout.session.completed`).

Environment: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_PRO`, `STRIPE_PRICE_MAX`, `ECOTHREAD_BASE_URL`, `ECOTHREAD_DB` (SQLite path; use persistent storage in production — serverless `/tmp` is ephemeral). Run tests: `python -m unittest discover -s tests`.
