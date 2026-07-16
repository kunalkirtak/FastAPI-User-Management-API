"""
End-to-end HTTP tests, exercised through `TestClient` exactly the way a real
client would call this API -- routing, validation, serialization, middleware,
and exception handlers all included. See test_users.py for lower-level
service/CRUD unit tests.
"""


# ------------------------------------------------------------------------------------
# Root / health
# ------------------------------------------------------------------------------------
def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "message" in body
    assert body["docs"] == "/docs"


def test_health_check_reports_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"


def test_swagger_docs_are_served(client):
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


# ------------------------------------------------------------------------------------
# Observability (request-id middleware)
# ------------------------------------------------------------------------------------
def test_response_includes_request_id_and_timing_headers(client):
    response = client.get("/health")
    assert "X-Request-ID" in response.headers
    assert "X-Process-Time-Ms" in response.headers


def test_client_supplied_request_id_is_echoed_back(client):
    response = client.get("/health", headers={"X-Request-ID": "abc-123"})
    assert response.headers["X-Request-ID"] == "abc-123"


# ------------------------------------------------------------------------------------
# POST /api/v1/users (create)
# ------------------------------------------------------------------------------------
def test_create_user_returns_201_and_never_leaks_the_password(client, sample_user_payload):
    response = client.post("/api/v1/users", json=sample_user_payload)
    assert response.status_code == 201

    body = response.json()
    assert body["username"] == sample_user_payload["username"]
    assert body["email"] == sample_user_payload["email"]
    assert "password" not in body
    assert "hashed_password" not in body
    assert body["is_active"] is True


def test_create_user_duplicate_email_returns_409(client, sample_user_payload):
    client.post("/api/v1/users", json=sample_user_payload)

    duplicate = {**sample_user_payload, "username": "different_username"}
    response = client.post("/api/v1/users", json=duplicate)
    assert response.status_code == 409


def test_create_user_duplicate_username_returns_409(client, sample_user_payload):
    client.post("/api/v1/users", json=sample_user_payload)

    duplicate = {**sample_user_payload, "email": "different@example.com"}
    response = client.post("/api/v1/users", json=duplicate)
    assert response.status_code == 409


def test_create_user_weak_password_returns_422(client, sample_user_payload):
    payload = {**sample_user_payload, "password": "weak"}
    response = client.post("/api/v1/users", json=payload)
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], list)


def test_create_user_invalid_username_returns_422(client, sample_user_payload):
    payload = {**sample_user_payload, "username": "bad username!"}
    response = client.post("/api/v1/users", json=payload)
    assert response.status_code == 422


def test_create_user_invalid_email_returns_422(client, sample_user_payload):
    payload = {**sample_user_payload, "email": "not-an-email"}
    response = client.post("/api/v1/users", json=payload)
    assert response.status_code == 422


def test_create_user_missing_required_field_returns_422(client, sample_user_payload):
    payload = {k: v for k, v in sample_user_payload.items() if k != "email"}
    response = client.post("/api/v1/users", json=payload)
    assert response.status_code == 422


# ------------------------------------------------------------------------------------
# GET /api/v1/users/{id} and GET /api/v1/users
# ------------------------------------------------------------------------------------
def test_get_user_by_id(client, sample_user_payload):
    created = client.post("/api/v1/users", json=sample_user_payload).json()

    response = client.get(f"/api/v1/users/{created['id']}")
    assert response.status_code == 200
    assert response.json()["email"] == sample_user_payload["email"]


def test_get_missing_user_returns_404(client):
    response = client.get("/api/v1/users/9999")
    assert response.status_code == 404
    assert response.json() == {"detail": "User with id 9999 not found"}


def test_list_users_returns_everything_created(client, sample_user_payload):
    client.post("/api/v1/users", json=sample_user_payload)
    second = {**sample_user_payload, "username": "second_user", "email": "second@example.com"}
    client.post("/api/v1/users", json=second)

    response = client.get("/api/v1/users")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_users_pagination(client, sample_user_payload):
    for i in range(5):
        payload = {**sample_user_payload, "username": f"user{i}", "email": f"user{i}@example.com"}
        client.post("/api/v1/users", json=payload)

    response = client.get("/api/v1/users", params={"skip": 0, "limit": 2})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_users_empty_by_default(client):
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    assert response.json() == []


# ------------------------------------------------------------------------------------
# PUT /api/v1/users/{id}
# ------------------------------------------------------------------------------------
def test_update_user_partial_update(client, sample_user_payload):
    created = client.post("/api/v1/users", json=sample_user_payload).json()

    response = client.put(f"/api/v1/users/{created['id']}", json={"full_name": "Updated Name"})
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"
    assert response.json()["email"] == sample_user_payload["email"]


def test_update_missing_user_returns_404(client):
    response = client.put("/api/v1/users/9999", json={"full_name": "Ghost"})
    assert response.status_code == 404


def test_update_user_weak_password_returns_422(client, sample_user_payload):
    created = client.post("/api/v1/users", json=sample_user_payload).json()

    response = client.put(f"/api/v1/users/{created['id']}", json={"password": "weak"})
    assert response.status_code == 422


# ------------------------------------------------------------------------------------
# DELETE /api/v1/users/{id}
# ------------------------------------------------------------------------------------
def test_delete_user_returns_204_and_removes_it(client, sample_user_payload):
    created = client.post("/api/v1/users", json=sample_user_payload).json()

    response = client.delete(f"/api/v1/users/{created['id']}")
    assert response.status_code == 204

    follow_up = client.get(f"/api/v1/users/{created['id']}")
    assert follow_up.status_code == 404


def test_delete_missing_user_returns_404(client):
    response = client.delete("/api/v1/users/9999")
    assert response.status_code == 404
