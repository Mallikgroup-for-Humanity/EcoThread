cat << 'EOF' > README.md
<div align="center">

# EcoThread

**3D Spatial Code Efficiency Analyzer, Rewrite Optimizer & Telemetry Engine**  
*Developed by **Mallik Group for Humanity** (`Malikgroup-for-Humanity`)*[span_3](start_span)[span_3](end_span)

[![License: MIT](https://img.shields.io/badge/License-MIT%202026-10b981?style=for-the-badge)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](pyproject.toml)
[![Deployments](https://img.shields.io/badge/Deploy-Vercel%20%7C%20GitHub%20Pages%20%7C%20Cloudflare-000000?style=for-the-badge&logo=vercel&logoColor=white)](DEPLOYMENT.md)

> **"Problem = Solve = Success"**

</div>

---

## 1. Overview & Vision

**EcoThread** is a multi-environment static code analysis and optimization suite designed to inspect Python code patterns, detect computational bottlenecks (such as deeply nested loops), estimate heuristic energy and $\text{CO}_2$ savings, and visualize code complexity in an interactive 3D and browser-based workspace[span_4](start_span)[span_4](end_span). 

Engineered for mobile-first development (Termux) as well as cloud and edge runtimes, EcoThread bridges command-line Abstract Syntax Tree (AST) parsing with web-based interactive rewrites and automated deployment pipelines[span_5](start_span)[span_5](end_span).

---

## 2. What's New (Latest Updates)

* **3D Visualization & Spatial AST Module:** Added 3D structural representation support for inspecting code complexity hotspots and execution paths.
* **Automated Vercel Deployment Reset (`vercel_reset_deploy.js`):** Introduced a Node.js automation script to clean stale Vercel deployments and trigger fresh production builds directly from the terminal[span_6](start_span)[span_6](end_span)[span_7](start_span)[span_7](end_span).
* **CI/CD GitHub Pages Pipeline (`.github/workflows/jekyll-gh-pages.yml`):** Configured automated GitHub Actions builds so static frontend updates on `main` deploy immediately to GitHub Pages[span_8](start_span)[span_8](end_span)[span_9](start_span)[span_9](end_span).
* **Repository Hygiene & Privacy Hardening (`.gitignore`):** Removed compiled Python bytecode (`__pycache__/`) from Git tracking and enforced strict ignore rules for local caches and environment secrets[span_10](start_span)[span_10](end_span)[span_11](start_span)[span_11](end_span).

---

## 3. Core Architecture & File-by-File Explanation

### 🧠 Analysis & Optimization Engine
* **`main.py` & `ecothread.py`:** Primary entry points for the Python CLI (`python main.py analyze <file.py>`) and Flask web server[span_12](start_span)[span_12](end_span). Parses Python AST structures to flag nested loops and calculate optional heuristic $\text{CO}_2$ estimates using runtime, assumed power draw, and grid carbon intensity inputs[span_13](start_span)[span_13](end_span).
* **`engine/`:** Core static analysis rules, pattern matchers, complexity scoring algorithms, and rewrite suggestion generators[span_14](start_span)[span_14](end_span).
* **`api/`:** REST API route handlers exposing EcoThread's analysis and rewrite engine to external clients and frontend interfaces[span_15](start_span)[span_15](end_span).

### 🌐 Interactive Frontend & 3D Workspace
* **`index.html`:** Browser-based optimizer and 3D visualization interface[span_16](start_span)[span_16](end_span). Allows users to paste Python snippets, inspect flagged patterns, view suggested rewrites, and copy or download optimized code (includes a 5-run browser profile demo mode)[span_17](start_span)[span_17](end_span).

### 🔐 Pro Licensing & Owner Security Gate
* **`ecothread_pro_gate.py`:** Validates 18-digit EcoThread Free/Pro access keys to unlock extended optimization runs and advanced telemetry[span_18](start_span)[span_18](end_span).
* **`activate_ecothread_customer.py`:** Automated customer key generation and provisioning script[span_19](start_span)[span_19](end_span).
* **`owner-face-key.html`:** Experimental owner-level authentication and biometric/face-key access prototype (`@Nirajmallik@hub`)[span_20](start_span)[span_20](end_span).

### ☁️ Multi-Cloud & Edge Deployment
* **`vercel.json` & `vercel_reset_deploy.js`:** Configures the Python/Flask serverless runtime on Vercel alongside automated deployment cleanup and redeployment[span_21](start_span)[span_21](end_span)[span_22](start_span)[span_22](end_span)[span_23](start_span)[span_23](end_span).
* **`worker/` & `wrangler.jsonc`:** Cloudflare Workers edge deployment setup providing a low-latency JSON API[span_24](start_span)[span_24](end_span).
* **`.github/workflows/`:** Automated continuous integration analysis and GitHub Pages publishing workflows[span_25](start_span)[span_25](end_span)[span_26](start_span)[span_26](end_span).

### 📊 Documentation, Benchmarks & Testing
* **`DEPLOYMENT.md`:** Step-by-step deployment instructions for Vercel, Cloudflare Workers, and local servers[span_27](start_span)[span_27](end_span).
* **`LEADERBOARD.md`:** Benchmark metrics tracking code efficiency improvements and optimization scores[span_28](start_span)[span_28](end_span).
* **`tests/`:** Automated unit and integration tests verifying AST detection accuracy and Pro-gate key validation[span_29](start_span)[span_29](end_span).
* **`pyproject.toml` & `requirements.txt`:** Python packaging metadata and dependency definitions[span_30](start_span)[span_30](end_span).

---

## 4. End-to-End Execution Flow

```text
[ Python Source Code ]
         │
         ▼
┌─────────────────────────────────────────┐
│  1. AST Parser & Pattern Engine         │  ◄── main.py / ecothread.py / engine/
│     • Detects nested loops & hotspots   │
│     • Computes heuristic CO₂ deltas     │
└────────┬───────────────────────┬────────┘
         │                       │
         ▼                       ▼
┌──────────────────┐   ┌──────────────────┐
│ 2A. CLI Output   │   │ 2B. 3D Web UI &  │  ◄── index.html / api/ / worker/
│ • Terminal audit │   │     Edge API     │
│ • JSON/text logs │   │ • Live rewrites  │
└──────────────────┘   └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ 3. Pro & Owner   │  ◄── ecothread_pro_gate.py
                       │    Access Gate   │      owner-face-key.html
                       └──────────────────┘
