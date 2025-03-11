"""Script that takes in a dataset with one word per line ("word" split strategy in the MakeDatasetWOTarget script.)"""

import argparse
import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer, AutoConfig
from kg_explorer.utils import get_sentences_from_path

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
entity_labels = ["SYMPTOM", "CONDITION", "RISKFACTOR", "TEST", "TREATMENT", "OUTCOME", "CONCEPT", "DOCUMENT"]

def load_model(model_path):
    if model_path == "knowledgator/gliner-multitask-large-v0.5":
        from gliner import GLiNER
        model = GLiNER.from_pretrained("knowledgator/gliner-multitask-large-v0.5")
        return None, model
    else:    
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        config = AutoConfig.from_pretrained(model_path)
        model = AutoModelForTokenClassification.from_config(config)
        model.to(device)
        model.eval()
        return tokenizer, model
    
def list2D_to_string(list2D):
    string = " \n".join(" ".join(list1D) for list1D in list2D)
    return string

def annotated_line(word:str, label:str):
    if word.strip() is None:
        return ""
    if word.strip() == "":
        return ""
    ret = word + "\t" + label + "\n"
    return ret

def create_batches(sentences:list, max_size):
    batches = []
    batch = []
    
    for sentence in sentences:
        if len(batch) + len(sentence) < max_size:
            batch = batch + sentence
        elif len(sentence) >= max_size:
            if len(batch) > 0:
                batches.append(batch)
                batch = []
            whole_splits = (len(sentence) // max_size)
            for i in range(whole_splits):
                batches.append(sentence[i*max_size : (i+1)*max_size])
            batches.append(sentence[whole_splits*max_size:])
        else:
            batches.append(batch)
            batch = []
            batch = batch + sentence
            
    if len(batch) > 0:
        batches.append(batch)
    
    return batches

def predict_and_save(model, tokenizer, path_to_input : str, path_to_output : str, batch_size : int, model_path : str = ""):
    sentences = get_sentences_from_path(path_to_input)
    
    if model_path == "knowledgator/gliner-multitask-large-v0.5":
        
        with open(path_to_output, 'w+', encoding='utf-8') as file:
            batches_list = create_batches(sentences, 80)
            
            for batch in batches_list:
                
                batch_as_string = " ".join(batch)
                entities = model.predict_entities(batch_as_string, entity_labels)
                
                pointer = 0
                for entity in entities:
                    outside = batch_as_string[pointer:entity["start"]]
                    outside_words = outside.split(" ")
                    for word in outside_words:
                        file.write(annotated_line(word, ""))
                    inside = entity["text"].split(" ")
                    for word in inside:
                        file.write(annotated_line(word, entity["label"]))
                    pointer = entity["end"]

                rest = batch_as_string[pointer:]
                rest = rest.split(" ")
                for word in rest:
                    file.write(annotated_line(word, ""))

    else:
        batch_sentences = [sentences[i:i + batch_size] for i in range(0, len(sentences), batch_size)]
        id2label = model.config.id2label
        # rest within else clause is partly written by ChatGPT (original code was missing a chunk)
        with open(path_to_output, 'w+', encoding='utf-8') as file:
            for batch in batch_sentences:
                encoding = tokenizer(batch, max_length=512, padding=True, truncation=True, 
                                    return_tensors="pt", is_split_into_words=True, stride=50)
                input_ids, attention_mask = encoding['input_ids'].to(device), encoding['attention_mask'].to(device)

                with torch.no_grad():
                    outputs = model(input_ids, attention_mask=attention_mask)
                    predictions = torch.argmax(outputs.logits, dim=-1)

                for i, (sentence, preds) in enumerate(zip(batch, predictions)):
                    word_ids = encoding.word_ids(batch_index=i)  # map subwords to words
                    previous_word_id = None
                    word_preds = {}

                    for token_idx, word_id in enumerate(word_ids):
                        if word_id is None:
                            continue  # skip special tokens

                        if word_id != previous_word_id:  # first subword of the word
                            word_preds[word_id] = id2label.get(preds[token_idx].item(), "O")

                        previous_word_id = word_id  # track word ID for subword aggregation

                    # Write output
                    for idx, word in enumerate(sentence):
                        label = word_preds.get(idx, "O")  # default to 'O' if missing
                        file.write(f"{word}\t{label}\n")
                    file.write("\n")

    print(f"NER predictions written to {path_to_output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NER Prediction Script")
    parser.add_argument("--model_path", type=str, default="knowledgator/gliner-multitask-large-v0.5", help="path to trained NER model")
    parser.add_argument("--input_file", type=str, default="../../data/ICSD3.tsv", help="path to tab-separated input data file")
    parser.add_argument("--output_file", type=str, default="knowledgator_gliner-multitask-large-v0.5.tsv", help="path to generated output predictions")
    parser.add_argument("--batch_size", type=int, default=8, help="size of batches to process input data in, for parallelization")
    args = parser.parse_args()
    tokenizer, model = load_model(args.model_path)

    predict_and_save(model, tokenizer, args.input_file, args.output_file, args.batch_size, model_path=args.model_path)