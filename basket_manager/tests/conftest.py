# -*- coding: utf-8 -*-

import uuid

from apistar import test
import pytest

from basket_manager.app import app
from basket_manager import models


@pytest.fixture
def client():
    return test.TestClient(app)


@pytest.fixture
def database(mocker):
    db = models.get_database()
    models.create_tables()

    yield db

    db.drop_tables(models.BaseModel.__subclasses__())


@pytest.fixture
def basket1(database):
    yield models.Basket.create(id=uuid.uuid4())


@pytest.fixture
def sim1_data():
    return dict(name="sim1", type="sim")


@pytest.fixture
def sim2_data():
    return dict(name="sim2", type="sim")


@pytest.fixture
def broadband1_data():
    return dict(name="broadband1", type="broadband")


@pytest.fixture
def mobile1_data():
    return dict(name="mobile1", type="mobile")
