#  e4c6 ~ 2021
from enum import *

from mongoengine import Document, StringField, EmbeddedDocument, EnumField, EmbeddedDocumentField

from Entities.SharedEntities import PreferredEngine


class PreferredLanguage(Enum):
    EN = "EN",
    TR = "TR"


class UserPreferences(EmbeddedDocument):
    language = EnumField(PreferredLanguage, default=PreferredLanguage.EN)
    preferred_engine = EnumField(PreferredEngine, default=PreferredEngine.ADA)


class User(Document):
    discord_id = StringField(unique=True, required=True, max_length=50)
    preferences = EmbeddedDocumentField(UserPreferences)
