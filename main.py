from datetime import datetime
from hashlib import new
from random import randint
from typing import Any

from fastapi import FastAPI

app = FastAPI(root_path="/api/v1")
data = [
    {"campaign_id": 1, "name": "Campaign 1", "created_at": datetime.now(), "updated_at": datetime.now()},
    {"campaign_id": 2, "name": "Campaign 2", "created_at": datetime.now(), "updated_at": datetime.now()},
]
@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.get("/campaigns")
async def read_campaigns():
    return {"campaigns": data}

@app.get("/campaigns/{campaign_id}")
async def read_campaign(campaign_id: int):
    for campaign in data:
        if campaign["campaign_id"] == campaign_id:
            return {"campaign": campaign}
    return {"error": "Campaign not found"}

@app.post("/campaigns")
async def create_campaign(body: dict[str,Any]):
    new : Any = {
        "campaign_id" : randint(100,1000),
        "name" : body.get("name"),
        "created_at" : datetime.now(),
        "due_date" : body.get("due_date"),
    }

    data.append(new)
    return {"campaign": new}
@app.put("/campaigns/{id}")
async def update_campaign(id: int, body: dict[str,Any]):
    for index, campaign in enumerate(data):
        if campaign["campaign_id"] == id:

            updated :Any = {
                "campaign_id" : id,
                "name" : body.get("name"),
                "created_at" : campaign["created_at"],
                "due_date" : body.get("due_date"),
            }
            data[index] = updated
            return {"campaign": updated}
    return {"error": "Campaign not found"}

@app.delete("/campaigns/{id}")
async def delete_campaign(id: int):
    for index, campaign in enumerate(data):
        if campaign["campaign_id"] == id:
            data.pop(index)
            return {"message": "Campaign deleted successfully"}
    return {"error": "Campaign not found"}