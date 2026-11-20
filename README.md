# EcoThread — Python Static Efficiency Review

> A lightweight Python code review tool by Mallik Group for Humanity.
>
> **Repository:** <https://github.com/Mallikgroup-for-Humanity/EcoThread>  
> **Vercel deployment:** See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment details.  
> **License:** MIT (see [LICENSE](LICENSE))

## 1D — Mission

EcoThread highlights possible repeated work in Python source. Its static analyzer flags loops containing nested loops as prompts for developer review. Findings are heuristic: nested loops are not automatically inefficient, and the analyzer does not prove that a change will improve performance.

## 2D — Features and architecture

- **AST-based Python review:** Parses Python source and reports nested-loop patterns with line numbers and a heuristic review score.
- **Command-line interface:** Analyze a local Python file with `main.py`.
- **Web interface:** Submit Python source to the Flask interface in `api/index.py`; submitted code is parsed, not executed.
- **Cloudflare Worker API:** The separate Worker provides JSON endpoints for health checks and Python source analysis. See [DEPLOYMENT.md](DEPLOYMENT.md).
- **Optional emissions estimate:** The CLI can estimate CO₂ savings only when before/after runtimes, assumed or measured power, and grid carbon intensity are all supplied.

## 3D — Metrics and limitations

The review score is a simple heuristic based on the number of nested-loop findings. It is not a benchmark, runtime measurement, or energy score. Static findings alone cannot establish that an optimization saves energy or emissions.

The optional CO₂ estimate uses the supplied runtime difference, power assumption, and grid intensity. Measure comparable runs and document the assumptions; the result is an estimate, not a direct emissions measurement. See `calculate_co2_impact` in `ecothread.py` for the calculation and input validation.

## 4D — Run locally

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

The Flask web interface is served by `api/index.py` in the Vercel deployment. For local setup and Worker commands, consult [DEPLOYMENT.md](DEPLOYMENT.md).

## 5D — Deployment

EcoThread has two documented deployment targets:

- **Vercel:** Flask web interface, served by `api/index.py`.
- **Cloudflare Workers:** Separate Python JSON API with `GET /`, `GET /health`, and `POST /analyze` endpoints.

Follow [DEPLOYMENT.md](DEPLOYMENT.md) for prerequisites, development, and deployment instructions. The Worker limits source input to 64 KiB.

## 6D — Repository guide

- `main.py` — command-line entry point.
- `ecothread.py` — Python AST analysis and optional CO₂ estimate.
- `api/index.py` — Flask web interface.
- `worker/` and `wrangler.jsonc` — Cloudflare Worker API and configuration.
- `tests/` — automated tests.
- `DEPLOYMENT.md` — hosting instructions.
- `requirements.txt` and `pyproject.toml` — runtime and Worker dependency configuration.

## 7D — Safety and attribution

EcoThread does not execute submitted source in its Flask analysis flow. Review findings and suggested changes before applying them, then use tests and benchmarks appropriate to your project. Do not treat static analysis or estimated emissions as a substitute for measurement.

Maintained by Niraj Mallik and Mallik Group for Humanity. Released under the MIT License; see [LICENSE](LICENSE) for terms.

## 8D — Roadmap

- Add carefully tested checks for more Python efficiency patterns.
- Expand automated coverage for the web and Worker interfaces.
- Compare analysis suggestions with reproducible benchmarks and document their limits.
