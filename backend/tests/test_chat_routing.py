import pytest
from backend.tests.factories import create_org, create_user, create_case, upload_test_doc

def test_greeting_routing(client):
    # Setup
    org = create_org()
    user = create_user(org.org_id, email="greeting@test.com")

    client.post("/api/v1/auth/login", json={"email": user.email, "password": "Password123!"})

    # Test greeting -> fast path
    res = client.post("/api/v1/chat", json={
        "case_id": "any", # Should not matter for greeting
        "message": "Hi there!"
    })
    assert res.status_code == 200
    assert res.json()["path"] == "fast"
    assert res.json()["findings"] == []

def test_document_routing(client):
    # Setup
    org = create_org()
    user = create_user(org.org_id, email="doc@test.com")
    case = create_case(org.org_id)
    upload_test_doc(case.case_id, content="The total amount is 5000 USD")

    client.post("/api/v1/auth/login", json={"email": user.email, "password": "Password123!"})

    # Test query -> document path
    res = client.post("/api/v1/chat", json={
        "case_id": case.case_id,
        "message": "What is the total amount?"
    })
    assert res.status_code == 200
    assert res.json()["path"] == "document"

def test_empty_case_integrity(client):
    # Setup
    org = create_org()
    user = create_user(org.org_id, email="empty@test.com")
    case = create_case(org.org_id) # No docs uploaded

    client.post("/api/v1/auth/login", json={"email": user.email, "password": "Password123!"})

    # Test query on empty case -> integrity engine returns []
    res = client.post("/api/v1/chat", json={
        "case_id": case.case_id,
        "message": "Are there any discrepancies?"
    })
    assert res.status_code == 200
    # Based on prompt, integrity engine should return nothing if no docs
    assert res.json()["findings"] == []
