from .test_config import client, session

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
        response = client.post("/api/users",json=payload )
        assert response.status_code == 200
        json_response = response.json()
        assert json_response['lname'] == payload['lname']
        assert json_response['fname'] == payload['fname']
        assert json_response['email'] == payload['email']
       


    
        

