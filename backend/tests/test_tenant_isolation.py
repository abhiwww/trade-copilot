import pytest
from backend.tests.factories import create_org, create_user, create_case, upload_test_doc

def test_tenant_isolation(client):
    # 1. Setup Org A and Org B
    org_a = create_org("Org A")
    org_b = create_org("Org B")

    user_a = create_user(org_a.org_id, email="user_a@test.com")
    user_b = create_user(org_b.org_id, email="user_b@test.com")

    # Create a case in Org B
    case_b = create_case(org_b.org_id, title="Org B Secret Case")

    # 2. Login as User A
    login_res = client.post("/api/v1/auth/login", json={
        "email": user_a.email,
        "password": "Password123!"
    })
    assert login_res.status_code == 200

    # 3. Attempt to access Org B's case
    res = client.get(f"/api/v1/cases/{case_b.case_id}")
    # Requirement: Cross-org access returns 404 (not 403)
    assert res.status_code == 404

    # 4. Attempt to access Org B's document
    doc_b = upload_test_doc(case_b.case_id, filename="secret.pdf")
    res_doc = client.get(f"/api/v1/documents/{doc_b.document_id}")
    assert res_doc.status_code == 404
