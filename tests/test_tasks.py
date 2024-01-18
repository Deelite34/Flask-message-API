from extensions import db
from models import User
from tasks import send_activation_email
from utils import make_simple_activation_template, make_uuid


def test_send_activation_email(app, mocked_send_activation_email):
    username = "testuser-" + make_uuid()
    user = User(username=username, email="testmail@mail.com")
    user.password = "samplepassword"
    db.session.add(user)
    db.session.commit()
    template = make_simple_activation_template(user.activation_code)

    send_activation_email.delay(user.email, template)

    mocked_send_activation_email.assert_called_once_with(user.email, template)
