from typing import List
import databases
import sqlalchemy
from fastapi import FastAPI
from pydantic import BaseModel


DATABASE_URL = "sqlite:///./blogapi.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

posts = sqlalchemy.Table(
    "posts",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("text", sqlalchemy.String),
    sqlalchemy.Column("is_published", sqlalchemy.Boolean),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

metadata.create_all(engine)

class PostIn(BaseModel):
    title: str
    text: str
    is_published: bool


class Post(BaseModel):
    id: int
    title: str
    text: str
    is_published: bool

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get('/posts/', response_model=List[Post])
async def read_posts():
    query = posts.select()
    return await database.fetch_all(query)


@app.post("/posts/", response_model=Post)
async def create_post(post: PostIn):
    query = posts.insert().values(title=post.title, text=post.text, is_published=post.is_published)
    last_record_id = await database.execute(query)
    return {**post.dict(), "id": last_record_id}


@app.delete("/posts/{post_id}")
async def delete_post(post_id: int):
    query = posts.delete().where(id == post_id)
    await database.execute(query)
    return {"detail": "Post deleted", "status_code": 204}