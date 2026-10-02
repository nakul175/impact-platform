"""Email send rate limits for the worker (v0.27 email readiness).

A transactional email provider admits so many messages per period (per account, sometimes per
sending domain). The worker respects such a limit at claim time: it claims only as many due EMAIL
intents as the limit still admits and leaves the rest PENDING and due. A deferred intent keeps its
attempt count and its `next_attempt_at`, so rate limiting can never make a delivery DEAD and never
consumes one of its six attempts; it is simply claimed on a later iteration. In-app intents are
never limited.

Two sliding windows share one length (`email_rate_window_seconds`): a global one
(`email_rate_limit`) and one per tenant (`email_tenant_rate_limit`); 0 means no limit. Both count
claims, not successful sends, so a message the provider refused still counts as one submission
toward the provider's quota, which is how providers count. The windows live in the worker process
(no table, no migration); with more than one worker process each process has its own allowance,
so the provider limit is divided between them (DEPLOYMENT-GUIDE.md, section 5). The clock is the
database time the worker already fetched for the claim, never the host clock, so every worker
agrees with the lease logic about when a window ends.
"""

import threading
from collections import deque
from datetime import timedelta

MAX_WINDOW_SECONDS = 86400
MAX_RATE = 1_000_000


class EmailRateLimiter:
    """Sliding windows of claim instants. Thread-safe; `at` is a timezone-aware datetime."""

    def __init__(self, global_limit=0, tenant_limit=0, window_seconds=60):
        if global_limit < 0 or tenant_limit < 0 or not 1 <= window_seconds <= MAX_WINDOW_SECONDS:
            raise ValueError("INVALID_EMAIL_RATE_LIMIT")
        self.global_limit = int(global_limit)
        self.tenant_limit = int(tenant_limit)
        self.window = timedelta(seconds=window_seconds)
        self.global_claims = deque()
        self.tenant_claims = {}
        self.deferred = 0
        self.lock = threading.Lock()

    @classmethod
    def from_settings(cls, s):
        return cls(
            global_limit=getattr(s, "email_rate_limit", 0),
            tenant_limit=getattr(s, "email_tenant_rate_limit", 0),
            window_seconds=getattr(s, "email_rate_window_seconds", 60),
        )

    @property
    def enabled(self):
        return bool(self.global_limit or self.tenant_limit)

    def prune(self, at):
        horizon = at - self.window
        while self.global_claims and self.global_claims[0] <= horizon:
            self.global_claims.popleft()
        for tenant in list(self.tenant_claims):
            claims = self.tenant_claims[tenant]
            while claims and claims[0] <= horizon:
                claims.popleft()
            if not claims:
                del self.tenant_claims[tenant]

    def allowance(self, tenant, at):
        """How many EMAIL intents of `tenant` may be claimed at `at`; None means no limit applies."""
        if not self.enabled:
            return None
        with self.lock:
            self.prune(at)
            remaining = []
            if self.global_limit:
                remaining.append(self.global_limit - len(self.global_claims))
            if self.tenant_limit:
                remaining.append(self.tenant_limit - len(self.tenant_claims.get(tenant, ())))
            return max(0, min(remaining))

    def record(self, tenant, at, count):
        """Count `count` EMAIL claims of `tenant` at `at` (claims, not successful sends)."""
        if not self.enabled or count <= 0:
            return
        with self.lock:
            for _ in range(count):
                self.global_claims.append(at)
                self.tenant_claims.setdefault(tenant, deque()).append(at)

    def defer(self, count):
        if count > 0:
            with self.lock:
                self.deferred += count

    def retry_after(self, tenant, at):
        """Seconds until the oldest counted claim leaves the window (0 when nothing is counted)."""
        with self.lock:
            self.prune(at)
            oldest = []
            if self.global_limit and self.global_claims and len(self.global_claims) >= self.global_limit:
                oldest.append(self.global_claims[0])
            claims = self.tenant_claims.get(tenant)
            if self.tenant_limit and claims and len(claims) >= self.tenant_limit:
                oldest.append(claims[0])
            if not oldest:
                return 0.0
            return max(0.0, (min(oldest) + self.window - at).total_seconds())
