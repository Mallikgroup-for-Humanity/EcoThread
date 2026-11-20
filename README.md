# EcoThread — Static Code Efficiency Analyzer

> Browser-based code analysis and refactoring assistant by Mallik Group for Humanity.
>
> **Repository:** <https://github.com/Mallikgroup-for-Humanity/EcoThread>  
> **Live site:** <https://mallikgroup-for-humanity.github.io/EcoThread/>  
> **License:** MIT (see [LICENSE](LICENSE))

## 1. Mission

EcoThread helps developers spot common sources of avoidable work in everyday code, such as repeated lookups, verbose logging, unbounded queries, and inefficient iteration. It provides static findings and suggested refactoring alongside indicative code-size and work-saved estimates.

## 2. Features

- **Static analysis and refactoring:** Analyze JavaScript/TypeScript, Python, and SQL snippets, with automatic language detection or manual selection.
- **Efficiency report:** Review a heuristic Green Score, source/output byte counts, estimated work saved, and explanations of detected patterns.
- **Sample snippets:** Load example code to explore supported checks.
- **Browser-based usage:** The analyzer runs in the browser and does not require a project backend for its static checks.

## 3. Metrics and limitations

EcoThread's Green Score, byte reduction, and estimated operations saved are heuristic indicators derived from static pattern matches. They are not measurements of runtime, electricity use, or carbon emissions. Validate suggested changes with tests, profilers, and benchmarks before adopting them in production; some transformations require project-specific context.

## 4. Free and Pro modes

The browser UI provides a free run allowance and a 30-day Pro state. Run counts and Pro state are stored in the browser's `localStorage`, so they are local to that browser and can be cleared or modified by its user.

**Important:** Entering a transaction reference in the static site does not verify payment with a financial provider or server. It only changes local browser state. Do not treat this client-side flow as secure entitlement or payment verification.

For current payment instructions, contact the maintainer privately. Financial account and personal payment details are intentionally not published in this README.

## 5. Repository overview

- `index.html` — browser-based optimizer interface.
- `main.py`, `ecothread.py`, and `engine/` — Python analysis and optimization components.
- `api/` and `worker/` — API and edge-runtime components.
- `tests/` — automated tests.
- `DEPLOYMENT.md` — deployment guidance.

## 6. Deployment

The repository includes deployment configuration for its supported hosting targets. See [DEPLOYMENT.md](DEPLOYMENT.md) for setup details. The GitHub Pages site serves the static frontend; client-side features do not provide server-side payment verification.

## 7. Attribution and license

EcoThread is maintained by Niraj Mallik and Mallik Group for Humanity. It is released under the MIT License; see [LICENSE](LICENSE) for the full text.

## 8. Roadmap

- Expand static rules for additional languages and patterns.
- Add focused automated checks for deployment and supported frontend behavior.
- Evaluate analyzer suggestions against representative benchmarks and document their limits.
