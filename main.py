import uuid
import logging
from fastapi import Depends, FastAPI, HTTPException, Query
from typing import Optional, List
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
from contextlib import asynccontextmanager

import discord_bot.bot as bot

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    discriminator: str
    avatar: str
    messages: List["Message"] = Relationship(back_populates="user")

class Thread(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    messages: List["Message"] = Relationship(back_populates="thread")

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    thread: Optional["Thread"] = Relationship(back_populates="messages")
    thread_id: Optional[int] = Field(default=None, foreign_key="thread.id")
    user: Optional["User"] = Relationship(back_populates="messages")
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    content: str
    role: str

class MessageResponse:
    id: int
    thread_id: int
    user_id: str
    content: str
    role: str

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
SQL_ENGINE = create_engine(sqlite_url, echo=True, connect_args=connect_args)
def create_db_and_tables():
    SQLModel.metadata.create_all(SQL_ENGINE)

def get_session():
    with Session(SQL_ENGINE) as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application..")
    print("Creating database tables if required..")
    create_db_and_tables()

    print("Starting api endpoints..")
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/ai/thread")
async def read_thread(*, session: Session = Depends(get_session), id: int):
    thread = session.get(Thread, id)
    return thread

@app.post("/ai/thread")
async def create_thread(*, session: Session = Depends(get_session), thread: Thread):
    session.add(thread)
    session.commit()
    session.refresh(thread)
    return thread

import random

@app.post("/ai/response")
async def create_response(*, session: Session = Depends(get_session), message: Message, thread_id: int, user_id: Optional[str] = None):
    if user_id is None:
        pass
        # user_id = str(uuid.uuid4())
        # user_id = str(random.randint(0, 1000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000))

    try:
        print("Sending message to bot")
        user_agent = None
        guru_agent = None

        for agent in bot.AGENTS:
            if agent.name == 'user':
                user_agent = agent
            if agent.name == 'guru':
                guru_agent = agent

        if user_agent is None:
            print("No user agent found, creating new one")
            user_agent = bot.generate_user_agent(name='user')

        if guru_agent is None:
            print("No guru agent found, creating new one")
            guru_agent = bot.generate_teachable_agent(name='guru')

        await user_agent.a_initiate_chat(guru_agent, message=message.content, clear_history=False)

        print("Bot response received")
        last_message = guru_agent.last_message(user_agent).copy()
        last_message['role'] = 'guru'
        last_message['user_id'] = user_id
        last_message['thread_id'] = thread_id

        return last_message
    except Exception as e:
        print(e.with_traceback())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)