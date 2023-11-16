import spacy
from .utils import install_spacy_model

try:
    _ = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading and installing spaCy model 'en_core_web_sm'...")
    install_spacy_model("en_core_web_sm")


class EntityAnalyzer:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def analyze_entities(self, text):
        doc = self.nlp(text)
        return doc

    @staticmethod
    def extract_entities(doc, entities, message_id):
        for ent in doc.ents:
            entities[ent.text] = (ent.label_, message_id)