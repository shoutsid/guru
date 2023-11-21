import pytest

from message_splitter import send_message_in_paragraphs


class MockMessage:
    """
    Mock message class to simulate Discord message object.
    """

    def __init__(self):
        self.channel = MockChannel()


class MockChannel:
    """
    Mock channel class to capture sent messages.
    """

    def __init__(self):
        self.messages = []

    async def send(self, content):
        self.messages.append(content)


@pytest.mark.asyncio
async def test_short_code_block():
    """
    Test that a short code block is sent as a single message.
    """
    mock_message = MockMessage()
    content = '```python\nprint("Hello, world!")\n```'
    await send_message_in_paragraphs(mock_message, content)
    assert len(mock_message.channel.messages) == 1
    assert mock_message.channel.messages[0] == content


@pytest.mark.asyncio
async def test_long_code_block():
    """
    Test that a long code block is split into multiple messages.
    """
    mock_message = MockMessage()
    content = '```' + '\n'.join(['line' + str(i) for i in range(200)]) + '```'
    await send_message_in_paragraphs(mock_message, content)
    assert len(mock_message.channel.messages) > 1
    assert all('```' in message for message in mock_message.channel.messages)


@pytest.mark.asyncio
async def test_split_non_code_text():
    """
    Test that non-code text is split correctly at sentence and word boundaries.
    """
    mock_message = MockMessage()
    content = 'This is a test message. ' * 50  # Long sentence repeated
    await send_message_in_paragraphs(mock_message, content)
    assert len(mock_message.channel.messages) > 1
    assert all(len(message) <= 1024 for message in mock_message.channel.messages)


@pytest.mark.asyncio
async def test_mixed_content():
    """
    Test that a message with mixed code blocks and text is split and sent correctly.
    """
    mock_message = MockMessage()
    content = 'Normal text. ' * 10 + \
        '```python\nprint("Code block")\n```' + ' More text.' * 10
    await send_message_in_paragraphs(mock_message, content)
    assert len(mock_message.channel.messages) > 1
