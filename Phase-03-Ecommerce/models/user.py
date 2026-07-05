from sqlalchemy import Column, Integer, String, Boolean, Enum
from database import Base
import enum

class UserRole(str, enum.Enum):
    admin    = "admin"
    customer = "customer"

class User(Base):
    __tablename__ = "users"

    id        = Column(Integer, primary_key=True, index=True)
    email     = Column(String(255), unique=True, index=True, nullable=False)
    name      = Column(String(100), nullable=False)
    password  = Column(String(255), nullable=False)
    role      = Column(Enum(UserRole, native_enum=False), default=UserRole.customer)
    is_active = Column(Boolean, default=True)