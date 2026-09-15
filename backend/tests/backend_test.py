"""UrbanisAI backend regression tests.
Covers: auth (login/register/me), catalog/regulations/suppliers, projects CRUD,
design compute totals, dashboard, and all six AI agents including data-gap flags.
"""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://housing-forge.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"

ADMIN_EMAIL = "admin@urbanis.ai"
ADMIN_PASSWORD = "urbanis2025"


@pytest.fixture(scope="session")
def admin_token():
    r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=20)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "token" in data and data["user"]["email"] == ADMIN_EMAIL
    return data["token"]


@pytest.fixture(scope="session")
def headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


# -------------------- Auth --------------------
class TestAuth:
    def test_login_success(self, admin_token):
        assert isinstance(admin_token, str) and len(admin_token) > 10

    def test_login_invalid(self):
        r = requests.post(f"{API}/auth/login", json={"email": ADMIN_EMAIL, "password": "wrong"}, timeout=20)
        assert r.status_code == 401

    def test_register_and_me(self):
        email = f"test_{uuid.uuid4().hex[:8]}@urbanis.ai"
        r = requests.post(f"{API}/auth/register", json={"name": "Test Planner", "email": email, "password": "pw12345!"}, timeout=20)
        assert r.status_code == 200, r.text
        token = r.json()["token"]
        r2 = requests.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {token}"}, timeout=20)
        assert r2.status_code == 200
        assert r2.json()["email"] == email

    def test_me_no_token(self):
        r = requests.get(f"{API}/auth/me", timeout=20)
        assert r.status_code == 401


# -------------------- Reference data --------------------
class TestReference:
    def test_catalog(self):
        r = requests.get(f"{API}/catalog", timeout=20)
        assert r.status_code == 200
        d = r.json()
        assert len(d["modules"]) >= 6 and len(d["materials"]) >= 6
        assert "benchmark_carbon" in d

    def test_regulations(self):
        r = requests.get(f"{API}/regulations", timeout=20)
        assert r.status_code == 200
        regs = r.json()
        assert any(x["code"] == "Municipal Bylaw MB-22.7" for x in regs)
        for r_ in regs:
            assert "level" in r_ and "date" in r_

    def test_suppliers(self):
        r = requests.get(f"{API}/suppliers", timeout=20)
        assert r.status_code == 200
        assert len(r.json()) >= 3

    def test_suppliers_filter(self):
        r = requests.get(f"{API}/suppliers", params={"material": "clt"}, timeout=20)
        assert r.status_code == 200
        for s in r.json():
            assert "clt" in s["materials"]

    def test_design_compute(self):
        payload = {"modules": [{"module_id": "bedroom", "material": "clt"}, {"module_id": "kitchen", "material": "clt"}]}
        r = requests.post(f"{API}/design/compute", json=payload, timeout=20)
        assert r.status_code == 200
        t = r.json()
        assert t["units"] == 2 and t["total_cost"] > 0 and t["floor_area"] > 0


# -------------------- Projects CRUD --------------------
class TestProjects:
    def test_full_crud_and_dashboard(self, headers):
        # Create
        payload = {"name": "TEST_Project_" + uuid.uuid4().hex[:6], "location": "Amsterdam, NL",
                   "description": "Modular pilot 20 units", "population": "60"}
        r = requests.post(f"{API}/projects", headers=headers, json=payload, timeout=20)
        assert r.status_code == 200, r.text
        proj = r.json()
        pid = proj["id"]
        assert proj["name"] == payload["name"] and "_id" not in proj

        # Read one
        r = requests.get(f"{API}/projects/{pid}", headers=headers, timeout=20)
        assert r.status_code == 200 and r.json()["id"] == pid

        # List
        r = requests.get(f"{API}/projects", headers=headers, timeout=20)
        assert r.status_code == 200
        assert any(p["id"] == pid for p in r.json())

        # Update design
        modules = [{"module_id": "bedroom", "material": "clt"},
                   {"module_id": "living", "material": "clt"}]
        r = requests.put(f"{API}/projects/{pid}", headers=headers,
                         json={"design": {"modules": modules}}, timeout=20)
        assert r.status_code == 200
        design = r.json()["design"]
        assert design["totals"]["units"] == 2 and design["totals"]["total_cost"] > 0

        # Dashboard
        r = requests.get(f"{API}/dashboard", headers=headers, timeout=20)
        assert r.status_code == 200 and r.json()["active"] >= 1

        # Delete
        r = requests.delete(f"{API}/projects/{pid}", headers=headers, timeout=20)
        assert r.status_code == 200

        # Verify gone
        r = requests.get(f"{API}/projects/{pid}", headers=headers, timeout=20)
        assert r.status_code == 404

    def test_projects_require_auth(self):
        r = requests.get(f"{API}/projects", timeout=20)
        assert r.status_code == 401


# -------------------- AI Agents --------------------
class TestAgents:
    @pytest.fixture(scope="class")
    def full_project(self, headers):
        payload = {"name": "TEST_Agents_" + uuid.uuid4().hex[:6], "location": "Amsterdam, NL",
                   "description": "Sustainable modular pilot on brownfield", "population": "80"}
        r = requests.post(f"{API}/projects", headers=headers, json=payload, timeout=20)
        pid = r.json()["id"]
        # approve site + add design
        modules = [{"module_id": "bedroom", "material": "clt"},
                   {"module_id": "kitchen", "material": "clt"},
                   {"module_id": "living", "material": "clt"}]
        requests.put(f"{API}/projects/{pid}", headers=headers,
                     json={"site": {"status": "approved", "polygon": None, "area_m2": 1200,
                                    "perimeter_m": 140, "veto_reason": None, "label": "Compliant Parcel"},
                           "design": {"modules": modules}}, timeout=20)
        yield pid
        requests.delete(f"{API}/projects/{pid}", headers=headers, timeout=20)

    @pytest.fixture(scope="class")
    def empty_project(self, headers):
        payload = {"name": "TEST_Empty_" + uuid.uuid4().hex[:6], "location": "", "description": "", "population": ""}
        r = requests.post(f"{API}/projects", headers=headers, json=payload, timeout=20)
        pid = r.json()["id"]
        yield pid
        requests.delete(f"{API}/projects/{pid}", headers=headers, timeout=20)

    def test_thot_llm(self, headers, full_project):
        r = requests.post(f"{API}/projects/{full_project}/agents/thot", headers=headers, timeout=60)
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "complete" and len(d["output"]) > 20

    def test_thot_gap(self, headers, empty_project):
        r = requests.post(f"{API}/projects/{empty_project}/agents/thot", headers=headers, timeout=30)
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "gap" and "institution" in d["gap"]

    def test_kael_approved(self, headers, full_project):
        r = requests.post(f"{API}/projects/{full_project}/agents/kael", headers=headers, timeout=30)
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "complete" and len(d["citations"]) > 0
        assert all("level" in c and "date" in c for c in d["citations"])

    def test_kael_gap_without_approval(self, headers, empty_project):
        r = requests.post(f"{API}/projects/{empty_project}/agents/kael", headers=headers, timeout=30)
        assert r.status_code == 200
        assert r.json()["status"] == "gap"

    def test_iris_llm(self, headers, full_project):
        r = requests.post(f"{API}/projects/{full_project}/agents/iris", headers=headers, timeout=60)
        assert r.status_code == 200
        assert r.json()["status"] == "complete"

    def test_iris_gap(self, headers, empty_project):
        r = requests.post(f"{API}/projects/{empty_project}/agents/iris", headers=headers, timeout=30)
        assert r.status_code == 200
        assert r.json()["status"] == "gap"

    def test_cronos(self, headers, full_project):
        r = requests.post(f"{API}/projects/{full_project}/agents/cronos", headers=headers, timeout=30)
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "complete" and d["totals"]["units"] == 3

    def test_terra(self, headers, full_project):
        r = requests.post(f"{API}/projects/{full_project}/agents/terra", headers=headers, timeout=30)
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "complete" and len(d["suppliers"]) > 0

    def test_lyra_after_all(self, headers, full_project):
        # Ensure all previous agents ran (idempotent)
        for a in ["thot", "kael", "iris", "cronos", "terra"]:
            requests.post(f"{API}/projects/{full_project}/agents/{a}", headers=headers, timeout=60)
        r = requests.post(f"{API}/projects/{full_project}/agents/lyra", headers=headers, timeout=60)
        assert r.status_code == 200
        assert r.json()["status"] == "complete"

    def test_lyra_gap_when_incomplete(self, headers, empty_project):
        r = requests.post(f"{API}/projects/{empty_project}/agents/lyra", headers=headers, timeout=30)
        assert r.status_code == 200
        assert r.json()["status"] == "gap"

    def test_unknown_agent(self, headers, full_project):
        r = requests.post(f"{API}/projects/{full_project}/agents/xxx", headers=headers, timeout=20)
        assert r.status_code == 400
