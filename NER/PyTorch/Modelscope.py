"""
Script to do NER using modelscope libraries (HuggingFace unavailable in China)
"""
from modelscope.pipelines import pipeline
import unicodedata
import re

input_file_path = '../../data/ICSD3_dataset.txt'

def clean_text(text):
    # Normalize unicode characters
    text = unicodedata.normalize('NFKC', text)
    # Remove unwanted special characters (example regex, customize as needed)
    text = re.sub(r'[^a-zA-Z0-9\s,.!?]', '', text)
    # Strip leading or trailing whitespace
    text = text.strip()
    return text

def prepare_texts_for_ner(texts):
    cleaned_texts = [clean_text(text) for text in texts]
    return cleaned_texts

# Function to read the input file
def read_input_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    return prepare_texts_for_ner(lines)

def apply_ner(texts):
    # ner = pipeline('named-entity-recognition', model='polyai/biobert-large-cased-v1.1')
    ner_pipeline = pipeline(task="named-entity-recognition", model='damo/nlp_raner_named-entity-recognition_english-large-ecom')
    result = ner_pipeline(texts)
    return result

# Read the input file
texts = read_input_file(input_file_path)

# Apply NER to the input texts
ner_results = apply_ner(texts)

# Print or save the results as needed
with open("output.txt", "w+") as file:
    file.write(ner_results)