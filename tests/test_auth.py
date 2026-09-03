from tests.conftest import register_user, login_user


def test_register_new_user(client):
    resp = register_user(client, "Alice", "alice@example.com", "password123", "student")
    assert resp.status_code == 200
    assert b"Registration successful" in resp.data


def test_register_duplicate_email_fails(client):
    register_user(client, "Alice", "alice@example.com", "password123", "student")
    resp = register_user(client, "Alice2", "alice@example.com", "password456", "student")
    assert b"already exists" in resp.data


def test_login_success(client):
    register_user(client, "Bob", "bob@example.com", "mypassword", "instructor")
    resp = login_user(client, "bob@example.com", "mypassword")
    assert b"Welcome back" in resp.data


def test_login_invalid_credentials(client):
    register_user(client, "Carl", "carl@example.com", "correctpass", "student")
    resp = login_user(client, "carl@example.com", "wrongpass")
    assert b"Invalid email or password" in resp.data


def test_logout_clears_session(client):
    register_user(client, "Dana", "dana@example.com", "password123", "student")
    login_user(client, "dana@example.com", "password123")
    resp = client.get("/logout", follow_redirects=True)
    assert b"logged out" in resp.data


def test_rbac_student_cannot_access_admin_dashboard(client):
    register_user(client, "Eve", "eve@example.com", "password123", "student")
    login_user(client, "eve@example.com", "password123")
    resp = client.get("/admin/dashboard", follow_redirects=True)
    assert b"do not have permission" in resp.data


def test_rbac_admin_can_access_admin_dashboard(client):
    register_user(client, "Frank", "frank@example.com", "password123", "admin")
    login_user(client, "frank@example.com", "password123")
    resp = client.get("/admin/dashboard")
    assert resp.status_code == 200


def test_api_login_returns_jwt(client):
    reg_resp = register_user(client, "Gina", "gina@example.com", "password123", "instructor")
    assert reg_resp.status_code == 200
    resp = client.post("/api/auth/login", json={"email": "gina@example.com", "password": "password123"})
    assert resp.status_code == 200
    assert "token" in resp.get_json()
