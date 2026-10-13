import pytest
import os
from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.core import repository

@pytest.fixture(scope="session")
def data_dir(tmp_path_factory):
    """Creates a temporary directory for JSON data storage."""
    temp_dir = tmp_path_factory.mktemp("data")

    # Initialize empty JSON files to prevent FileNotFound errors
    files = [
        "users.json", "orgs.json", "cases.json",
        "docs.json", "notifications.json",
        "conversations.json", "messages.json"
    ]
    for f in files:
        with open(temp_dir / f, "w") as file:
            file.write("{}")

    return temp_dir

@pytest.fixture(scope="session", autouse=True)
def setup_test_env(data_dir):
    """Overrides the application's DATA_DIR to use the temporary path."""
    # Set environment variable before any repository instances are used
    os.environ["TRADE_DATA_DIR"] = str(data_dir)

    # Monkeypatch the DATA_DIR in the repository module
    repository.DATA_DIR = data_dir

    # Force re-initialization of global repository paths
    # BaseRepository._load and _save use self.path,
    # but global instances were created at import time.
    # We must update the path of all existing global repositories.
    repos = [
        repository.users, repository.orgs, repository.cases,
        repository.docs, repository.notifications,
        repository.conversations, repository.messages
    ]
    for repo in repos:
        repo.path = data_dir / repo.path.name

@pytest.fixture
def client(setup_test_env):
    """FastAPI TestClient fixture."""
    return TestClient(app)
