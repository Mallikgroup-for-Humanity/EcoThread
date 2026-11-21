# ©Nirajmallik@hub
"""Plans, API keys, usage metering and Stripe payments for EcoThread.

Plans: TRIAL (14 days, free), PRO and MAX (paid monthly via Stripe Checkout).
Secrets come from the environment only:
  STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, STRIPE_PRICE_PRO, STRIPE_PRICE_MAX,
  ECOTHREAD_DB (SQLite path), ECOTHREAD_BASE_URL (for checkout redirects).
"""

import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

TRIAL_DAYS = 14
PAID_DAYS = 31
WEBHOOK_TOLERANCE_S = 300

PLANS = {
    "trial": {"price_usd": 0, "daily_limit": 25, "max_source_bytes": 16 * 1024, "days": TRIAL_DAYS},
    "pro": {"price_usd": 9, "daily_limit": 500, "max_source_bytes": 64 * 1024, "days": PAID_DAYS},
    "max": {"price_usd": 29, "daily_limit": 5000, "max_source_bytes": 256 * 1024, "days": PAID_DAYS},
}
PAID_PLANS = ("pro", "max")
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,255}\.[^@\s]{2,}$")

_lock = threading.Lock()


class BillingError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def _db_path():
    return os.environ.get("ECOTHREAD_DB") or os.path.join(tempfile.gettempdir(), "ecothread.db")


def _connect():
    conn = sqlite3.connect(_db_path(), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS accounts (
            id TEXT PRIMARY KEY, email TEXT UNIQUE NOT NULL, key_hash TEXT UNIQUE NOT NULL,
            plan TEXT NOT NULL, expires_at INTEGER NOT NULL, created_at INTEGER NOT NULL,
            stripe_customer TEXT);
        CREATE TABLE IF NOT EXISTS usage (
            account_id TEXT NOT NULL, day TEXT NOT NULL, count INTEGER NOT NULL,
            PRIMARY KEY (account_id, day));
        CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY);
        """
    )
    return conn


def _hash_key(key):
    return hashlib.sha256(key.encode()).hexdigest()


def _today():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _public(row):
    now = int(time.time())
    plan = row["plan"]
    active = row["expires_at"] > now
    return {
        "account_id": row["id"],
        "email": row["email"],
        "plan": plan,
        "active": active,
        "expires_at": row["expires_at"],
        "daily_limit": PLANS[plan]["daily_limit"],
        "max_source_bytes": PLANS[plan]["max_source_bytes"],
    }


def start_trial(email):
    """Create a free-trial account; returns the API key (shown only once)."""
    email = (email or "").strip().lower()
    if not EMAIL_RE.match(email):
        raise BillingError("A valid email is required")
    key = "eco_" + secrets.token_urlsafe(32)
    now = int(time.time())
    with _lock, _connect() as conn:
        try:
            conn.execute(
                "INSERT INTO accounts (id, email, key_hash, plan, expires_at, created_at) VALUES (?,?,?,?,?,?)",
                (secrets.token_hex(8), email, _hash_key(key), "trial", now + TRIAL_DAYS * 86400, now),
            )
        except sqlite3.IntegrityError:
            raise BillingError("A trial already exists for this email", 409)
    return {"api_key": key, "plan": "trial", "trial_days": TRIAL_DAYS}


def get_account(key):
    if not key:
        raise BillingError("Missing API key (X-API-Key header)", 401)
    with _connect() as conn:
        row = conn.execute("SELECT * FROM accounts WHERE key_hash=?", (_hash_key(key),)).fetchone()
    if row is None:
        raise BillingError("Invalid API key", 401)
    return row


def consume(key, source_bytes=0):
    """Authenticate, enforce plan expiry/quotas, and count one analysis."""
    row = get_account(key)
    info = _public(row)
    if not info["active"]:
        raise BillingError("Plan expired - upgrade at /pricing", 402)
    if source_bytes > info["max_source_bytes"]:
        raise BillingError("Source exceeds the %d byte limit of the %s plan" % (info["max_source_bytes"], info["plan"]), 413)
    day = _today()
    with _lock, _connect() as conn:
        conn.execute("INSERT OR IGNORE INTO usage VALUES (?,?,0)", (row["id"], day))
        cur = conn.execute(
            "UPDATE usage SET count=count+1 WHERE account_id=? AND day=? AND count<?",
            (row["id"], day, info["daily_limit"]),
        )
        used = conn.execute("SELECT count FROM usage WHERE account_id=? AND day=?", (row["id"], day)).fetchone()[0]
    if cur.rowcount == 0:
        raise BillingError("Daily limit reached for the %s plan - upgrade at /pricing" % info["plan"], 429)
    info["used_today"] = used
    info["remaining_today"] = info["daily_limit"] - used
    return info


def activate_paid(account_id, plan, stripe_customer=None):
    """Upgrade (or extend) an account after a verified payment."""
    if plan not in PAID_PLANS:
        raise BillingError("Unknown plan")
    now = int(time.time())
    with _lock, _connect() as conn:
        row = conn.execute("SELECT * FROM accounts WHERE id=?", (account_id,)).fetchone()
        if row is None:
            raise BillingError("Unknown account", 404)
        base = row["expires_at"] if row["plan"] == plan and row["expires_at"] > now else now
        conn.execute(
            "UPDATE accounts SET plan=?, expires_at=?, stripe_customer=COALESCE(?, stripe_customer) WHERE id=?",
            (plan, base + PLANS[plan]["days"] * 86400, stripe_customer, account_id),
        )


def _stripe(path, data):
    secret = os.environ.get("STRIPE_SECRET_KEY")
    if not secret:
        raise BillingError("Payments are not configured", 503)
    req = urllib.request.Request(
        "https://api.stripe.com/v1/" + path,
        data=urllib.parse.urlencode(data).encode(),
        headers={"Authorization": "Bearer " + secret},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, ValueError):
        raise BillingError("Payment provider error", 502)


def create_checkout(key, plan):
    if plan not in PAID_PLANS:
        raise BillingError("plan must be 'pro' or 'max'")
    row = get_account(key)
    price = os.environ.get("STRIPE_PRICE_" + plan.upper())
    if not price:
        raise BillingError("Payments are not configured", 503)
    base = os.environ.get("ECOTHREAD_BASE_URL", "").rstrip("/")
    session = _stripe(
        "checkout/sessions",
        {
            "mode": "payment",
            "line_items[0][price]": price,
            "line_items[0][quantity]": "1",
            "client_reference_id": row["id"],
            "customer_email": row["email"],
            "metadata[plan]": plan,
            "success_url": base + "/pricing?paid=1",
            "cancel_url": base + "/pricing?canceled=1",
        },
    )
    return {"checkout_url": session.get("url")}


def verify_webhook(payload, header, secret, now=None):
    """Verify a Stripe-Signature header (HMAC-SHA256 over '<t>.<payload>')."""
    if not secret or not header:
        return False
    try:
        parts = dict(p.split("=", 1) for p in header.split(","))
        ts = int(parts["t"])
    except (ValueError, KeyError):
        return False
    if abs((now or time.time()) - ts) > WEBHOOK_TOLERANCE_S:
        return False
    expected = hmac.new(secret.encode(), b"%d." % ts + payload, hashlib.sha256).hexdigest()
    return any(
        hmac.compare_digest(expected, p.split("=", 1)[1])
        for p in header.split(",")
        if p.startswith("v1=")
    )


def handle_webhook(payload, header):
    if not verify_webhook(payload, header, os.environ.get("STRIPE_WEBHOOK_SECRET", "")):
        raise BillingError("Invalid signature", 400)
    try:
        event = json.loads(payload.decode())
    except ValueError:
        raise BillingError("Invalid payload")
    if event.get("type") != "checkout.session.completed":
        return {"ignored": True}
    obj = event["data"]["object"]
    if obj.get("payment_status") != "paid":
        return {"ignored": True}
    with _lock, _connect() as conn:
        try:
            conn.execute("INSERT INTO events VALUES (?)", (event["id"],))
        except sqlite3.IntegrityError:
            return {"duplicate": True}
    activate_paid(obj.get("client_reference_id"), (obj.get("metadata") or {}).get("plan"), obj.get("customer"))
    return {"activated": True}
