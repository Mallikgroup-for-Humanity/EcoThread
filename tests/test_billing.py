# ©Nirajmallik@hub
"""Tests for plans, quotas and Stripe webhook handling."""

import hashlib
import hmac
import json
import os
import sys
import tempfile
import time
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import billing
from api.index import app

SECRET = "whsec_test"


def signed(event):
    body = json.dumps(event).encode()
    ts = int(time.time())
    sig = hmac.new(SECRET.encode(), b"%d." % ts + body, hashlib.sha256).hexdigest()
    return body, "t=%d,v1=%s" % (ts, sig)


class BillingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        os.environ["ECOTHREAD_DB"] = os.path.join(self.tmp, "t.db")
        os.environ["STRIPE_WEBHOOK_SECRET"] = SECRET
        self.client = app.test_client()

    def trial(self, email="a@b.co"):
        return self.client.post("/api/trial", json={"email": email}).get_json()["api_key"]

    def test_trial_once_per_email_and_analyze(self):
        key = self.trial()
        self.assertEqual(self.client.post("/api/trial", json={"email": "a@b.co"}).status_code, 409)
        r = self.client.post("/api/analyze", json={"code": "x = 1"}, headers={"X-API-Key": key})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["plan"], "trial")

    def test_requires_valid_key(self):
        r = self.client.post("/api/analyze", json={"code": "x = 1"})
        self.assertEqual(r.status_code, 401)

    def test_daily_limit_and_expiry(self):
        key = self.trial()
        orig = billing.PLANS["trial"]["daily_limit"]
        billing.PLANS["trial"]["daily_limit"] = 1
        try:
            billing.consume(key)
            with self.assertRaises(billing.BillingError) as ctx:
                billing.consume(key)
            self.assertEqual(ctx.exception.status, 429)
        finally:
            billing.PLANS["trial"]["daily_limit"] = orig
        row = billing.get_account(key)
        with billing._connect() as conn:
            conn.execute("UPDATE accounts SET expires_at=1 WHERE id=?", (row["id"],))
        with self.assertRaises(billing.BillingError) as ctx:
            billing.consume(key)
        self.assertEqual(ctx.exception.status, 402)

    def test_webhook_upgrades_once(self):
        key = self.trial()
        acct = billing.get_account(key)["id"]
        event = {"id": "evt_1", "type": "checkout.session.completed", "data": {"object": {
            "client_reference_id": acct, "payment_status": "paid", "metadata": {"plan": "max"}}}}
        body, sig = signed(event)
        h = {"Stripe-Signature": sig}
        self.assertEqual(self.client.post("/api/stripe/webhook", data=body, headers=h).status_code, 200)
        self.assertEqual(billing.get_account(key)["plan"], "max")
        r = self.client.post("/api/stripe/webhook", data=body, headers=h)
        self.assertTrue(r.get_json().get("duplicate"))

    def test_webhook_rejects_bad_signature(self):
        r = self.client.post("/api/stripe/webhook", data=b"{}", headers={"Stripe-Signature": "t=1,v1=x"})
        self.assertEqual(r.status_code, 400)

    def test_checkout_unconfigured(self):
        key = self.trial()
        os.environ.pop("STRIPE_SECRET_KEY", None)
        os.environ.pop("STRIPE_PRICE_PRO", None)
        r = self.client.post("/api/checkout", json={"plan": "pro"}, headers={"X-API-Key": key})
        self.assertEqual(r.status_code, 503)


if __name__ == "__main__":
    unittest.main()
