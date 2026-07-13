import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import Base, get_db
from core.auth import create_access_token
from models.user import User, UserRole
from core.auth import hash_password

# Use separate in-memory SQLite for tests — never touch real DB
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override get_db to use test DB
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def customer_token(db):
    """Create a customer user and return their JWT token"""
    user = User(
        name="Test Customer",
        email="customer@test.com",
        password=hash_password("password123"),
        role=UserRole.customer
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return create_access_token({"sub": str(user.id), "role": user.role})


@pytest.fixture
def admin_token(db):
    """Create an admin user and return their JWT token"""
    user = User(
        name="Test Admin",
        email="admin@test.com",
        password=hash_password("admin123"),
        role=UserRole.admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return create_access_token({"sub": str(user.id), "role": user.role})