# filename: arxiv_search.py
import urllib.request
import urllib.parse
import feedparser

# Base API query URL
base_url = 'http://export.arxiv.org/api/query?'

# Search parameters
search_query = 'all:gpt-4'  # search for the term 'gpt-4' in all fields
start = 0                     # start at the first result
max_results = 1               # maximum results to return

query = f'search_query={search_query}&start={start}&max_results={max_results}&sortBy=submittedDate&sortOrder=descending'
url = base_url + query

# Perform the GET request
with urllib.request.urlopen(url) as response:
    response_text = response.read()

# Parse the response using feedparser
feed = feedparser.parse(response_text)

# Print out information about the most recent paper
if feed.entries:
    entry = feed.entries[0]
    print(f"Title: {entry.title}")
    print(f"Authors: {', '.join(author.name for author in entry.authors)}")
    print(f"Published: {entry.published}")
    print(f"Summary: {entry.summary}")
else:
    print("No papers found on GPT-4.")