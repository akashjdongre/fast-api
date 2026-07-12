from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.order import Order, OrderStatus
from models.product import Product
from models.user import User
from core.dependencies import get_current_user, require_admin
from core.redis import redis_client
from tasks.celery_app import send_order_confirmation
import json

router = APIRouter(prefix="/orders", tags=["Orders"])


# CREATE ORDER — triggers Celery email task
@router.post("/", status_code=201)
async def create_order(
    product_id: int,
    quantity: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    total = product.price * quantity
    order = Order(
        user_id=current_user.id,
        product_id=product_id,
        quantity=quantity,
        total=total
    )

    # Deduct stock
    product.stock -= quantity

    db.add(order)
    db.commit()
    db.refresh(order)

    # ✉️ Fire-and-forget email via Celery (non-blocking)
    send_order_confirmation.delay(current_user.email, order.id, total)

    # Invalidate user's cached orders
    await redis_client.delete(f"orders:user:{current_user.id}")
    return order


# GET MY ORDERS — with Redis caching (60s TTL)
@router.get("/my")
async def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cache_key = f"orders:user:{current_user.id}"

    # 1. Try cache first
    cached = await redis_client.get(cache_key)
    if cached:
        return {"source": "cache", "orders": json.loads(cached)}

    # 2. Cache miss → query DB
    orders = db.query(Order).filter(Order.user_id == current_user.id).all()
    data   = [{"id": o.id, "product_id": o.product_id, "quantity": o.quantity,
               "total": o.total, "status": o.status} for o in orders]

    # 3. Store in Redis for 60s
    await redis_client.setex(cache_key, 60, json.dumps(data))

    return {"source": "db", "orders": data}


# ADMIN — update order status (triggers WebSocket broadcast)
@router.put("/{order_id}/status")
async def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = new_status
    db.commit()

    # 📡 Broadcast real-time update to connected WebSocket clients
    from routes.websocket import manager
    await manager.broadcast(json.dumps({
        "event":    "order_status_update",
        "order_id": order_id,
        "status":   new_status
    }))

    return {"message": f"Order {order_id} updated to {new_status}"}