
# These are Pytest test cases for the Authentication API (/auth/register and /auth/login).

# The purpose of these tests is to verify that:

# ✅ A new user can register.
# ✅ Duplicate emails are rejected.
# ✅ Login works with correct credentials.
# ✅ Login fails with incorrect password.
# ✅ Login fails if the user doesn't exist.

# Let's go through each line with examples.

import io

def test_register_success(client):
    response = client.post("/auth/register", params={
        "name": "Akash", "email": "akash@test.com", "password": "pass123"
    })
    assert response.status_code == 201
    assert response.json()["message"] == "User created"


def test_register_duplicate_email(client):
    # Register once
    client.post("/auth/register", params={
        "name": "Akash", "email": "akash@test.com", "password": "pass123"
    })
    # Register again with same email
    response = client.post("/auth/register", params={
        "name": "Akash", "email": "akash@test.com", "password": "pass123"
    })
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(client):
    client.post("/auth/register", params={
        "name": "Akash", "email": "akash@test.com", "password": "pass123"
    })
    response = client.post("/auth/login", data={
        "username": "akash@test.com", "password": "pass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/auth/register", params={
        "name": "Akash", "email": "akash@test.com", "password": "pass123"
    })
    response = client.post("/auth/login", data={
        "username": "akash@test.com", "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]


def test_login_nonexistent_user(client):
    response = client.post("/auth/login", data={
        "username": "nobody@test.com", "password": "pass123"
    })
    assert response.status_code == 401