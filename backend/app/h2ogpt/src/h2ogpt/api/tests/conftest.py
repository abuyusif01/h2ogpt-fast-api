import pytest
from httpx import Client
from auth.app.core.session import async_session
from auth.app.core import security
from auth.app.api.api import api_router as auth_api_router

default_user_email = "dev-pytest@test.com"
default_user_password = "string"
first_first_name = "pytest"
first_last_name = "pytest"
first_mobile = "1234567890"
default_user_password_hash = security.get_password_hash(default_user_password)


# client object
@pytest.fixture(scope="session")
def client():
    with Client(
        follow_redirects=True,
        base_url="https://localhost:8000",
        verify=False,
    ) as client:
        client.headers.update({"Host": "internal_testing_localhost"})
        yield client


# log user in
@pytest.fixture(scope="session")
def user_auth_header(client: Client):

    response = client.post(
        auth_api_router.url_path_for("login_access_token"),
        data={
            "username": default_user_email,
            "password": default_user_password,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if response.status_code != 200:
        response = client.post(
            auth_api_router.url_path_for("login_access_token"),
            data={
                "username": default_user_email,
                "password": "testxxxxxx",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


# create new user
@pytest.fixture(scope="session")
def create_pytest_user(client: Client):
    response = client.post(
        auth_api_router.url_path_for("register_new_user"),
        json={
            "email": default_user_email,
            "password": default_user_password,
            "first_name": first_first_name,
            "last_name": first_last_name,
            "mobile": first_mobile,
        },
    )
    assert (
        response.status_code == 200
        or response.json()["detail"] == "Cannot use this email address"
    )


# delete current user
@pytest.fixture(scope="session")
def delete_pytest_user(client: Client, user_auth_header):
    response = client.delete("/api/v1/auth/me", headers=user_auth_header)
    assert response.status_code == 204
    return response


# current user
@pytest.fixture(scope="session")
def current_user(client: Client, user_auth_header):
    response = client.get(
        auth_api_router.url_path_for("read_current_user"),
        headers=user_auth_header,
    )
    assert response.status_code == 200
    return response.json()

