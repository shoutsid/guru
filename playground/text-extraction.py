# https://github.com/openai/openai-cookbook/blob/main/examples/Entity_extraction_for_long_documents.ipynb

import tiktoken
import textract
import os
from openai import OpenAI

client = OpenAI()

# Extract the raw text from each PDF using textract
text = textract.process(
    'data/q_learning.pdf', method='pdfminer').decode('utf-8')
clean_text = text.replace("  ", " ").replace("\n", "; ").replace(';', ' ')

# Example prompt -
document = '<document>'
template_prompt = f'''Extract key pieces of information from this document. If a particular piece of information is not present, output \"Not specified\".
When you extract a key piece of information, include the closest page number. Write your answers in a numbered list. Split each page as a title. \n\nDocument: \"\"\"{document}\"\"\"\n\n0. Who is the author: \n1.'''
print(template_prompt)

# Split a text into smaller chunks of size n, preferably ending at the end of a sentence


def create_chunks(text, n, tokenizer):
    tokens = tokenizer.encode(text)
    """Yield successive n-sized chunks from text."""
    i = 0
    while i < len(tokens):
        # Find the nearest end of sentence within a range of 0.5 * n and 1.5 * n tokens
        j = min(i + int(1.5 * n), len(tokens))
        while j > i + int(0.5 * n):
            # Decode the tokens and check for full stop or newline
            chunk = tokenizer.decode(tokens[i:j])
            if chunk.endswith(".") or chunk.endswith("\n"):
                break
            j -= 1
        # If no end of sentence found, use n tokens as the chunk size
        if j == i + int(0.5 * n):
            j = min(i + n, len(tokens))
        yield tokens[i:j]
        i = j


def extract_chunk(document, template_prompt):

    prompt = template_prompt.replace('<document>', document)

    response = client.completions.create(model='text-davinci-003',
                                         prompt=prompt,
                                         temperature=1,
                                         max_tokens=1500,
                                         top_p=1,
                                         frequency_penalty=2,
                                         presence_penalty=0)
    return "1." + response.choices[0].text


# Initialise tokenizer
tokenizer = tiktoken.get_encoding("cl100k_base")

results = []

chunks = create_chunks(clean_text, 1000, tokenizer)
text_chunks = [tokenizer.decode(chunk) for chunk in chunks]

for chunk in text_chunks:
    results.append(extract_chunk(chunk, template_prompt))
    # print(chunk)
    print(results[-1])


groups = [r.split('\n') for r in results]

# zip the groups together
zipped = list(zip(*groups))
zipped = [x for y in zipped for x in y if "Not specified" not in x and "__" not in x]
print(zipped)
