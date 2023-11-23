import os
import json
import pandas as pd
import numpy as np
import re
import nltk
import spacy
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob import TextBlob
from gensim import corpora, models
from collections import Counter

import openai

# Initialize NLTK and Spacy resources
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('vader_lexicon')
if not spacy.util.is_package('en_core_web_sm'):
    spacy.cli.download('en_core_web_sm')
nlp = spacy.load('en_core_web_sm')

def clean_text(text):
    # Convert text to lowercase
    text = text.lower()
    # Remove non-alphabetic characters
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

def tokenize_text(text):
    # Tokenization
    tokens = nltk.word_tokenize(text)
    return tokens

def remove_stopwords(tokens):
    # Stopword Removal
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return filtered_tokens

def lemmatize_tokens(tokens):
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return lemmatized_tokens

def preprocess_text(text):
    cleaned_text = clean_text(text)
    tokens = tokenize_text(cleaned_text)
    filtered_tokens = remove_stopwords(tokens)
    lemmatized_tokens = lemmatize_tokens(filtered_tokens)
    cleaned_text = ' '.join([word for word in lemmatized_tokens if len(word) > 2])
    return cleaned_text

def analyze_sentiment(text):
    # Sentiment Analysis
    sentiment = TextBlob(text).sentiment.polarity
    return sentiment

def tfidf_vectorize(texts):
    # TF-IDF Vectorization
    # Limiting to the top 1000 features
    tfidf_vectorizer = TfidfVectorizer(max_features=1000)
    tfidf_matrix = tfidf_vectorizer.fit_transform(texts)
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(),
                            columns=tfidf_vectorizer.get_feature_names_out())
    return tfidf_df

def build_lda_model(tokens):
    # Create a dictionary and corpus
    dictionary = corpora.Dictionary(tokens)
    corpus = [dictionary.doc2bow(tokens) for tokens in tokens]

    # Build the LDA model
    lda_model = models.LdaModel(corpus, num_topics=2, id2word=dictionary, passes=15)
    return dictionary, lda_model  # Return both dictionary and lda_model

def extract_named_entities(text):
    # Extract named entities using Spacy
    doc = nlp(text)
    named_entities = [(ent.text, ent.label_) for ent in doc.ents]
    return named_entities

def calculate_personality_scores(text):
    # Perform analysis and return personality scores
    return {
        'Openness': 0.6,
        'Conscientiousness': 0.4,
        'Extraversion': 0.5,
        'Agreeableness': 0.3,
        'Neuroticism': 0.7
    }

from nltk.sentiment.vader import SentimentIntensityAnalyzer

def extract_likes_and_dislikes(text):
    # Initialize the VADER sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    # Tokenize the text
    tokens = nltk.word_tokenize(text)

    likes = []
    dislikes = []

    for token in tokens:
        # Get sentiment score for each token
        sentiment_score = analyzer.polarity_scores(token)['compound']

        # Define a threshold (you can adjust this as needed)
        threshold = 0.2

        if sentiment_score > threshold:
            likes.append(token)
        elif sentiment_score < -threshold:
            dislikes.append(token)

    return likes, dislikes

def generate_synthetic_sentences(prompt, num_samples=100, save_interval=10, save_file="synthetic_data.json"):
    # Check if the data file already exists
    if os.path.exists(save_file):
        with open(save_file, 'r') as file:
            synthetic_data = json.load(file)
    else:
        synthetic_data = {"review_id": [], "text": []}

    num_existing_samples = len(synthetic_data["review_id"])
    # get the number of samples to generate
    num_samples = num_samples - num_existing_samples

    for i in range(num_existing_samples + 1, num_samples + 1):
        client = openai.OpenAI()
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a assistant that generates a wide range of mixed customer reviews, not all are positive or negative"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,  # Adjust the max_tokens based on desired sentence length
            temperature=0.7,  # Adjust the temperature for creativity
        )
        synthetic_sentence = chat_completion.choices[0].message.content.strip()

        # Add the synthetic sentence to the data dictionary
        synthetic_data["review_id"].append(i)
        synthetic_data["text"].append(synthetic_sentence)
        print(f"Generated sentence {i}: {synthetic_sentence}")
        print(f"Total number of sentences generated: {len(synthetic_data['review_id'])} / {num_samples}")

        # Periodically save the data
        if i % save_interval == 0:
            with open(save_file, 'w') as file:
                json.dump(synthetic_data, file)

    # Final save of the synthetic data
    with open(save_file, 'w') as file:
        json.dump(synthetic_data, file)

    return synthetic_data
prompt = "Generate a customer review for a product with variations of mood, sentiment personality, likes dislikes and named entities all involved:"

data = generate_synthetic_sentences(prompt, num_samples=100)

df = pd.DataFrame(data)

# Data Cleaning and Preprocessing
df['cleaned_text'] = df['text'].apply(preprocess_text)

# Sentiment Analysis
df['sentiment'] = df['cleaned_text'].apply(analyze_sentiment)


df['lemmatized_tokens'] = df['cleaned_text'].apply(tokenize_text)  # Replace 'tokenize_text' with your desired tokenization function

# TF-IDF Vectorization
tfidf_df = tfidf_vectorize(df['cleaned_text'])

# Combine the original DataFrame with the extracted features
df = pd.concat([df, tfidf_df], axis=1)

# LDA Topic Modeling
dictionary, lda_model = build_lda_model(df['lemmatized_tokens'])  # Get dictionary and lda_model
df['topic_probabilities'] = df['lemmatized_tokens'].apply(lambda tokens: lda_model[dictionary.doc2bow(tokens)])

# Personality Scores
df['personality_scores'] = df['cleaned_text'].apply(calculate_personality_scores)

# Likes and Dislikes
df['likes'], df['dislikes'] = zip(*df['cleaned_text'].apply(extract_likes_and_dislikes))

# Named Entities
df['named_entities'] = df['cleaned_text'].apply(extract_named_entities)


# Display the updated DataFrame
print(df)

import matplotlib
matplotlib.use('TkAgg')  # Use an interactive backend (e.g., TkAgg)
import matplotlib.pyplot as plt

plt.hist(df['sentiment'], bins=10, color='skyblue')
plt.xlabel('Sentiment Score')
plt.ylabel('Frequency')
plt.title('Sentiment Analysis Distribution')
plt.show()

likes_text = ' '.join(df['likes'].explode().dropna())
dislikes_text = ' '.join(df['dislikes'].explode().dropna())

# Word cloud for likes
wordcloud_likes = WordCloud(width=800, height=400, background_color='white').generate(likes_text)
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud_likes, interpolation='bilinear')
plt.title('Word Cloud for Likes')
plt.axis('off')
plt.show()

# Word cloud for dislikes
wordcloud_dislikes = WordCloud(width=800, height=400, background_color='white').generate(dislikes_text)
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud_dislikes, interpolation='bilinear')
plt.title('Word Cloud for Dislikes')
plt.axis('off')
plt.show()



named_entities_list = df['named_entities'].explode().dropna()
named_entities_count = Counter(named_entities_list)
top_entities = named_entities_count.most_common(10)  # Get the top 10 named entities

entities, counts = zip(*top_entities)

# Convert entities to strings
entities = [str(entity) for entity in entities]

plt.figure(figsize=(12, 6))
plt.barh(entities, counts, color='skyblue')
plt.xlabel('Frequency')
plt.ylabel('Named Entities')
plt.title('Top Named Entities')
plt.gca().invert_yaxis()  # Reverse the order for better readability
plt.show()