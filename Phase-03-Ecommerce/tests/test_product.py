import io

def test_list_products_empty(client):
    response = client.get("/products/")
    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["results"] == []


def test_create_product_as_admin(client, admin_token):
    response = client.post(
        "/products/",
        params={"name": "iPhone", "description": "Apple phone", "price": 79999, "stock": 10},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "iPhone"
    assert response.json()["price"] == 79999


def test_create_product_as_customer_forbidden(client, customer_token):
    response = client.post(
        "/products/",
        params={"name": "iPhone", "description": "Apple phone", "price": 79999, "stock": 10},
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    # Customer cannot create products
    assert response.status_code == 403
    assert "Admin access required" in response.json()["detail"]


def test_create_product_unauthenticated(client):
    response = client.post(
        "/products/",
        params={"name": "iPhone", "description": "Apple phone", "price": 79999, "stock": 10}
    )
    assert response.status_code == 401


def test_get_product_not_found(client):
    response = client.get("/products/999")
    assert response.status_code == 404


def test_product_pagination(client, admin_token):
    # Create 3 products
    for i in range(3):
        client.post(
            "/products/",
            params={"name": f"Product {i}", "description": "desc", "price": 100, "stock": 5},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

    # Page 1 with limit 2
    response = client.get("/products/?page=1&limit=2")
    assert response.status_code == 200
    assert response.json()["total"] == 3
    assert len(response.json()["results"]) == 2


def test_product_search(client, admin_token):
    client.post("/products/", params={"name": "iPhone", "description": "Apple", "price": 79999, "stock": 5},
                headers={"Authorization": f"Bearer {admin_token}"})
    client.post("/products/", params={"name": "Samsung", "description": "Android", "price": 59999, "stock": 5},
                headers={"Authorization": f"Bearer {admin_token}"})

    response = client.get("/products/?search=iPhone")
    assert response.json()["total"] == 1
    assert response.json()["results"][0]["name"] == "iPhone"


def test_upload_invalid_file_type(client, admin_token):
    fake_pdf = io.BytesIO(b"fake pdf content")
    response = client.post(
        "/products/",
        params={"name": "iPhone", "description": "desc", "price": 999, "stock": 5},
        files={"image": ("test.pdf", fake_pdf, "application/pdf")},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400
    assert "JPEG/PNG/WebP" in response.json()["detail"]