"""The one definition of "now" for request-time code (timezone-aware UTC).

Modules import it by name (`from .clock import now`), so a test may still replace `module.now`.
The worker has its own database-clock logic and does not use this.
"""

from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc)
