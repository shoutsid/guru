from autogen.agentchat.user_proxy_agent import UserProxyAgent
from autogen.agentchat.assistant_agent import AssistantAgent
from settings import LLM_CONFIG

import asyncio


def get_market_news(ind, ind_upper):
    import requests
    import json
    # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
    # url = 'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&sort=LATEST&limit=5&apikey=demo'
    # r = requests.get(url)
    # data = r.json()
    # with open('market_news_local.json', 'r') as file:
    #     # Load JSON data from file
    #     data = json.load(file)
    data = {
        "feed": [
            {
                "title": "Palantir CEO Says Our Generation's Atomic Bomb Could Be AI Weapon - And Arrive Sooner Than You Think - Palantir Technologies  ( NYSE:PLTR ) ",
                "summary": "Christopher Nolan's blockbuster movie \"Oppenheimer\" has reignited the public discourse surrounding the United States' use of an atomic bomb on Japan at the end of World War II.",
                "overall_sentiment_score": 0.009687,
            },
            {
                "title": '3 "Hedge Fund Hotels" Pulling into Support',
                "summary": "Institutional quality stocks have several benefits including high-liquidity, low beta, and a long runway. Strategist Andrew Rocco breaks down what investors should look for and pitches 3 ideas.",
                "banner_image": "https://staticx-tuner.zacks.com/images/articles/main/92/87.jpg",
                "overall_sentiment_score": 0.219747,
            },
            {
                "title": "PDFgear, Bringing a Completely-Free PDF Text Editing Feature",
                "summary": "LOS ANGELES, July 26, 2023 /PRNewswire/ -- PDFgear, a leading provider of PDF solutions, announced a piece of exciting news for everyone who works extensively with PDF documents.",
                "overall_sentiment_score": 0.360071,
            },
            {
                "title": "Researchers Pitch 'Immunizing' Images Against Deepfake Manipulation",
                "summary": "A team at MIT says injecting tiny disruptive bits of code can cause distorted deepfake images.",
                "overall_sentiment_score": -0.026894,
            },
            {
                "title": "Nvidia wins again - plus two more takeaways from this week's mega-cap earnings",
                "summary": "We made some key conclusions combing through quarterly results for Microsoft and Alphabet and listening to their conference calls with investors.",
                "overall_sentiment_score": 0.235177,
            },
        ]
    }
    feeds = data["feed"][ind:ind_upper]
    feeds_summary = "\n".join(
        [
            f"News summary: {f['title']}. {f['summary']} overall_sentiment_score: {f['overall_sentiment_score']}"
            for f in feeds
        ]
    )
    return feeds_summary


async def add_stock_price_data():
    global DATA

    # simulating the data stream
    for i in range(0, 5, 1):
        latest_news = get_market_news(i, i + 1)
        if DATA.done():
            DATA.result().append(latest_news)
        else:
            DATA.set_result([latest_news])
        # print(data.result())
        await asyncio.sleep(5)


async def add_data_reply(recipient, messages, sender, config):
    await asyncio.sleep(0.1)
    data = config["news_stream"]
    if data.done():
        result = data.result()
        if result:
            news_str = "\n".join(result)
            result.clear()
            return (
                True,
                f"Just got some latest market news. Merge your new suggestion with previous ones.\n{news_str}",
            )
        return False, None


user_agent = UserProxyAgent(
    name="user",
    system_message="You are a discord_agent_user_proxy",
    is_termination_msg=lambda x: x.get("content", "") and x.get(
        "content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=3,
    # code_execution_config={
    #     "work_dir": "agent_workplace", "last_n_messages": 2},
    code_execution_config=False,
    llm_config=LLM_CONFIG,
    default_auto_reply=None,
)

assistant = AssistantAgent(
    "assistant",
    system_message="You are a financial expert.",
    is_termination_msg=lambda x: x.get("content", "") and x.get(
        "content", "").rstrip().endswith("TERMINATE"),
    llm_config=LLM_CONFIG
)


async def run():
    global DATA_TASK, DATA

    DATA = asyncio.Future()
    user_agent.register_reply(AssistantAgent, add_data_reply,
                              1, config={"news_stream": DATA})

    DATA_TASK = await add_stock_price_data()
    message = "Give me investment suggestion in 1 bullet point."
    await user_agent.a_initiate_chat(assistant, message=message, clear_history=True)
    if DATA_TASK:
        while not DATA_TASK.done() and not DATA_TASK.cancelled():
            reply = await user_agent.a_generate_reply(sender=assistant)
            if reply is not None:
                await user_agent.a_send(reply, assistant)


if __name__ == "__main__":
    asyncio.run(run())
