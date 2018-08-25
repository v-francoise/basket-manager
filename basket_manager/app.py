# -*- coding: utf-8 -*-

import logging
import typing
import uuid

import apistar
from apistar import App, Route
from apistar_cors_hooks import CORSRequestHooks

import daiquiri
import peewee

from basket_manager import models
from basket_manager import schemas

daiquiri.setup(level=logging.DEBUG)


def create_basket(basket: schemas.Basket) -> schemas.Basket:
    basket = models.Basket.create(id=basket.id or uuid.uuid4())

    return schemas.Basket(
        id=str(basket.id),
        products=[],
    )


def list_baskets() -> typing.List[schemas.Basket]:
    baskets = models.Basket.select()

    return [schemas.Basket.from_model(basket) for basket in baskets]


def get_basket(id: str) -> schemas.Basket:
    basket = models.Basket.get_by_id(id)
    return schemas.Basket.from_model(basket)


def add_product_to_basket(id: str, product: schemas.Product) -> schemas.Basket:
    basket = models.Basket.get_by_id(id)
    for existing_product in basket.products:
        if existing_product.type == product.type:
            raise apistar.exceptions.HTTPException(
                status_code=409,
                detail="A product of the same type has already been "
                       "added: %s." % existing_product.name)

    models.Product.create(
        name=product.name,
        type=product.type,
        basket=basket,
    )
    return schemas.Basket.from_model(basket)


def delete_basket(id: str) -> schemas.Basket:
    basket = models.Basket.get_by_id(id)
    models.Basket.delete().where(models.Basket.id == id).execute()
    return schemas.Basket.from_model(basket)


def remove_product_from_basket(id: str, product_name: str) -> schemas.Basket:
    basket = models.Basket.get_by_id(id)
    product = models.Product.get(id=id, name=product_name)
    product.delete()

    return schemas.Basket.from_model(basket)


routes = [
    Route('/baskets', method='POST', handler=create_basket),
    Route('/baskets', method='GET', handler=list_baskets),
    Route('/baskets/{id}', method='DELETE', handler=delete_basket),
    Route('/baskets/{id}', method='GET', handler=get_basket),
    Route('/baskets/{id}/add', method='POST', handler=add_product_to_basket),
    Route('/baskets/{id}/remove/{name}',
          method='DELETE', handler=remove_product_from_basket),
]


event_hooks = [CORSRequestHooks()]
app = App(routes=routes, event_hooks=event_hooks)


def main():
    app.serve('0.0.0.0', 8080, debug=False)


if __name__ == '__main__':
    main()
