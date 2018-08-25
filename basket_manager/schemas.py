# -*- coding: utf-8 -*-

from apistar import types, validators


# class Article(types.Type):
#     """Represent the catalog entry of what can be added to a basket."""
#     name = validators.String(max_length=100)


class Product(types.Type):
    """Represent the item that was added to a basket."""
    name = validators.String(max_length=100)
    type = validators.String(enum=["mobile", "sim", "broadband"])
    basket_id = validators.String(max_length=48, allow_null=True)

    @classmethod
    def from_model(cls, obj):
        return cls(name=obj.name, type=obj.type, basket_id=str(obj.basket.id))


class Basket(types.Type):
    """Represent the item that was added to a basket."""
    id = validators.String(max_length=48, allow_null=True)
    products = validators.Array(items=Product, allow_null=True)

    @classmethod
    def from_model(cls, obj):
        return cls(
            id=str(obj.id),
            products=[Product.from_model(p) for p in obj.products]
        )
