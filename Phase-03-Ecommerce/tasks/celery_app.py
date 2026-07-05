from celery import Celery
from config import settings
import time

celery_app = Celery(
    "ecommerce",                    # name of your Celery application.
    broker=settings.REDIS_URL,      # The broker is that waiter who carries the order to Chef
    backend=settings.REDIS_URL      # 
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC"
)

@celery_app.task(name="send_order_confirmation")
def send_order_confirmation(email: str, order_id: int, total: float):
    time.sleep(2)
    print(f"📧 Email sent to {email}: Order #{order_id} confirmed. ₹{total:.2f}")
    return {"status": "sent", "email": email}

@celery_app.task(name="process_refund")
def process_refund(order_id: int, amount: float):
    time.sleep(3)
    print(f"💰 Refund of ₹{amount:.2f} for Order #{order_id}")
    return {"status": "refunded"}