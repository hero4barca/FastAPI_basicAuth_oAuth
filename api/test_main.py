from .conf_test import client, session
from requests.auth import HTTPBasicAuth 
from requests.structures import CaseInsensitiveDict

def test_api_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Todo api root"


class TestSignup:   
           
    def test_missing_lname_input_returns_error(self, client):
        payload = {
            "fname": "test_fname",
            "password": "password",
            "email": 'test_email@example.com'
        }
        response = client.post("/api/users", json=payload)
        assert response.status_code == 422
        response_detail = response.json()['detail']
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
        response = client.post("/api/users",json=payload )
        assert response.status_code == 200
        json_response = response.json()
        assert json_response['lname'] == payload['lname']
        assert json_response['fname'] == payload['fname']
        assert json_response['email'] == payload['email']
       

class TestUserMe:
    
    def setup_class(self):
        self.payload = {
            "fname": "test_fname",
            "lname": "test_lname",
            "password": "password",
            "email": 'test_email@example.com'
        }

    def test_unauthenticated_request_returns_error(self, client):
        response = client.get('/users/me')
        assert response.status_code == 401
    
    def test_authenticated_request_returns_username(self, client):
        signup_response = client.post("/api/users",json=self.payload )
        assert signup_response.status_code == 200

        response = client.get('/users/me',  auth = HTTPBasicAuth( self.payload['email'], self.payload['password']) )
        response.status_code == 200
        assert response.json()['username'] == self.payload['email']


class TestOauthUserMe:
    def setup_class(self):
        self.payload = {
            "fname": "test_fname",
            "lname": "test_lname",
            "password": "password",
            "email": 'test_email@example.com'
        }

    def get_oauth_token(self, client):
        token_response = client.post('/token', data={"username": self.payload['email'],
                                                    "password": self.payload['password'] })
        return token_response

    def test_unauthenticated_request_returns_error(self, client):
        response = client.get('/users/oauth_me')
        assert response.status_code == 401

    def test_authenticated_request_returns_user(self, client):
        signup_response = client.post("/api/users",json=self.payload )
        assert signup_response.status_code == 200

        token_response = self.get_oauth_token(client=client)
        oauth_token = token_response.json()['access_token']

        headers = CaseInsensitiveDict()
        headers["Accept"] = "application/json"
        headers["Authorization"] = "Bearer {}".format(oauth_token)  

        response = client.get('/users/oauth_me', headers=headers)
        assert response.status_code == 200



        


