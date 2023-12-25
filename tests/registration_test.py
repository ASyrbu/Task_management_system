from modules import api_url, registration_credentials, urls
import requests


def test_registration():
    print(f"Registration ", end="")
    response = requests.post(
        api_url(urls["REGISTRATION"]),
        json=registration_credentials
    )

    j_response = response.json()
    j_keys = j_response.keys()

    if response.status_code != 200:
        print(f"[BAD]: Missing expected keys in response: {j_response}")

    token = j_response.get("token")
    session_id = j_response.get("session_id")
    user_id = j_response.get("user_id")

    assert response.status_code == 200
    assert len(j_keys) == 1

    print(f"[OK]:  {j_response}")

    return token, session_id, user_id
