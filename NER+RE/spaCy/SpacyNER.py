"""
Script to do named entity recognition with Spacy. Prints out html with annotations.

Some recommended models:
    en_ner_bc5cdr_md
    en_core_med7_lg
"""

# import pandas as pd
# import numpy as np
import spacy
# import re
import chardet
# import csv
# from  spacy.matcher import Matcher
import argparse
import os

def generate_annotation(texts):
    """Generate anotation for each entities and label"""
    annotations = []
    for text in texts:
        doc = nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append((ent.start_char, ent.end_char, ent.label_))
        annotations.append((text, {'entities': entities}))
    return annotations

def extract_keywords(text):
    """This function will extract relevant entities and labels needed from medical transcription 
    """
    doc = nlp(text)
    entities = []
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities

def get_full_text_chunks(filepath:str) :
    """Get the text using the provided path.
    Arg:
        filepath (str): path to input file
    Return:
        full_text (str): full text read from the provided input file
        chunks (list[str]): list of sentences.
    """
    # Detect the encoding of the file
    with open(filepath, 'rb') as file:
        raw_data = file.read()
        encoding = chardet.detect(raw_data)
        print("Input file encoding:", encoding['encoding'])

    with open(filepath, encoding=encoding['encoding']) as file:
        full_text = file.read()
        
    with open(filepath, encoding=encoding['encoding']) as file: 
        chunks = file.readlines()
    print("Entries in chunked up text:", len(chunks))
    return full_text, chunks

# transcription_list = [re.sub(r'(\.,)', ". ", x) for x in chunks]

# output_file = "output.tsv"

# with open(output_file, mode="w", newline="") as file:
#     writer = csv.writer(file, delimiter="\t")
    
#     for item in chunks:
#         writer.writerow([item])   

# print(f"Data successfully written to {output_file}")

# nlp = spacy.load("en_core_med7_lg")

# Extract text entities and labels from the dataset (transcription)
# medical_doc = chunks

# Let's generate annotations
# annotations = generate_annotation(medical_doc)

# Let's print documents and annotations
# print(f"Number of lines with annotations: {len(annotations)}")
# print("Document:")
# print(annotations[0][0]) # first document text
# print("Annotations:")
# print(annotations[0][1]) # annotation for the first document

def make_labelled_html(doc: spacy.Language, filename:str, path:str):
    # Create distict colours for labels
    col_dict = {}
    s_colours = ['#e6194B', '#3cb44b', '#ffe119', '#ffd8b1', '#f58231', '#f032e6', '#42d4f4']
    for label, colour in zip(nlp.pipe_labels['ner'], s_colours):
        col_dict[label] = colour

    options = {'ents': nlp.pipe_labels['ner'], 'colors':col_dict}

    html = spacy.displacy.render(doc, style = 'ent', jupyter=False, options = options)

    html_filename = path + "/annotated_" + filename.split(".")[0] + ".html"
    with open(html_filename, "w+") as file:
        file.write(html)

    # [(ent.text, ent.label_) for ent in doc.ents]

# # Let's load the model
# nlp = spacy.load("en_core_med7_lg")

# patterns = [
#     [{"ENT_TYPE": "DRUG"}, {"LIKE_NUM": True}, {"IS_ASCII": True}],
#     [{"LOWER": {"IN": ["mg", "g", "ml"]}}, {"ENT_TYPE": "DRUG"}],
#     [{"ENT_TYPE": "DRUG"}, {"IS_DIGIT": True, "OP": "?"}, {"LOWER": {"IN": ["mg", "g", "ml"]}}]
# ]

# matcher = Matcher(nlp.vocab)
# matcher.add("DRUG_DOSE", patterns)

# for transcription in  chunks:
#     doc = nlp(transcription)
#     matches = matcher(doc)
#     for match_id, start, end in matches:
#         string_id = nlp.vocab.strings[match_id]
#         span = doc[start:end]
#         print(string_id, start, end, span.text)

# Let's load our pretrained spacy model

# nlp = spacy.load("en_core_med7_lg")

# # Lets define our categories
# surgery_keywords = ["surgery", "operation", "procedure", "acute Cholangitis", "surgisis", "appendicitis"]
# cardio_pul_keywords = ["heart", "cardiovascular", "pulmonary", "lungs"]
# orthopaedic_keywords = ["orthopaedic", "bone", "joint", "fracture"]
# neurology_keywords = ["neurology", "nervours system", "brain", "nerve"]
# general_med_keywords = ["patient", "complaining", "history", "medical"]
    
# # This will process each medical description and check for relevant keywords
# medical_doc = chunks
# for transcription in medical_doc:
#     entities = extract_keywords(transcription.lower())
    
#     is_surgery = any(keyword in transcription.lower() for keyword in surgery_keywords)
#     is_cardio_pul = any(keyword in transcription.lower() for keyword in cardio_pul_keywords)
#     is_orthopaedic = any(keyword in transcription.lower() for keyword in orthopaedic_keywords)
#     is_neurology = any(keyword in transcription.lower() for keyword in neurology_keywords)
#     is_general_med = any(keyword in transcription.lower() for keyword in general_med_keywords)
    
#     print("Transcription:", transcription)
#     print("Entities:", entities)
#     print("Is Surgery:", is_surgery)
#     print("Is Cardio Pulmonary:", is_cardio_pul)
#     print("Orthopaedic:", is_orthopaedic)
#     print("Neurology:", is_neurology)
#     print("General Medicine:", is_general_med)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script to do NER with Spacy.")
    
    parser.add_argument(
        '--input_file',
        type=str,
        required=True,
        help="Path to dataset with each input entry on each line."
    )
    parser.add_argument(
        '--dataset_name',
        type=str,
        default="",
        help="Name of the dataset used, to be used in filenames for generated files containing annotations."
    )
    parser.add_argument(
        '--model',
        type=str,
        default="en_core_med7_lg",
        help="Spacy model to use for NER."
    )
    args = parser.parse_args()
    full_text, chunks = get_full_text_chunks(args.input_file)
    print("Input file path: ", args.input_file)
    try:
        nlp = spacy.load(args.model)
    except OSError:
        print(f"Model '{args.model}' is not installed. Please download it using: \npython -m spacy download {args.model}")
        exit(-1)
    print("Model used: ", args.model)
    print("NER labels: ", nlp.pipe_labels['ner'])
    transcription = full_text
    doc = nlp(transcription)
    import os

    # Define the path where you want to create a new directory
    directory_path = args.model + "_" + args.dataset_name

    # Create the directory
    # The exist_ok parameter ensures that no error is raised if the directory already exists
    os.makedirs(directory_path, exist_ok=True)

    print(f"Directory '{directory_path}' created successfully.")
    make_labelled_html(doc, args.dataset_name, directory_path)