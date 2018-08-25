# -*- coding: utf-8 -*-

import json
import uuid

from peewee import *

from playhouse.shortcuts import model_to_dict

DATABASE = None


def get_database():
    global DATABASE
    if DATABASE is None:
        DATABASE = SqliteDatabase(':memory:')
    return DATABASE


def create_tables():
    get_database().create_tables(BaseModel.__subclasses__())


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj)
        if obj is None:
            return None
        return json.JSONEncoder.default(self, obj)


class BaseModel(Model):

    def to_dict(self, backrefs=True):
        return model_to_dict(self, backrefs=True)

    def to_json(self):
        return json.loads(json.dumps(self.to_dict(), cls=UUIDEncoder))


class Basket(BaseModel):
    id = UUIDField(primary_key=True)

    class Meta:
        database = get_database()


class Product(BaseModel):
    name = CharField(max_length=100)
    type = CharField(max_length=100, choices=("sim", "broadband", "mobile"))
    basket = ForeignKeyField(Basket, backref='products')

    class Meta:
        database = get_database()
        primary_key = CompositeKey('name', 'basket')


create_tables()
