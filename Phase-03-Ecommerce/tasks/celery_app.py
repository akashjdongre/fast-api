from celery import Celery
from config import settings
import time
import ssl
import smtplib
from email.message import EmailMessage

redis_url = settings.REDIS_URL

celery_app = Celery(
    "ecommerce",                    # name of your Celery application.
    broker=redis_url,               # The broker is that waiter who carries the order to Chef
    backend=redis_url               # 
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC"
)

@celery_app.task(
    name="send_order_confirmation",
    bind=True,              # gives access to `self` (the task instance)
    max_retries=3,          # retry up to 3 times
    default_retry_delay=60  # wait 60 seconds between retries 
    )
def send_order_confirmation(self, email: str, order_id: int, total: float):
    msg = EmailMessage()
    msg["Subject"] = f"Order #{order_id} Confirmed"
    msg["From"] = f"Ecommerce Store <{settings.MAIL_FROM_ADDRESS}>"
    msg["To"] = "akashjdongre@gmail.com"  # email
    msg.set_content(f"Your order #{order_id} is confirmed. Total: ₹{total:.2f}")

    port = int(settings.MAIL_PORT)
    if port == 465:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(settings.MAIL_HOST, port, context=context) as smtp:
            smtp.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            smtp.send_message(msg)
    else:
        context = ssl.create_default_context()
        with smtplib.SMTP(settings.MAIL_HOST, port) as smtp:
            smtp.starttls(context=context)
            smtp.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            smtp.send_message(msg)

    return {"status": "sent"}

    # def send_order_confirmation(email: str, order_id: int, total: float):
    #     time.sleep(2)
    #     print(f"📧 Email sent to {email}: Order #{order_id} confirmed. ₹{total:.2f}")
    #     return {"status": "sent", "email": email}

@celery_app.task(name="process_refund")
def process_refund(order_id: int, amount: float):
    time.sleep(3)
    print(f"💰 Refund of ₹{amount:.2f} for Order #{order_id}")
    return {"status": "refunded"}