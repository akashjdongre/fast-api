from unittest.mock import patch

def create_product_helper(client, admin_token, stock=10):
    res = client.post(
        "/products/",
        params={"name": "Test Product", "description": "desc", "price": 299.0, "stock": stock},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    return res.json()["id"]


def test_create_order_success(client, customer_token, admin_token):
    product_id = create_product_helper(client, admin_token)

    # Mock Celery task so email isn't actually sent during tests
    with patch("app.routes.orders.send_order_confirmation.delay") as mock_task:
        response = client.post(
            "/orders/",
            params={"product_id": product_id, "quantity": 2},
            headers={"Authorization": f"Bearer {customer_token}"}
        )

    assert response.status_code == 201
    assert response.json()["total"] == 598.0   # 299 * 2
    assert response.json()["status"] == "pending"
    mock_task.assert_called_once()   # verify Celery was triggered


def test_create_order_insufficient_stock(client, customer_token, admin_token):
    product_id = create_product_helper(client, admin_token, stock=1)

    with patch("app.routes.orders.send_order_confirmation.delay"):
        response = client.post(
            "/orders/",
            params={"product_id": product_id, "quantity": 5},  # more than stock
            headers={"Authorization": f"Bearer {customer_token}"}
        )

    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]


def test_create_order_product_not_found(client, customer_token):
    with patch("app.routes.orders.send_order_confirmation.delay"):
        response = client.post(
            "/orders/",
            params={"product_id": 999, "quantity": 1},
            headers={"Authorization": f"Bearer {customer_token}"}
        )
    assert response.status_code == 404


def test_create_order_unauthenticated(client, admin_token):
    product_id = create_product_helper(client, admin_token)
    response = client.post("/orders/", params={"product_id": product_id, "quantity": 1})
    assert response.status_code == 401