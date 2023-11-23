import spacy.cli
import spacy
from gensim import corpora, models
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob import TextBlob
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Sample data (customer reviews)
data = {
    'review_id': [1, 2, 3, 4, 5],
    'text': [
        "I love this product! It's amazing!!!",
        "Not happy with the quality. Will not buy again.",
        "The service was excellent, but the product is average.",
        "Delivery was late, and the item was damaged.",
        "Great value for the price! Highly recommended."
    ]
}

df = pd.DataFrame(data)

# Data Cleaning
df['text'] = df['text'].str.lower()  # Convert text to lowercase
# Remove non-alphabetic characters
df['text'] = df['text'].apply(lambda x: re.sub(r'[^a-zA-Z\s]', '', x))

# Tokenization
nltk.download('punkt')
df['tokens'] = df['text'].apply(nltk.word_tokenize)

# Stopword Removal
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
df['filtered_tokens'] = df['tokens'].apply(
    lambda tokens: [word for word in tokens if word not in stop_words])

# Lemmatization
nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()
df['lemmatized_tokens'] = df['filtered_tokens'].apply(
    lambda tokens: [lemmatizer.lemmatize(word) for word in tokens])

# Removing Short Words
df['cleaned_text'] = df['lemmatized_tokens'].apply(
    lambda tokens: ' '.join([word for word in tokens if len(word) > 2]))

# Handling Missing Data (if any)
df.dropna(inplace=True)

# Adding Features
df['word_count'] = df['tokens'].apply(len)  # Word count in each review

# Encoding Categorical Variables (if any)

# Scaling/Normalizing Numeric Features (if any)

# Handling Outliers (if any)

# Final DataFrame
print(df[['review_id', 'cleaned_text', 'word_count']])


# Sentiment Analysis
df['sentiment'] = df['cleaned_text'].apply(
    lambda text: TextBlob(text).sentiment.polarity)

# TF-IDF Vectorization
# Limiting to the top 1000 features
tfidf_vectorizer = TfidfVectorizer(max_features=1000)
tfidf_matrix = tfidf_vectorizer.fit_transform(df['cleaned_text'])
tfidf_df = pd.DataFrame(tfidf_matrix.toarray(),
                        columns=tfidf_vectorizer.get_feature_names_out())

# Combine the original DataFrame with the extracted features
df = pd.concat([df, tfidf_df], axis=1)

# Display the updated DataFrame
print(df)


df['sentiment'] = df['cleaned_text'].apply(
    lambda x: TextBlob(x).sentiment.polarity)

# Create a dictionary and corpus
dictionary = corpora.Dictionary(df['lemmatized_tokens'])
corpus = [dictionary.doc2bow(tokens) for tokens in df['lemmatized_tokens']]

# Build the LDA model
lda_model = models.LdaModel(
    corpus, num_topics=2, id2word=dictionary, passes=15)

# Extract topic probabilities for each review
df['topic_probabilities'] = df['lemmatized_tokens'].apply(
    lambda tokens: lda_model[dictionary.doc2bow(tokens)])


def personality_score(text):
    # Perform analysis and return personality scores
    return {
        'Openness': 0.6,
        'Conscientiousness': 0.4,
        'Extraversion': 0.5,
        'Agreeableness': 0.3,
        'Neuroticism': 0.7
    }


df['personality_scores'] = df['cleaned_text'].apply(personality_score)

df['likes'] = df['cleaned_text'].apply(
    lambda x: [word for word in x.split() if word in ['love', 'like']])
df['dislikes'] = df['cleaned_text'].apply(
    lambda x: [word for word in x.split() if word in ['hate', 'dislike']])


# Calculate average word count
avg_word_count = df['word_count'].mean()

# Calculate average sentiment score
avg_sentiment = df['sentiment'].mean()

# Calculate average response time (assuming you have timestamps)
# df['timestamp'] = pd.to_datetime(df['timestamp'])
# df['time_diff'] = df['timestamp'].diff()
# avg_response_time = df['time_diff'].mean()


if not spacy.util.is_package('en_core_web_sm'):
    spacy.cli.download('en_core_web_sm')

nlp = spacy.load('en_core_web_sm')
df['named_entities'] = df['cleaned_text'].apply(
    lambda x: [(ent.text, ent.label_) for ent in nlp(x).ents])

print(df)
