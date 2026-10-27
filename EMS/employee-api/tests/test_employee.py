import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test_employee.db"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


sample_employee = {
    "name": "Dhinesha G",
    "email": "dhinesha@example.com",
    "department": "Engineering",
    "role": "Backend Developer",
    "salary": 75000.0,
}

class TestHealthCheck:

    def test_health_check(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestCreateEmployee:

    def test_create_employee_success(self):
        response = client.post("/api/v1/employees/", json=sample_employee)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Dhinesha G"
        assert data["email"] == "dhinesha@example.com"
        assert "id" in data  

    def test_create_employee_duplicate_email(self):
        client.post("/api/v1/employees/", json=sample_employee)
        response = client.post("/api/v1/employees/", json=sample_employee)
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_employee_missing_fields(self):
        response = client.post("/api/v1/employees/", json={"name": "Test"})
        assert response.status_code == 422 


class TestGetEmployees:

    def test_get_all_employees_empty(self):
        response = client.get("/api/v1/employees/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_employees(self):
        client.post("/api/v1/employees/", json=sample_employee)
        response = client.get("/api/v1/employees/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_employee_by_id(self):
        create_response = client.post("/api/v1/employees/", json=sample_employee)
        employee_id = create_response.json()["id"]

        response = client.get(f"/api/v1/employees/{employee_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Dhinesha G"

    def test_get_employee_not_found(self):
        response = client.get("/api/v1/employees/999")
        assert response.status_code == 404


class TestUpdateEmployee:

    def test_update_employee_success(self):
        create_response = client.post("/api/v1/employees/", json=sample_employee)
        employee_id = create_response.json()["id"]

        update_data = {"name": "Dhinesha Updated", "salary": 85000.0}
        response = client.put(f"/api/v1/employees/{employee_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["name"] == "Dhinesha Updated"
        assert response.json()["salary"] == 85000.0

    def test_update_employee_not_found(self):
        response = client.put("/api/v1/employees/999", json={"name": "Ghost"})
        assert response.status_code == 404


class TestDeleteEmployee:

    def test_delete_employee_success(self):
        create_response = client.post("/api/v1/employees/", json=sample_employee)
        employee_id = create_response.json()["id"]

        response = client.delete(f"/api/v1/employees/{employee_id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

        get_response = client.get(f"/api/v1/employees/{employee_id}")
        assert get_response.status_code == 404

    def test_delete_employee_not_found(self):
        response = client.delete("/api/v1/employees/999")
        assert response.status_code == 404
