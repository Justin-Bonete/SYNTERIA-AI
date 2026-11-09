import os
import tempfile

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"
os.environ["FRONTEND_DIR"] = "/nonexistent"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

user = {"name": "Owner", "email": "Owner@Example.com", "password": "correct-horse-battery"}


def test_full_auth_flow():
    with TestClient(app) as c:
        assert c.get("/api/v1/health").json()["status"] == "ok"
        assert c.get("/api/v1/auth/me").status_code == 401

        r = c.post("/api/v1/auth/register", json=user)
        assert r.status_code == 201 and r.json()["user"]["is_owner"] is True

        # registration closes after the owner exists
        other = {**user, "email": "x@example.com"}
        assert c.post("/api/v1/auth/register", json=other).status_code == 403

        assert c.post("/api/v1/auth/login", json={"email": user["email"], "password": "wrong-pass"}).status_code == 401
        r = c.post("/api/v1/auth/login", json={"email": "owner@example.com", "password": user["password"]})
        assert r.status_code == 200
        token = r.json()["token"]
        me = c.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me.status_code == 200 and me.json()["email"] == "owner@example.com"
        assert c.get("/api/v1/auth/me", headers={"Authorization": "Bearer garbage"}).status_code == 401
