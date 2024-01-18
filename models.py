from datetime import datetime, timezone

import bcrypt
from sqlalchemy.ext.hybrid import hybrid_property

from extensions import db
from utils import make_uuid

# M2M relationship users-messages
follow = db.Table(
    "follow",
    db.Column("follower_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    _password = db.Column(db.String(200), nullable=False)
    _salt = db.Column(db.String(200), nullable=False)
    activated = db.Column(db.Boolean, nullable=False, default=False)
    invitation_codes = db.relationship("InvitationCode", backref="user", lazy=True)
    messages = db.relationship("Message", backref="user", lazy=True)
    created = db.Column(
        db.DateTime, nullable=True, default=lambda: datetime.now(tz=timezone.utc)
    )
    activation_code = db.Column(db.String(40), nullable=True, default=make_uuid)

    # m2m self referential relationship https://docs.sqlalchemy.org/en/20/orm/join_conditions.html#self-referential-many-to-many
    follows = db.relationship(
        "User",
        secondary=follow,
        primaryjoin=id == follow.c.follower_id,
        secondaryjoin=id == follow.c.followed_id,
        backref="followed_by",
    )

    def make_salted_hash(self, raw_password: str) -> str:
        """
        To prevent db data conversion issues use encoded binary type
        while operating in bcrypt and decoded str type for storing cryptographic values in db
        """
        if not self._salt:
            self._salt = bcrypt.gensalt().decode("utf-8")

        pw_encoded = raw_password.encode("utf-8")
        salt_encoded = self._salt.encode("utf-8")
        return bcrypt.hashpw(pw_encoded, salt_encoded).decode("utf-8")

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value: str) -> bool:
        self._password = self.make_salted_hash(value)
        return True

    def verify_password(self, value: str) -> bool:
        pw_to_verify = self.make_salted_hash(value)
        return pw_to_verify == self._password


class InvitationCode(db.Model):
    """
    Not used yet.
    Invite other user to allow him to view your messages.
    """

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(30), nullable=False)
    owner = db.Column(db.String(100), nullable=False)
    created = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(tz=timezone.utc)
    )
    valid_for = db.Column(db.Integer, nullable=False)
    disabled = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def generate_code(self):
        pass  # TODO


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(500), nullable=False)
    created = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(tz=timezone.utc)
    )

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
