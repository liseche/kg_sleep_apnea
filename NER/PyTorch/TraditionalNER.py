import argparse
import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer, AutoConfig

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model(model_path):
    tokenizer = AutoTokenizer.from_pretrained(model_path, truncation=True)
    config = AutoConfig.from_pretrained(model_path)
    model = AutoModelForTokenClassification.from_config(config)
    model.to(device)
    model.eval()
    return tokenizer, model

def predict_and_save(model, tokenizer, path_to_input : str, path_to_output : str, batch_size : int):
    id2label = model.config.id2label
    sentences = get_sentences_from_path(path_to_input)

    batch_sentences = [sentences[i:i + batch_size] for i in range(0, len(sentences), batch_size)]
    
    with open(path_to_output, 'w', encoding='utf-8') as file:
        for batch in batch_sentences:
            encoding = tokenizer(batch, max_length=512, padding=True, truncation=True, return_tensors="pt", is_split_into_words=True)
            input_ids, attention_mask = encoding['input_ids'].to(device), encoding['attention_mask'].to(device)

            with torch.no_grad():
                outputs = model(input_ids, attention_mask=attention_mask)
                predictions = torch.argmax(outputs.logits, dim=-1)
            
            for i, (sentence, preds) in enumerate(zip(batch, predictions)):
                word_preds = [id2label[pred.item()] for pred in preds if pred.item() in id2label]
                for word, label in zip(sentence, word_preds):
                    file.write(f"{word}\t{label}\n")
                file.write("\n")

    print(f"NER predictions written to {path_to_output}")

def get_sentences_from_path(file_path : str):
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
    parser.add_argument("--model_path", type=str, default="alvaroalon2/biobert_diseases_ner", help="path to trained NER model")
    parser.add_argument("--input_file", type=str, default="data/ICSD3.tsv", help="path to tab-separated input data file")
    parser.add_argument("--output_file", type=str, default="predictions.tsv", help="path to generated output predictions")
    parser.add_argument("--batch_size", type=int, default=32, help="size of batches to process input data in, for parallelization")
    args = parser.parse_args()
    tokenizer, model = load_model(args.model_path)

    predict_and_save(model, tokenizer, args.input_file, args.output_file, args.batch_size)