from models import User


def test_user_model_setter_salted_hashed_password(app):
    user = User(username="John Smith", email="somemail@qwe.com")
    input_pw = "testpassword"

    user.password = input_pw

    assert len(user.password) == 60
    assert user.password != input_pw


def test_user_model_verify_password(app):
    user = User(username="John Smith", email="somemail@qwe.com")
    input_pw = "testpassword"
    user.password = input_pw

    assert user.verify_password(input_pw) is True
