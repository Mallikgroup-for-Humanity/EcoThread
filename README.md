# EcoThread

EcoThread is a collection of small tools for reviewing Python code patterns and exploring more efficient implementations. It includes a command-line analyzer, browser-based optimizer prototype, and optional web/API deployments. Static findings and displayed scores are heuristics; they are not measurements of runtime, energy use, or emissions.

## What’s included

- **Python CLI:** `main.py analyze` parses a Python file and flags nested loops for human review. Optional CO₂ estimates require before/after runtimes, assumed power, and grid carbon intensity.
- **Browser optimizer:** Open `index.html` to inspect snippets for a few patterns, view suggested rewrites, and copy or download the output. The browser demo allows five free runs per browser profile.
- **Pro and owner-key prototypes:** `ecothread_pro_gate.py`, `activate_ecothread_customer.py`, and `owner-face-key.html` contain experimental access and key-related flows.
- **Deployments:** `DEPLOYMENT.md` documents the Flask web app for Vercel and the JSON API for Cloudflare Workers.

## Getting started

Clone this repository and run the Python CLI with Python 3:

```bash
git clone https://github.com/Mallikgroup-for-Humanity/EcoThread.git
cd EcoThread
python main.py analyze path/to/your_file.py
```

To estimate CO₂ savings, supply all four inputs; these are assumptions based on your own measurements, not values measured by EcoThread:

```bash
python main.py analyze path/to/your_file.py \
  --before-seconds 10 \
  --after-seconds 8 \
  --power-w 50 \
  --grid-intensity-g-per-kwh 400
```

For the browser demo, open `index.html` in a browser. The owner-key page requests camera access and generally needs to be served from `localhost` or HTTPS; open `owner-face-key.html` only if you intend to try that prototype.

## Important limitations

- Analysis is heuristic. A flagged pattern is a prompt for review, not proof that code is inefficient or that a suggested change is equivalent or faster.
- CO₂ estimates are only produced by the CLI when all runtime and energy assumptions are supplied. Results depend on those inputs and do not represent measured emissions.
- The browser Pro activation flow is client-side and does not reliably verify payment or enforce tamper-resistant licensing. Do not use it for production billing or access control.
- The owner-face page compares a small image-derived vector stored in browser local storage. It is not robust biometric authentication, and its generated key flow is a prototype—not a secure identity or authorization system.
- The browser demo includes payment contact and transfer details configured in `index.html`.
- `activate_ecothread_customer.py` imports `auto_payment_key_engine` from a separate local project and is not standalone.

## Repository layout

| Path | Purpose |
| --- | --- |
| `main.py`, `ecothread.py` | Python CLI and static analysis / estimate logic |
| `index.html` | Browser-based optimizer and experimental Pro activation UI |
| `ecothread_pro_gate.py` | Experimental local free/Pro access check |
| `activate_ecothread_customer.py` | Bridge to an external payment-key engine |
| `owner-face-key.html` | Experimental browser camera and owner-key flow |
| `api/`, `worker/` | Vercel web app and Cloudflare Workers API |
| `DEPLOYMENT.md` | Deployment instructions |
| `tests/` | Python tests |

## License

This project is distributed under the MIT License. See [LICENSE](LICENSE).
