import logging
from fastapi import Depends, HTTPException, FastAPI
from sqlmodel import Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager
from townhall.db import Agent

import discord_bot.bot as bot

# TODO: Move to database.py or something
from townhall.db import User, Thread, Message, MessageResponse

logging.basicConfig(filename='discord_bot.log', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())

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
    logging.debug("Starting application..")
    logging.debug("Creating database tables if required..")
    create_db_and_tables()

    logging.debug("Starting api endpoints..")
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
async def create_response(*, session: Session = Depends(get_session), message: Message, thread_id: int = None, user_id: int):
    user_agent = None
    guru_agent = None
    user_agent_name = 'user' + str(user_id)
    guru_agent_name = 'guru' + str(user_id)

    logging.debug("Looking up agents")
    # TODO: Use agent_id's instead
    lookup = session.exec(select(Agent).where(Agent.name == user_agent_name))
    db_user_agent = lookup.one_or_none()
    lookup = session.exec(select(Agent).where(Agent.name == guru_agent_name))
    db_guru_agent = lookup.one_or_none()

    if db_user_agent is None:
        logging.debug("No user agent found, creating new one")
        db_user_agent = Agent(name=user_agent_name, system_message=bot.DEFAULT_SYSTEM_MESSAGE)
        session.add(db_user_agent)
        session.commit()
    if db_guru_agent is None:
        logging.debug("No guru agent found, creating new one")
        db_guru_agent = Agent(name=guru_agent_name, system_message=bot.DEFAULT_SYSTEM_MESSAGE)
        session.add(db_guru_agent)
        session.commit()
    user_agent = bot.generate_user_agent(name=user_agent_name)
    guru_agent = bot.generate_teachable_agent(name=guru_agent_name)

    if user_id:
        # we have everything, do the things
        user = session.exec(select(User).where(User.id == user_id))
        user = user.one_or_none()

    if user is None:
        logging.debug("No user found, creating new one")
        user = User(id=user_id, username='sid', discriminator='0', avatar="http://www.gravatar.com/avatar") # attempt to save with the user_id passed.
        session.add(user)
        session.commit()
        session.refresh(user)

    thread = session.get(Thread, thread_id)
    logging.debug("123123Thread found: " + str(thread))
    if thread is None or thread.id is None:
        logging.debug("No thread found, creating new one")
        thread = Thread(id=thread_id)
        session.add(thread)
        session.commit()
        session.refresh(thread)

    print("thread ASD: ", thread.id)

    logging.debug("Update agents with oai_messages")
    msgs = []
    for msg in thread.messages:
        logging.debug(msg)
        if msg.role == 'user':
            logging.debug("Sending message to user agent")
            await user_agent.a_send(msg.content, guru_agent, request_reply=False, silent=False)
            logging.debug("Message sent to user agent")
        else:
            logging.debug("Sending message to guru agent")
            await guru_agent.a_send(msg.content, user_agent, request_reply=False, silent=False)
            logging.debug("Message sent to guru agent")
        msgs.append(msg)
    logging.debug(msgs)
    logging.debug("Agents updated")

    logging.debug("Thread found, adding message")
    message.thread_id = thread.id
    message.user_id = user.id
    session.add(message)
    session.commit()
    session.refresh(message)
    logging.debug("Message added, starting chat")

    logging.debug("Agents found, starting chat")
    await user_agent.a_initiate_chat(guru_agent, message=message.content, clear_history=False)
    logging.debug("Guru response received")
    last_message = guru_agent.last_message(user_agent).copy()
    last_message['user_id'] = user.id
    last_message['thread_id'] = thread.id

    logging.debug("Reply Found, adding message")
    reply_message = Message(**last_message)
    reply_message.thread_id = thread.id
    reply_message.user_id = user.id
    session.add(reply_message)
    session.commit()
    session.refresh(reply_message)
    logging.debug("Message added, starting chat")

    # switch role last, as we are saving above
    last_message['role'] = 'guru'
    return last_message