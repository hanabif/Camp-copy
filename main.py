from contextlib import asynccontextmanager
from datetime import datetime, timezone
from random import randint
from typing import Annotated, Any
from fastapi import Depends, FastAPI
from sqlmodel import Field, SQLModel, Session, create_engine, select

class Campaign(SQLModel, table=True):
    campaign_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    due_date: datetime | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory = lambda: datetime.now(timezone.utc), index=True, nullable=False)

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Campaign)).first():
            session.add_all([
                Campaign(name="Campaign 1", due_date=datetime.now(timezone.utc)),
                Campaign(name="Campaign 2", due_date=datetime.now(timezone.utc)),
            ])
            session.commit()
    yield

app = FastAPI(root_path="/api/v1", lifespan=lifespan)

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