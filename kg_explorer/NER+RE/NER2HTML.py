"""
Script to do named entity recognition with Spacy. Prints out html with annotations.

Some recommended models:
    en_ner_bc5cdr_md
    en_core_med7_lg
"""

import spacy
import chardet
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