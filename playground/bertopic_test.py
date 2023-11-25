# https://github.com/MaartenGr/BERTopic
from bertopic import BERTopic
from bertopic.representation import KeyBERTInspired
from sklearn.datasets import fetch_20newsgroups

print("Loading 20 newsgroups dataset... This can take a while...")
docs = fetch_20newsgroups(subset='all',  remove=(
    'headers', 'footers', 'quotes'))['data']

representation_model = KeyBERTInspired()
topic_model = BERTopic(representation_model=representation_model)

print("Fitting BERTopic model...")
topics, probs = topic_model.fit_transform(docs)
print("Done!")

print("Topics:")
print(topic_model.get_topic_info())

print("Documents:")
print(topic_model.get_document_info(docs))
