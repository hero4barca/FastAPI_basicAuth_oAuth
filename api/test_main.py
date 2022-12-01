import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .main import app, get_db
from .models import Base
# from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'sqlite:///test_db.db'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture()
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)

def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Todo api root"

# def test_complete(test_db):
#         payload = {
#             "fname": "test_fname",
#             "lname": "test_lname",
#             "password": "password",
#             "email": 'test_email@example.com'
#         }
#         response = client.post("/api/users",
#                                      json=payload,  
#                                      )
#         assert response.status_code == 200

class TestClassSignup:
    
           
    def test_missing_lname_input_returns_error(self):
        payload = {
            "fname": "test_fname",
            "password": "password",
            "email": 'test_email@example.com'
        }
        response = client.post("/api/users", json=payload)
        assert response.status_code == 422
        response_detail = response.json()['detail']
        # print(response_detail)
        assert response_detail[0]['msg'] == "field required"
        assert response_detail[0]['type'] == "value_error.missing"
        assert response_detail[0]['loc'] == ["body","lname"]


    def test_missing_fname_input_returns_error(self):
        payload = {
            "lname": "test_lname",
            "password": "password",
            "email": 'test_email@example.com'
        }
        response = client.post("/api/users", json=payload)
        assert response.status_code == 422
        response_detail = response.json()['detail']
        assert response_detail[0]['msg'] == "field required"
        assert response_detail[0]['type'] == "value_error.missing"
        assert response_detail[0]['loc'] == ["body","fname"]


    def test_missing_email_input_returns_error(self):
        payload = {
            "lname": "test_lname",
            "fname": "test_fname",
            "password": "password",
            
        }
        response = client.post("/api/users", json=payload)
        assert response.status_code == 422
        response_detail = response.json()['detail']
        assert response_detail[0]['msg'] == "field required"
        assert response_detail[0]['type'] == "value_error.missing"
        assert response_detail[0]['loc'] == ["body","email"]

    @pytest.mark.usefixtures("test_db")
    def test_complete(self):
        payload = {
            "fname": "test_fname",
            "lname": "test_lname",
            "password": "password",
            "email": 'test_email@example.com'
        }
        response = client.post("/api/users",
                                     json=payload,  
                                     )
        assert response.status_code == 200
       


    
        

