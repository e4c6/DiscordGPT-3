#  e4c6 ~ 2021

import os

import pytest
from mongoengine import connect, get_connection

from Entities.ServerEntities import Server, ServerAuthentication, ServerRules
from Entities.ServerErrors import EngineNotAllowedError, AllowanceOverError
from Entities.SharedEntities import PreferredEngine
from Entities.UserEntities import User
from Implementation.CryptoHandler import CryptoHandler

db_name = os.environ.get("MONGO_DBNAME", default="gpt3")
db_user = os.environ.get("MONGO_DBUSER", default="gpt3")
db_pass = os.environ.get("MONGO_DBPASS", default="gpt3")
db_host = os.environ.get("MONGO_HOST", default="127.0.0.1")
db_port = os.environ.get("MONGO_PORT", default="27017")


@pytest.fixture()
def mock_connect():
    connect(host="mongodb://{}:{}@{}:{}/{}?authSource=admin".format(db_user, db_pass, db_host, db_port, db_name))
    yield get_connection()


@pytest.fixture()
def crypto_handler():
    yield CryptoHandler()


@pytest.fixture()
def mock_server(mock_connect):
    User.drop_collection()
    Server.drop_collection()
    ServerAuthentication.drop_collection()

    new_auth = ServerAuthentication()
    new_auth.save()
    new_vip = User(discord_id="test_vip")
    new_vip.save()
    new_rules = ServerRules(vips=[new_vip], default_allowance=50, default_engine=PreferredEngine.ADA)
    new_user = User(discord_id="test_user")
    new_admin = User(discord_id="test_admin")
    new_server = Server(discord_id="test_server", admin=new_admin,
                        users=[new_user, new_admin], rules=new_rules, authentication=new_auth)

    new_user.save()
    new_admin.save()
    new_server.save()

    server = Server.objects(discord_id=new_server.discord_id).get()
    yield server


def test_change_token(mock_server, crypto_handler):
    mock_token = "sk-128312983721"
    key = crypto_handler.generate_key()
    encrypted_token = crypto_handler.encrypt(mock_token.encode(), key)
    mock_server.authentication.token = encrypted_token
    mock_server.authentication.save()
    mock_server.save()
    server = Server.objects(discord_id="test_server").get()
    decrypted_token = crypto_handler.decrypt(server.authentication.token, key).decode()
    assert decrypted_token == mock_token


def test_get_user_usage(mock_server, crypto_handler):
    test_change_token(mock_server, crypto_handler)
    standard_user = User.objects(discord_id="test_user").get()
    assert mock_server.get_user_usage(standard_user) == 0
    mock_server.consume_token(standard_user, 20, PreferredEngine.ADA)
    standard_user = User.objects(discord_id="test_user").get()
    assert mock_server.get_user_usage(standard_user) == 20


def test_can_spend(mock_server):
    vip_user = User.objects(discord_id="test_vip").get()
    standard_user = User.objects(discord_id="test_user").get()
    admin_user = User.objects(discord_id="test_admin").get()
    assert mock_server.can_spend(vip_user, 100) is True
    assert mock_server.can_spend(admin_user, 100) is True
    assert mock_server.can_spend(standard_user, 100) is False
    assert mock_server.can_spend(standard_user, 20) is True


def test_can_use_engine(mock_server):
    vip_user = User.objects(discord_id="test_vip").get()
    standard_user = User.objects(discord_id="test_user").get()
    admin_user = User.objects(discord_id="test_admin").get()
    assert mock_server.can_use_engine(vip_user, PreferredEngine.DAVINCI) is True
    assert mock_server.can_use_engine(admin_user, PreferredEngine.DAVINCI) is True
    assert mock_server.can_use_engine(standard_user, PreferredEngine.DAVINCI) is False
    assert mock_server.can_use_engine(standard_user, PreferredEngine.ADA) is True


def test_consume_token(mock_server, crypto_handler):
    test_change_token(mock_server, crypto_handler)
    vip_user = User.objects(discord_id="test_vip").get()
    standard_user = User.objects(discord_id="test_user").get()
    admin_user = User.objects(discord_id="test_admin").get()
    mock_server.consume_token(standard_user, 20, PreferredEngine.ADA)
    server = Server.objects(discord_id="test_server").get()
    assert server.can_spend(standard_user, 31) is False
    with pytest.raises(EngineNotAllowedError):
        server.consume_token(standard_user, 20, PreferredEngine.DAVINCI)
    with pytest.raises(AllowanceOverError):
        server.consume_token(standard_user, 100, PreferredEngine.ADA)
    server.consume_token(vip_user, 100, PreferredEngine.DAVINCI)
    server.consume_token(admin_user, 100, PreferredEngine.DAVINCI)
    assert server.get_user_usage(vip_user) == 100
    assert server.get_user_usage(admin_user) == 100
    assert server.get_user_usage(standard_user) == 20


def test_add_user(mock_server):
    test_user_2 = User(discord_id="test_user_2")
    test_user_2.save()
    mock_server.add_user(test_user_2)
    server = Server.objects(discord_id="test_server").get()
    assert test_user_2 in server.users


def test_remove_user(mock_server):
    test_user_2 = User(discord_id="test_user_2")
    test_user_2.save()
    mock_server.add_user(test_user_2)
    assert test_user_2 in mock_server.users
    mock_server.remove_user(test_user_2)
    server = Server.objects(discord_id="test_server").get()
    assert test_user_2 not in server.users


def test_set_admin(mock_server):
    test_user_2 = User(discord_id="test_user_2")
    test_user_2.save()
    mock_server.add_user(test_user_2)
    assert test_user_2 in mock_server.users
    mock_server.set_admin(test_user_2)
    server = Server.objects(discord_id="test_server").get()
    assert server.admin == test_user_2


def test_add_vip(mock_server):
    server = mock_server
    test_vip = User.objects(discord_id="test_vip").get()
    server.remove_vip(test_vip)
    server.add_vip(test_vip)
    server = Server.objects(discord_id="test_server").get()
    assert test_vip in server.rules.vips


def test_remove_vip(mock_server):
    server = mock_server
    test_vip = User.objects(discord_id="test_vip").get()
    if test_vip not in server.rules.vips:
        server.add_vip(test_vip)
    server.remove_vip(test_vip)
    server = Server.objects(discord_id="test_server").get()
    assert test_vip not in server.rules.vips


def test_set_allowance(mock_server):
    mock_server.rules.default_allowance = 1
    mock_server.save()
    mock_server = Server.objects(discord_id="test_server").get()
    assert mock_server.rules.default_allowance == 1


def test_set_length(mock_server):
    mock_server.rules.default_response_length = 1
    mock_server.save()
    mock_server = Server.objects(discord_id="test_server").get()
    assert mock_server.rules.default_response_length == 1
