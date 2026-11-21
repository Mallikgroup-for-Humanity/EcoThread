# Deployment

EcoThread has three deployment targets. GitHub Pages deploys the static root site, Vercel serves the Flask web interface, and Cloudflare Workers serves a lightweight Python JSON API. The reported CO₂ value is an estimate—not a measurement. The current deployments do not include an LLM integration, live carbon-data provider, account system, or payment processor.

## GitHub Pages (static site)

The workflow in `.github/workflows/jekyll-gh-pages.yml` builds the repository root with Jekyll and deploys it to <https://mallikgroup-for-humanity.github.io/EcoThread/>. A push to `main` triggers deployment; the workflow can also be started manually from the GitHub Actions tab.

GitHub Pages only serves static files and does not run the Flask application. The repository's root `index.html` is a standalone legacy demo; the Markdown README is repository documentation, not the deployed Flask interface.

## Vercel (web interface)

1. Import `nirajmallik143-hub/EcoThread` into Vercel and keep the project root at the repository root.
2. Vercel detects `vercel.json` and installs the Flask dependency from `requirements.txt`.
3. Deploy, then open the deployment URL. The Python web app is served by `api/index.py`.

No environment variables are required. The CLI (`main.py`) is not part of the serverless web deployment.

## Cloudflare Workers (JSON API)

The Worker is implemented separately from Flask because Cloudflare Workers does not run the Vercel/Flask application entrypoint. It provides `GET /` and `GET /health` health checks, plus `POST /analyze`.

Requirements: a current `uv` installation and Cloudflare account authenticated with Wrangler.

```bash
uv sync
uv run pywrangler dev
```

Deploy with:

```bash
uv run pywrangler deploy
```

Example request:

```bash
curl -X POST https://<your-worker>.<your-subdomain>.workers.dev/analyze \
  -H 'content-type: application/json' \
  --data '{"code":"for x in xs:\n    for y in ys:\n        pass"}'
```

The API expects a JSON object with a string `code` field and limits source input to 64 KiB. Invalid JSON, Python syntax errors, unsupported routes, and oversized payloads return JSON error responses. Cloudflare's `wrangler.jsonc` selects the Python Worker entry point and enables the Python Workers compatibility flag.


---
©Nirajmallik@hub
