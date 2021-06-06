#  e4c6 ~ 2021

from datetime import datetime, timedelta

from mongoengine import *
from mongoengine import Document, StringField, ListField, ReferenceField, BinaryField, BooleanField, DateTimeField

from Entities.ServerErrors import NoTokenError, AllowanceOverError, EngineNotAllowedError
from Entities.SharedEntities import PreferredEngine
from Entities.UserEntities import User


class ServerAuthentication(Document):
    token = BinaryField(default=None)
    locked = BooleanField(default=False)
    valid = BooleanField(default=False)
    last_changed = DateTimeField()

    @property
    def _token(self) -> bytes:
        return self.token

    @_token.setter
    def _token(self, value) -> None:
        self.token = value
        self.last_changed = datetime.utcnow()
        if self.locked:
            self.unlock()

    def lock(self) -> None:
        self.locked = True

    def unlock(self) -> None:
        self.locked = False


class ServerUsageLog(EmbeddedDocument):
    user = ReferenceField(User, required=True, reverse_delete_rule=DO_NOTHING)
    date = DateTimeField(required=True)
    amount = IntField(required=True)
    key = ReferenceField(ServerAuthentication, required=True, reverse_delete_rule=DO_NOTHING)
    engine = EnumField(PreferredEngine, required=True)


class ServerRules(EmbeddedDocument):
    vips = ListField(ReferenceField(User), reverse_delete_rule=DO_NOTHING)
    default_allowance = IntField(default=50, max_value=50000)
    default_response_length = IntField(default=50, max_value=1024)
    default_engine = EnumField(PreferredEngine, default=PreferredEngine.ADA)


class Server(Document):
    discord_id = StringField(unique=True, required=True, max_length=50)
    authentication = ReferenceField(ServerAuthentication, required=False, default=None, reverse_delete_rule=DO_NOTHING)
    admin = ReferenceField(User, reverse_delete_rule=DO_NOTHING)
    users = ListField(ReferenceField(User, reverse_delete_rule=DO_NOTHING))
    rules = EmbeddedDocumentField(ServerRules)
    usage = ListField(EmbeddedDocumentField(ServerUsageLog))

    def change_token(self, encrypted_token: bytes):
        self.authentication._token = encrypted_token
        self.authentication.save()

    def get_user_usage(self, user: User):
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        usage = [r.amount for r in self.usage if r.user == user and r.date > yesterday]
        return sum(usage)

    def can_spend(self, user: User, amount: int) -> bool:
        if self.admin == user or user in self.rules.vips:
            return True
        today_usage = self.get_user_usage(user)
        if self.rules.default_allowance >= today_usage + amount:
            return True
        return False

    def can_use_engine(self, user: User, engine: PreferredEngine) -> bool:
        if self.rules.default_engine >= engine:
            return True
        if self.admin == user or user in self.rules.vips:
            return True
        return False

    def consume_token(self, user: User, amount: int, engine: PreferredEngine):
        if self.authentication.token is None:
            raise NoTokenError()

        if not self.can_spend(user, amount):
            raise AllowanceOverError()

        if not self.can_use_engine(user, engine):
            raise EngineNotAllowedError()

        usage = ServerUsageLog(user=user, amount=amount, date=datetime.utcnow(), engine=engine, key=self.authentication)
        self.usage.append(usage)
        self.save()

    def add_user(self, user: User):
        self.users.append(user)
        self.save()

    def remove_user(self, user: User):
        self.users.remove(user)
        self.save()

    def set_admin(self, user: User):
        if user not in self.users:
            self.add_user(user)
        self.admin = user
        self.save()

    def add_vip(self, user: User):
        self.rules.vips.append(user)
        self.save()

    def remove_vip(self, user: User):
        self.rules.vips.remove(user)
        self.save()

    def set_allowance(self, allowance: int):
        self.rules.default_allowance = allowance
        self.save()

    def set_length(self, length: int):
        self.rules.default_response_length = length
        self.save()
