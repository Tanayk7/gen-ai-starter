import pprint
from typing import Union
from fastapi import FastAPI, HTTPException
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
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "q": q}

# filter items 
@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    if skip < 0:
        raise HTTPException(status_code=400, detail="Skip parameter must be non-negative")
    if limit < 0:
        raise HTTPException(status_code=400, detail="Limit parameter must be non-negative")
    if limit > 100:
        raise HTTPException(status_code=400, detail="Limit parameter must not exceed 100")
    return items[skip : skip + limit]

# create item
@app.post("/items/")
def create_item(item: Item):
    if any(existing_item["name"] == item.name for existing_item in items):
        raise HTTPException(status_code=400, detail="Item with this name already exists")
    if item.price < 0:
        raise HTTPException(status_code=400, detail="Price must be non-negative")
    items.append(item.model_dump())
    return item

# update item
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    if item_id < 0 or item_id >= len(items):
        raise HTTPException(status_code=404, detail="Item not found")
    if item.price < 0:
        raise HTTPException(status_code=400, detail="Price must be non-negative")
    items[item_id] = item.model_dump()
    return item
