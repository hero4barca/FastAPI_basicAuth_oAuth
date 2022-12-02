import pytest
from fastapi.testclient import TestClient
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from .main import app, get_db
from .models import Base
# from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'sqlite:///test_db.db'

engine = sa.create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Set up the database once
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# These two event listeners are only needed for sqlite for proper
# SAVEPOINT / nested transaction support. Other databases like postgres
# don't need them. 
# From: https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl
@sa.event.listens_for(engine, "connect")
def do_connect(dbapi_connection, connection_record):
    # disable pysqlite's emitting of the BEGIN statement entirely.
    # also stops it from emitting COMMIT before any DDL.
    dbapi_connection.isolation_level = None

@sa.event.listens_for(engine, "begin")
def do_begin(conn):
    # emit our own BEGIN
    conn.exec_driver_sql("BEGIN")


# This fixture is the main difference to before. It creates a nested
# transaction, recreates it when the application code calls session.commit
# and rolls it back at the end.
# Based on: https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
@pytest.fixture()
def session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Begin a nested transaction (using SAVEPOINT).
    nested = connection.begin_nested()

    # If the application code calls session.commit, it will end the nested
    # transaction. Need to start a new one when that happens.
    @sa.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    # Rollback the overall transaction, restoring the state before the test ran.
    session.close()
    transaction.rollback()
    connection.close()

# A fixture for the fastapi test client which depends on the
# previous session fixture. Instead of creating a new session in the
# dependency override as before, it uses the one provided by the
# session fixture.
@pytest.fixture()
def client(session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


def test_api_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Todo api root"


class TestClassSignup:   
           
    def test_missing_lname_input_returns_error(self, client):
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


    def test_missing_fname_input_returns_error(self,client):
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


    def test_missing_email_input_returns_error(self,client):
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


    def test_complete(self,client):
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
        json_response = response.json()
        assert json_response['lname'] == payload['lname']
        assert json_response['fname'] == payload['fname']
        assert json_response['email'] == payload['email']
       


    
        

