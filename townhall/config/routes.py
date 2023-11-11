from fastapi import Depends, HTTPException, FastAPI
from sqlmodel import Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager
from townhall.db import Agent

import discord_bot.bot as bot

# TODO: Move to database.py or something
from townhall.db import User, Thread, Message, MessageResponse

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

@app.post("/ai/user")
async def create_user(*, session: Session = Depends(get_session), user: User):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.post("/ai/response")
async def create_response(*, session: Session = Depends(get_session), message: Message, thread_id: int, user_id: int):
    user_agent = None
    guru_agent = None
    try:
        user_agent_name = 'user' + str(user_id)
        guru_agent_name = 'guru' + str(user_id)
        print("Looking up agents")
        # TODO: Use agent_id's instead
        lookup = session.exec(select(Agent).where(Agent.name == user_agent_name))
        db_user_agent = lookup.one_or_none()
        lookup = session.exec(select(Agent).where(Agent.name == guru_agent_name))
        db_guru_agent = lookup.one_or_none()

        if db_user_agent is None:
            print("No user agent found, creating new one")
            db_user_agent = Agent(name=guru_agent_name, system_message=bot.DEFAULT_SYSTEM_MESSAGE)
            session.add(db_user_agent)
            session.commit()
        if db_guru_agent is None:
            print("No guru agent found, creating new one")
            db_guru_agent = Agent(name=guru_agent_name, system_message=bot.DEFAULT_SYSTEM_MESSAGE)
            session.add(db_guru_agent)
            session.commit()
        user_agent = bot.generate_user_agent(name=user_agent_name)
        guru_agent = bot.generate_teachable_agent(name=guru_agent_name)

        print("Agents found, starting chat")
        await user_agent.a_initiate_chat(guru_agent, message=message.content, clear_history=False)
        print("Guru response received")
        last_message = guru_agent.last_message(user_agent).copy()
        last_message['role'] = 'guru'
        last_message['user_id'] = user_id
        last_message['thread_id'] = thread_id
        return last_message
    except Exception as e:
        print(e.with_traceback())
        raise HTTPException(status_code=500, detail=str(e))