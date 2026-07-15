import pytest       # write test cases | check expected results
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

#----- Fixtures is a way to provide a fixed baseline upon which tests can reliably and repeatedly execute. 
#----- Fixtures are used to set up the necessary preconditions for tests, such as creating test data, initializing resources, 
#----- or configuring the environment. They help ensure that tests run in a consistent and isolated manner, 
#----- making it easier to identify issues and maintain test reliability.


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test, drop after"""
    Base.metadata.create_all(bind=engine)
    yield # pauses the fixture and lets the test execute.
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


# This file builds a complete, isolated testing environment:
# create_engine() ---->  connects to a separate SQLite test database.
# TestingSessionLocal ----> creates database sessions for tests.
# override_get_db() ----> ensures FastAPI uses the test database instead of the production one.
# setup_db automatically creates tables before each test and removes them afterward.
# client provides a TestClient for making API requests without running a server.
# db provides a database session for inserting or querying test data.
# customer_token and admin_token create test users and return valid JWTs, allowing you to test 
# authenticated endpoints without calling the login API.