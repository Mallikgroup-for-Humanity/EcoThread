# ©Nirajmallik@hub
"""Minimal web interface for static review; no user code is executed."""

import ast
import os
import sys
from flask import Flask, jsonify, render_template_string, request

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import billing
from ecothread import analyze_source

app = Flask(__name__)

HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>EcoThread Python Review</title>
  <style>
    body { font: 16px/1.5 system-ui, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; background: #0b1220; color: #e8f1ff; }
    main { background: #121b2d; border: 1px solid #35513c; border-radius: 16px; padding: 1.5rem; }
    textarea { box-sizing: border-box; width: 100%; min-height: 340px; padding: 1rem; color: inherit; background: #08121d; border: 1px solid #526276; border-radius: 8px; font: 14px/1.5 monospace; }
    button { margin-top: 1rem; padding: .8rem 1.2rem; border: 0; border-radius: 8px; background: #7ae582; font-weight: bold; cursor: pointer; }
    .note { color: #c4d2e3; }
    .error { color: #ffaaa3; }
    li { margin: .5rem 0; }
  </style>
</head>
<body><main>
  <h1>EcoThread</h1>
  <p>Free {{ trial_days }}-day trial, then Pro or Max. <a href="/pricing" style="color:#7ae582">Pricing</a></p>
  <p>Static Python review for possible repeated work. Findings are heuristic, not proof of inefficiency.</p>
  <form method="post">
    <label for="code">Python source</label>
    <label for="key">API key</label>
    <input id="key" name="key" type="password" autocomplete="off" placeholder="eco_..." style="width:100%;box-sizing:border-box;margin:.4rem 0 1rem;padding:.6rem;border-radius:8px">
    <textarea id="code" name="code" spellcheck="false">{{ code }}</textarea>
    <button type="submit">Analyze source</button>
  </form>
  {% if analyzed %}
    <h2>Review results</h2>
    {% if error %}<p class="error">Could not parse source: {{ error }}</p>
    {% else %}
      <p>Heuristic review score: {{ score }}/100 · Findings: {{ findings|length }}</p>
      {% if findings %}<ul>{% for finding in findings %}<li>{{ finding }}</li>{% endfor %}</ul>
      {% else %}<p>No nested-loop patterns flagged by this check.</p>{% endif %}
      <p><strong>CO₂ savings: Not measured.</strong> Static source analysis cannot establish runtime, energy use, or emissions.</p>
    {% endif %}
  {% endif %}
  <p class="note">This tool does not execute submitted code. Benchmark changes separately and provide documented power and grid-intensity data before estimating emissions.</p>
</main></body></html>"""


def analyze_python_code(code: str):
    """Return the heuristic score and findings for Python source."""
    return analyze_source(code)


@app.get("/")
def index():
    return render_template_string(HTML, code="", analyzed=False, trial_days=billing.TRIAL_DAYS)


@app.post("/")
def submit():
    code = request.form.get("code", "")
    try:
        billing.consume(request.form.get("key", "").strip(), len(code.encode()))
    except billing.BillingError as exc:
        return render_template_string(
            HTML, code=code, analyzed=True, error=str(exc), trial_days=billing.TRIAL_DAYS
        ), exc.status
    try:
        score, findings = analyze_python_code(code)
    except (SyntaxError, ValueError) as exc:
        return render_template_string(HTML, code=code, analyzed=True, error=str(exc), trial_days=billing.TRIAL_DAYS)
    return render_template_string(
        HTML, code=code, analyzed=True, score=score, findings=findings, error=None,
        trial_days=billing.TRIAL_DAYS,
    )


PRICING = """<!doctype html><meta charset="utf-8"><title>EcoThread Pricing</title>
<body style="font:16px system-ui;max-width:720px;margin:2rem auto;background:#0b1220;color:#e8f1ff">
<h1>EcoThread Pricing</h1>
{% if paid %}<p>Payment received. Your plan activates within moments.</p>{% endif %}
<ul>{% for name, p in plans.items() %}<li><b>{{ name|upper }}</b> - ${{ p.price_usd }}{% if name != "trial" %}/month{% endif %},
{{ p.daily_limit }} analyses/day, {{ p.max_source_bytes // 1024 }} KB source</li>{% endfor %}</ul>
<p>Start the trial: POST /api/trial {"email": "you@example.com"}. Upgrade: POST /api/checkout {"plan": "pro"|"max"} with X-API-Key.</p>
<p>&copy; Nirajmallik@hub</p></body>"""


def _json_body():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _error(exc):
    return jsonify(error=str(exc)), exc.status


@app.get("/pricing")
def pricing():
    return render_template_string(PRICING, plans=billing.PLANS, paid=request.args.get("paid"))


@app.get("/api/plans")
def api_plans():
    return jsonify(plans=billing.PLANS)


@app.post("/api/trial")
def api_trial():
    try:
        return jsonify(billing.start_trial(_json_body().get("email"))), 201
    except billing.BillingError as exc:
        return _error(exc)


@app.get("/api/account")
def api_account():
    try:
        return jsonify(billing._public(billing.get_account(request.headers.get("X-API-Key", ""))))
    except billing.BillingError as exc:
        return _error(exc)


@app.post("/api/analyze")
def api_analyze():
    code = _json_body().get("code")
    if not isinstance(code, str):
        return jsonify(error="'code' string is required"), 400
    try:
        info = billing.consume(request.headers.get("X-API-Key", ""), len(code.encode()))
        score, findings = analyze_python_code(code)
    except billing.BillingError as exc:
        return _error(exc)
    except (SyntaxError, ValueError) as exc:
        return jsonify(error="Could not parse source: %s" % exc), 422
    return jsonify(score=score, findings=findings, plan=info["plan"], remaining_today=info["remaining_today"])


@app.post("/api/checkout")
def api_checkout():
    try:
        return jsonify(billing.create_checkout(request.headers.get("X-API-Key", ""), _json_body().get("plan")))
    except billing.BillingError as exc:
        return _error(exc)


@app.post("/api/stripe/webhook")
def stripe_webhook():
    try:
        return jsonify(billing.handle_webhook(request.get_data(), request.headers.get("Stripe-Signature", "")))
    except billing.BillingError as exc:
        return _error(exc)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
