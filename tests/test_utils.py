from flask import current_app, url_for

from utils import api_exception, make_simple_activation_template, make_uuid


def test_make_uuid():
    uuid = make_uuid()
    assert len(uuid) == 36
    assert type(uuid) is str


def test_make_simple_activation_template():
    code = "activation_code"
    with current_app.test_request_context():
        template = make_simple_activation_template(code)

    assert code in template
    assert "<html><head>" in template


def test_api_exception():
    message = "some error has occured"
    status = 418
    exception = api_exception(message, status)

    assert type(exception) is tuple
    assert "errors" in exception[0].keys()
    assert exception[0]["errors"] == message
    assert exception[1] == status
