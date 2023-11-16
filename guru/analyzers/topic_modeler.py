from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import CountVectorizer

class TopicModeler:
    def __init__(self):
        self.lda_model = LatentDirichletAllocation(n_components=5)
        self.vectorizer = CountVectorizer(stop_words='english')

    def analyze_topics(self, text):
        X = self.vectorizer.fit_transform([text])
        self.lda_model.fit(X)
        doc = self.lda_model.transform(X)
        return doc

    def extract_topics(self, doc, topics, message_id):
        feature_names = self.vectorizer.get_feature_names_out()
        topics[message_id] = (feature_names, message_id)
