import pytest
from backend.tests.factories import create_org, create_user, create_case, upload_test_doc

def test_happy_path_flow(client):
    # 1. Register
    reg_payload = {
        "email": "founder@test.com",
        "password": "Password123!",
        "first_name": "Founder",
        "last_name": "User",
        "org_name": "Global Trade Corp"
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201

    # Auth route returns {"message": "...", "user_id": "..."}
    user_id = reg_res.json()["user_id"]

    # 2. Login
    login_payload = {
        "email": "founder@test.com",
        "password": "Password123!"
    }
    login_res = client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200

    # 3. Create Case
    case_payload = {
        "title": "Import-Export-2026-Q3",
        "product": "Industrial Valves",
        "origin": {"country": "India"},
        "destination": {"country": "USA"}
    }
    case_res = client.post("/api/v1/cases", json=case_payload)
    assert case_res.status_code == 201
    case_id = case_res.json()["id"]

    # 4. Upload Document
    # Note: Using multipart/form-data for real API upload
    files = {"file": ("invoice.pdf", b"fake pdf content", "application/pdf")}
    data = {"case_id": case_id}
    doc_res = client.post("/api/v1/documents/upload", files=files, data=data)
    assert doc_res.status_code == 201
    doc_id = doc_res.json()["id"]

    # 5. Chat with Case
    chat_payload = {
        "case_id": case_id,
        "message": "What is the total amount on the invoice?"
    }
    chat_res = client.post("/api/v1/chat", json=chat_payload)
    assert chat_res.status_code == 200
    assert "reply" in chat_res.json()

    # 6. Delete Case (Cleanup)
    del_res = client.delete(f"/api/v1/cases/{case_id}")
    assert del_res.status_code == 204
