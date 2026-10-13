from __future__ import annotations
import secrets
import time
from typing import Optional, Dict, Any
from pathlib import Path
import json
from app.core.repository import DATA_DIR

# Session storage path
SESSIONS_FILE = DATA_DIR / "sessions.json"

class SessionStore:
    """
    Server-side session store.
    In production, this would be replaced by Redis.
    """
    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        if not SESSIONS_FILE.exists():
            with open(SESSIONS_FILE, "w") as f:
                json.dump({}, f)

    def _load(self) -> Dict[str, Any]:
        with open(SESSIONS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def _save(self, data: Dict[str, Any]):
        with open(SESSIONS_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def create_session(self, user_id: str, org_id: str, user_agent: str, ip: str) -> str:
        token = secrets.token_urlsafe(32)
        sessions = self._load()
        sessions[token] = {
            "user_id": user_id,
            "org_id": org_id,
            "created_at": time.time(),
            "last_seen": time.time(),
            "ua_hash": hash(user_agent),
            "ip": ip
        }
        self._save(sessions)
        return token

    def get_session(self, token: str) -> Optional[Dict[str, Any]]:
        sessions = self._load()
        session = sessions.get(token)
        if not session:
            return None

        # Check TTL (7 days)
        if time.time() - session["last_seen"] > 86400 * 7:
            self.delete_session(token)
            return None

        return session

    def touch_session(self, token: str):
        sessions = self._load()
        if token in sessions:
            sessions[token]["last_seen"] = time.time()
            self._save(sessions)

    def delete_session(self, token: str):
        sessions = self._load()
        if token in sessions:
            del sessions[token]
            self._save(sessions)

    def delete_all_user_sessions(self, user_id: str):
        sessions = self._load()
        to_delete = [t for t, s in sessions.items() if s["user_id"] == user_id]
        for t in to_delete:
            del sessions[t]
        self._save(sessions)

# Global session store instance
session_store = SessionStore()
