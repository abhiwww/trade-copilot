from __future__ import annotations
import time
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import json

# Rate limit storage path
LIMITS_FILE = Path("data/ratelimits.json")

class RateLimiter:
    """
    A simple file-backed rate limiter.
    In production, this would be implemented in Redis using INCR and EXPIRE.
    """
    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        LIMITS_FILE.parent.mkdir(exist_ok=True)
        if not LIMITS_FILE.exists():
            with open(LIMITS_FILE, "w") as f:
                json.dump({}, f)

    def _load(self) -> Dict[str, List[float]]:
        with open(LIMITS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def _save(self, data: Dict[str, List[float]]):
        with open(LIMITS_FILE, "w") as f:
            json.dump(data, f)

    def check_limit(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """
        Checks if a key has exceeded the limit within the given window (seconds).
        Returns (is_allowed, retry_after).
        """
        now = time.time()
        data = self._load()

        # Get timestamps for this key, filter out those outside the window
        timestamps = data.get(key, [])
        timestamps = [ts for ts in timestamps if now - ts < window]

        if len(timestamps) >= limit:
            # Calculate time until the oldest request in the window expires
            retry_after = int(window - (now - timestamps[0]))
            return False, retry_after

        # Record current request
        timestamps.append(now)
        data[key] = timestamps
        self._save(data)
        return True, 0

# Global rate limiter instance
limiter = RateLimiter()
