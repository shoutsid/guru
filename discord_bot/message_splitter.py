import re


async def send_message_in_paragraphs(message, content):
    """
    Splits a large message into chunks suitable for Discord, ensuring each chunk is no more than 1024 characters.
    Code blocks and non-code text are handled separately to preserve their integrity.
    :param message: The message object to reply to
    :param content: The large content string to be sent
    """

    MAX_LENGTH = 1024  # Discord's max message length
    code_block_pattern = r'```[\s\S]*?```'  # Pattern to match code blocks

    def split_code_block(block):
      """
      Splits a long code block into multiple chunks, each within the Discord message length limit.
      Now ensures no extra newline is added at the end of the block.
      """
      lines = block.split('\n')
      chunks = []
      current_chunk = ''
      for line in lines:
          if len(current_chunk) + len(line) + 1 <= MAX_LENGTH:
              current_chunk += line + '\n'
          else:
              # Remove the trailing newline for the last line in the chunk
              if current_chunk.endswith('\n'):
                  current_chunk = current_chunk[:-1]
              chunks.append(current_chunk)
              current_chunk = line + '\n'
      # Ensure no extra newline at the end of the last chunk
      if current_chunk.endswith('\n'):
          current_chunk = current_chunk[:-1]
      if current_chunk:
          chunks.append(current_chunk)
      return chunks

    def split_code_blocks(text):
        """
        Splits the text into a list of strings where each string is either a code block or a non-code block substring.
        Handles splitting long code blocks into smaller chunks.
        """
        chunks = []
        start = 0
        for match in re.finditer(code_block_pattern, text):
            if match.start() > start:
                chunks.extend(split_text(text[start:match.start()]))
            code_block_chunks = split_code_block(match.group())
            chunks.extend(code_block_chunks)
            start = match.end()
        if start < len(text):
            chunks.extend(split_text(text[start:]))
        return chunks

    def split_text(text):
        """
        Splits non-code block text into chunks, each within the Discord message length limit.
        """
        words = text.split()
        chunks = []
        current_chunk = ''
        for word in words:
            if len(current_chunk) + len(word) + 1 <= MAX_LENGTH:
                current_chunk += (word + ' ')
            else:
                chunks.append(current_chunk)
                current_chunk = word + ' '
        if current_chunk:
            chunks.append(current_chunk)
        return chunks

    async def send_chunks(chunks):
        """
        Sends the chunks as separate messages.
        """
        for chunk in chunks:
            await message.channel.send(chunk)

    chunks = split_code_blocks(content)
    await send_chunks(chunks)
