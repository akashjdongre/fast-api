from sqlalchemy import Column, Integer, Float, ForeignKey, Enum, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class OrderStatus(str, enum.Enum):
    pending   = "pending"
    confirmed = "confirmed"
    shipped   = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity   = Column(Integer, default=1)
    total      = Column(Float, nullable=False)
    status     = Column(Enum(OrderStatus, native_enum=False), default=OrderStatus.pending)
    created_at = Column(DateTime, server_default=func.now())

    user    = relationship("User")
    product = relationship("Product")