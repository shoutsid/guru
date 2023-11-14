import subprocess
import sys

# Function to install spaCy model
def install_spacy_model(model_name):
    subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])
