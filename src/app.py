import pprint
from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

items: Item = [
    {"name": "Foo", "price": 50.2, "is_offer": True},
    {"name": "Bar", "price": 62.3, "is_offer": False}, 
    {"name": "Baz", "price": 72.3, "is_offer": True},
]

# root 
@app.get("/")
def read_root():
    return {"message": "Hello World"}

# get item by id 
@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# filter items 
@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    return items[skip : skip + limit]

# create item
@app.post("/items/")
def create_item(item: Item):
    items.append(item.model_dump())
    return item

# update item
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    items[item_id] = item.model_dump()
    return item
