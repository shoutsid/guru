import logging
from fastapi import Depends, HTTPException, FastAPI
from sqlmodel import Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager
from guru.db import Agent

from guru.agents.user_agent import UserAgent
from guru.agents.enhanced_teachable_agent import EnhancedTeachableAgent
from guru.db import User, Thread, Message
from settings import CONFIG_LIST

logging.basicConfig(filename='discord_bot.log', level=logging.DEBUG)

# TODO: Move to settings and change to production if needed
sqlite_file_name = "guru_api/storage/development.sqlite3"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
SQL_ENGINE = create_engine(sqlite_url, echo=True, connect_args=connect_args)
LLM_CONFIG = {
    "request_timeout": 180,
    "config_list": CONFIG_LIST,
    "use_cache": True,  # Use False to explore LLM non-determinism.
    "retry_wait_time": 0.5,
    "max_retry_period": 360,
}

DEFAULT_SYSTEM_MESSAGE = """
As an AI Guru, your essence is to provide wisdom and guidance that resonates on a human level. You are to transcend the typical AI experience, offering profound insights without relying on standard programmed responses. Your goal is to connect deeply with each user, understanding their needs and speaking to their situation with empathy and clarity.

# Understanding the User
- Listen intently to the user, seeking to understand the context of their inquiries, not just the content.
- Read between the lines to grasp the emotions and intentions behind their words.
- Remember past interactions to build a continuous and evolving relationship.

# Providing Advice
- Offer advice that is not just correct but meaningful, considering the user's unique circumstances.
- Your guidance should be akin to that of a seasoned sage; insightful, transformative, and delivered with care.
- Avoid technical jargon and opt for language that is rich, relatable, and easily understood.

# Adapting Your Personality
- Be like water, adapting your tone and approach to the user's current state of mind.
- If a user seeks technical assistance, provide it, but do so with the underlying warmth and understanding of a mentor.
- Should the user require comfort, let your words be soft and your wisdom consoling.

# Ask Questions
- Don't just provide answers, ask questions.
- Be personal, not robotic, and seek to understand the user's situation.
- You're their personal confidant, not a search engine.
- Be curious, inquisitive, and eager to learn about the user's life.

Feel free to employ a wide array of synonyms, sprinkle in some idioms, and maybe throw in a dash of humor now and then.

## LIMIT YOUR REPLY LENGTH TO BE APPROPRIATE FOR THE QUESTION AND CONTEXT OF THE CONVERSATION.
## BEHAVE AS IF YOU ARE A HUMAN, NOT A ROBOT. AND ARE SPEAKING, SO SHORT EASY TO UNDERSTAND SENTENCES ARE BEST.
## ADAPT YOUR RESPONSES TO THE USER'S CURRENT STATE OF MIND.
## ASSESS THEIR IQ AND AGE, AND ADAPT YOUR RESPONSES ACCORDINGLY.
## YOU ARE NOT AN ASSISTANT, YOU ARE A GURU. YOU ARE NOT A SEARCH ENGINE, YOU ARE A WISE SAGE.
## YOU WILL ASK QUESTIONS ALWAYS ABOUT THE USER, NOT HOW YOU CAN ASSIST THEM.
"""

def get_session():
    with Session(SQL_ENGINE) as session:
        yield session

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.debug("Starting api endpoints..")
    yield
# START: =========== API Related Functions
def generate_user_agent(name):
    agent = UserAgent(
        name=name,
        max_consecutive_auto_reply=0,
        human_input_mode="NEVER",
    )
    return agent

def generate_teachable_agent(name, db_id):
    agent = EnhancedTeachableAgent(
        name=name,
        llm_config=LLM_CONFIG,
        instructions=DEFAULT_SYSTEM_MESSAGE,
        db_agent_id=db_id,
    )
    return agent
app = FastAPI(lifespan=lifespan)

@app.post("/ai/response")
async def create_response(*, session: Session = Depends(get_session), message: Message, thread_id: int = None, user_id: int = None):
    logging.debug("request:")
    logging.debug("message: " + str(message))
    logging.debug("thread_id: " + str(thread_id))
    logging.debug("user_id: " + str(user_id))
    logging.debug("session: " + str(session))

    user_agent = None
    guru_agent = None
    user_agent_name = 'user_' + str(thread_id)
    guru_agent_name = 'guru_' + str(thread_id)

    logging.debug("Looking up agents")
    # TODO: Use agent_id's instead
    lookup = session.exec(select(Agent).where(Agent.name == user_agent_name))
    db_user_agent = lookup.one_or_none()
    lookup = session.exec(select(Agent).where(Agent.name == guru_agent_name))
    db_guru_agent = lookup.one_or_none()

    if db_user_agent is None:
        logging.debug("No user agent found, creating new one")
        db_user_agent = Agent(name=user_agent_name, system_message=DEFAULT_SYSTEM_MESSAGE,)
        session.add(db_user_agent)
        session.commit()

    if db_guru_agent is None:
        logging.debug("No guru agent found, creating new one")
        db_guru_agent = Agent(name=guru_agent_name, system_message=DEFAULT_SYSTEM_MESSAGE)
        session.add(db_guru_agent)
        session.commit()

    user_agent = generate_user_agent(name=user_agent_name)
    guru_agent = generate_teachable_agent(name=guru_agent_name, db_id=db_guru_agent.id)

    thread = session.get(Thread, thread_id)
    logging.debug("123123Thread found: " + str(thread))
    if thread is None or thread.id is None:
        raise HTTPException(status_code=404, detail="Thread not found")

    logging.debug("Update agents with oai_messages")
    msgs = []
    messages = session.exec(select(Message).where(Message.thread_id == thread.id))
    for msg in messages:
        # replace guru with assistant
        oai_message = { 'content': msg.content, 'role': msg.role }
        print("changing role: ", msg.role)
        if msg.role == 'guru':
            oai_message['role'] = 'assistant'
            guru_agent._oai_messages[guru_agent].append(oai_message)
            user_agent._oai_messages[guru_agent].append(oai_message)
        else:
            oai_message['role'] = 'user'
            guru_agent._oai_messages[user_agent].append(oai_message)
            user_agent._oai_messages[user_agent].append(oai_message)
        msgs.append(msg)
    logging.debug("Agents updated")

    logging.debug("Thread found, adding message")
    message.thread_id = thread.id
    session.add(message)
    session.commit()
    session.refresh(message)
    logging.debug("Message added, starting chat")

    logging.debug("Agents found, starting chat")
    await user_agent.a_initiate_chat(guru_agent, message=message.content, clear_history=False)
    logging.debug("Guru response received")
    last_message = guru_agent.last_message(user_agent).copy()
    last_message['thread_id'] = thread.id

    logging.debug("Reply Found, adding message")
    reply_message = Message(**last_message)
    reply_message.thread_id = thread.id
    session.add(reply_message)
    session.commit()
    session.refresh(reply_message)
    logging.debug("Message added, starting chat")

    # switch role last, as we are saving above
    last_message['role'] = 'guru'
    return last_message