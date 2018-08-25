# -*- coding: utf-8 -*-

import uuid

from basket_manager import models


def test_list_basket(client, database, basket1):
    result = client.get("/baskets")

    assert result.json() == [dict(id=str(basket1.id), products=[])]


def test_create_basket(client, database):
    result = client.post('/baskets', {"id": str(uuid.uuid4())})

    assert result.json() == models.Basket.select().first().to_json()


def test_get_basket_by_id(client, database, basket1):
    result = client.get('/baskets/%s' % basket1.id)
    assert result.json() == dict(id=str(basket1.id), products=[])


def test_delete_basket(client, database, basket1):
    result = client.delete('/baskets/%s' % basket1.id)
    assert result.json() == dict(id=str(basket1.id), products=[])


def test_add_product_to_basket(client, database, basket1, sim1_data):
    result = client.post('/baskets/%s/add' % basket1.id, data=sim1_data)

    expected_product = sim1_data.copy()
    expected_product["basket_id"] = str(basket1.id)
    expected = dict(id=str(basket1.id), products=[expected_product])

    assert result.json() == expected


def test_add_2_sim_to_basket(client, database, basket1, sim1_data, sim2_data):
    result = client.post('/baskets/%s/add' % basket1.id, data=sim1_data)

    expected_product = sim1_data.copy()
    expected_product["basket_id"] = str(basket1.id)
    expected = dict(id=str(basket1.id), products=[expected_product])

    result2 = client.post('/baskets/%s/add' % basket1.id, data=sim2_data)

    assert result.status_code == 200
    assert result.json() == expected
    assert result2.status_code == 409
