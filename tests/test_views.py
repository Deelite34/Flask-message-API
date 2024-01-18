import json

from flask import current_app, url_for
from sqlalchemy import select

from extensions import db
from models import User
from utils import make_simple_activation_template, make_uuid


def test_base_redirection(client):
    res = client.get("/")
    assert res.status_code == 302


def test_message_endpoint_authorization_required(app, client):
    get = client.get("/api/v1/message/")
    post = client.get("/api/v1/message/")
    put = client.get("/api/v1/message/")
    delete = client.get("/api/v1/message/")

    assert get.status_code == 401
    assert post.status_code == 401
    assert put.status_code == 401
    assert delete.status_code == 401


def test_message_endpoint_get_all(app, client, token):
    for _ in range(2):
        client.post(
            url_for("api.messageendpoint"),
            json={"title": f"title {_}", "content": f"content {_}"},
            headers={"Authorization": f"Bearer {token}"},
        )

    response = client.get(
        "/api/v1/message/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert len(response.json) == 2


def test_message_endpoint_get_specific(app, client, token):
    data = client.post(
        url_for("api.messageendpoint"),
        json={"title": "title 1", "content": "content 1"},
        headers={"Authorization": f"Bearer {token}"},
    )

    id = data.json["id"]

    response = client.get(
        f"/api/v1/message/{id}/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json["id"] == data.json["id"]
    assert response.json["title"] == data.json["title"]


def test_message_endpoint_post(app, client, token):
    post_response = client.post(
        url_for("api.messageendpoint"),
        json={"title": "title 1", "content": "content 1"},
        headers={"Authorization": f"Bearer {token}"},
    )

    expected_keys = ["id", "title", "content", "created"]
    expected_keys_present = map(lambda x: x in post_response.json.keys(), expected_keys)

    assert post_response.status_code == 201
    assert all(expected_keys_present)


def test_message_endpoint_get_specific_not_found(app, client, token):
    response = client.get(
        "/api/v1/message/5555/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert response.json["errors"]


def test_message_endpoint_put_existing(app, client, token):
    data = client.post(
        url_for("api.messageendpoint"),
        json={"title": "title 1", "content": "content 1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    id = data.json["id"]

    response = client.put(
        url_for("api.messageendpoint"),
        json={"id": id, "title": "edited title 1", "content": "edited content 1"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json["id"] == data.json["id"]
    assert response.json["title"] != data.json["title"]
    assert response.json["content"] != data.json["title"]


def test_message_endpoint_put_new(app, client, token):
    id = 1555
    title = "title"
    content = "content"

    response = client.put(
        url_for("api.messageendpoint"),
        json={"id": id, "title": title, "content": content},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json["id"] == id
    assert response.json["title"] == title
    assert response.json["content"] == content


def test_message_endpoint_delete(app, client, token):
    data = client.post(
        url_for("api.messageendpoint"),
        json={"title": "title", "content": "content"},
        headers={"Authorization": f"Bearer {token}"},
    )
    id = data.json["id"]

    delete_res = client.delete(
        url_for("api.messageendpoint", id=data.json["id"]),
        headers={"Authorization": f"Bearer {token}"},
    )
    get_res = client.get(
        f"/api/v1/message/{id}/", headers={"Authorization": f"Bearer {token}"}
    )

    get_res_dict = json.loads(get_res.get_data(as_text=True))

    assert delete_res.status_code == 204
    assert get_res_dict.get("errors") is not None
    assert get_res.status_code == 404


def test_account_endpoint_post_create_account(
    app, client, mocked_send_activation_email
):
    username = "testuser-" + make_uuid()
    response = client.post(
        url_for("api.accountregisterendpoint"),
        json={
            "username": username,
            "password": "testpassword",
            "email": "testmail@gmail.com",
        },
    )

    user = db.session.scalars(select(User).where(User.username == username)).first()
    expected_keys = ["username", "email"]
    expected_keys_present = map(lambda x: x in response.json.keys(), expected_keys)
    template = make_simple_activation_template(user.activation_code)

    assert response.status_code == 201
    assert all(expected_keys_present)
    assert user
    if not current_app.config["SKIP_EMAIL_ACTIVATION"]:
        mocked_send_activation_email.assert_called_once_with(user.email, template)


def test_account_endpoint_post_user_exists(app, client, mocked_send_activation_email):
    username = "testuser-" + make_uuid()

    client.post(
        url_for("api.accountregisterendpoint"),
        json={
            "username": username,
            "password": "testpassword",
            "email": "testmail@wp.com",
        },
    )
    response = client.post(
        url_for("api.accountregisterendpoint"),
        json={
            "username": username,
            "password": "testpassword",
            "email": "testmail@gmail.com",
        },
    )

    assert response.status_code == 400
    assert "errors" in response.json.keys()


def test_account_endpoint_post_bad_schema(app, client, mocked_send_activation_email):
    response = client.post(
        url_for("api.accountregisterendpoint"),
        json={"somefield": "qwe"},
    )

    assert response.status_code == 400
    assert "errors" in response.json.keys()


def test_activate_account_endpoint_get_activate_account(
    app, client, mocked_send_activation_email
):
    username = "testuser-" + make_uuid()

    client.post(
        url_for("api.accountregisterendpoint"),
        json={
            "username": username,
            "password": "testpassword",
            "email": "testmail@wp.com",
        },
    )
    user = db.session.scalars(select(User).where(User.username == username)).first()

    get_res = client.get(
        url_for("api.accountactivateendpoint", code=user.activation_code),
    )

    assert get_res.status_code == 200
    assert "status" in get_res.json.keys()


def test_activate_account_endpoint_get_usr_doesnt_exist(app, client):
    get_res = client.get(
        url_for("api.accountactivateendpoint", code="qweqweqweq"),
    )

    assert get_res.status_code == 404


def test_login_endpoint_post_login(app, client, mocked_send_activation_email):
    username = "testuser-" + make_uuid()
    password = "testpassword"
    client.post(
        url_for("api.accountregisterendpoint"),
        json={
            "username": username,
            "password": password,
            "email": "testmail@gmail.com",
        },
    )

    user = db.session.scalars(select(User).where(User.username == username)).first()
    user.activated = True

    response = client.post(
        url_for("api.accountloginendpoint"),
        json={"username": username, "password": password},
    )
    expected_keys = ["access_token", "refresh_token"]
    expected_keys_present = map(lambda x: x in response.json.keys(), expected_keys)

    assert response.status_code == 200
    assert all(expected_keys_present)


def test_login_endpoint_post_bad_schema(app, client, mocked_send_activation_email):
    response = client.post(
        url_for("api.accountloginendpoint"),
        json={"something": "qwe"},
    )

    assert response.status_code == 400
    assert "errors" in response.json.keys()


def test_login_endpoint_post_user_doesnt_exist(
    app, client, mocked_send_activation_email
):
    response = client.post(
        url_for("api.accountloginendpoint"),
        json={"username": "qweqwe", "password": "qweqweqwe"},
    )

    assert response.status_code == 401
    assert "errors" in response.json.keys()


def test_login_endpoint_post_user_not_active(app, client, mocked_send_activation_email):
    username = "testuser-" + make_uuid()
    password = "testpassword"
    client.post(
        url_for("api.accountregisterendpoint"),
        json={
            "username": username,
            "password": password,
            "email": "testmail@gmail.com",
        },
    )

    response = client.post(
        url_for("api.accountloginendpoint"),
        json={"username": username, "password": password},
    )

    assert response.status_code == 401
    assert "errors" in response.json.keys()


def test_login_endpoint_post_wrong_password(app, client, mocked_send_activation_email):
    username = "testuser-" + make_uuid()
    client.post(
        url_for("api.accountregisterendpoint"),
        json={
            "username": username,
            "password": "password",
            "email": "testmail@gmail.com",
        },
    )

    user = db.session.scalars(select(User).where(User.username == username)).first()
    user.activated = True

    response = client.post(
        url_for("api.accountloginendpoint"),
        json={"username": username, "password": "badpassword"},
    )

    assert response.status_code == 401
    assert "errors" in response.json.keys()


def test_login_refresh_endpoint_post_refresh_tokens(
    app, client, mocked_send_activation_email
):
    username = "testuser-" + make_uuid()
    password = "testpassword"

    client.post(
        url_for("api.accountregisterendpoint"),
        json={"username": username, "password": password, "email": "testmail@wp.com"},
    )
    user = db.session.scalars(select(User).where(User.username == username)).first()
    user.activated = True

    tokens_response = client.post(
        url_for("api.accountloginendpoint"),
        json={"username": username, "password": password},
    )

    token = tokens_response.json["refresh_token"]
    response = client.post(
        url_for("api.accountloginrefreshendpoint"),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json.keys()
