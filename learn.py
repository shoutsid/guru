import logging

from townhall.helpers.conversation_analyzer import *
from townhall.db.utils import Session, SQL_ENGINE

logging.basicConfig(level=logging.DEBUG)

session = Session(SQL_ENGINE)
conversation_analyzer = ConversationAnalyzer()
messages = session.exec(select(Message).where(Message.thread_id == 1)).all()
messages = convert_db_messages_to_dict(messages)
logging.debug("Messages:")
logging.debug(messages)

analysis_result = conversation_analyzer.analyze_conversation(messages)
logging.debug("Analysis result:")
logging.debug(analysis_result)
conversation_analyzer.save_analysis_results(analysis_result, session)
retrieved_results = conversation_analyzer.retrieve_analysis_results(session)
logging.info("Retrieved results:")
logging.info(retrieved_results)