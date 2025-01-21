"""Script that takes in a dataset with one word per line ("word" split strategy in the MakeDatasetWOTarget script.)"""

import argparse
import spacy

def load_model(model_path):
    nlp = spacy.load(model_path)
    return nlp

def predict_and_save(nlp, path_to_input: str, path_to_output: str):
    sentences = get_sentences_from_path(path_to_input)

    with open(path_to_output, 'w', encoding='utf-8') as file:
        for sentence in sentences:
            doc = nlp(" ".join(sentence))
            
            for token in doc:
                file.write(f"{token.text}\t{token.ent_type_}\n")
            
            file.write("\n")

    print(f"NER predictions written to {path_to_output}")

def get_sentences_from_path(file_path: str):
    sentences = []
    with open(file_path, 'r', encoding='utf-8') as file:
        sentence = []
        for line in file:
            if line.strip():
                sentence.append(line.strip())
            else:
                if sentence: 
                    sentences.append(sentence)
                sentence = []
        if sentence: 
            sentences.append(sentence)
    return sentences

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='NER Prediction Script')
    parser.add_argument("--model_path", type=str, default="en_ner_bc5cdr_md", help="name or path to spaCy model")
    parser.add_argument("--input_file", type=str, default="../../data/ICSD3.tsv", help="path to tab-separated input data file")
    parser.add_argument("--output_file", type=str, default="predictions.tsv", help="path to generated output predictions")
    args = parser.parse_args()

    nlp = load_model(args.model_path)

    predict_and_save(nlp, args.input_file, args.output_file)
