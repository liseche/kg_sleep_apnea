"""
UNFINISHED
Script that takes in type of language model, path to the same language 
model and a text file.
Generates a summarization of this text file using the language model.
"""

import argparse
import sys
import torch
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoModelForCausalLM, AutoTokenizer, AutoConfig, T5ForConditionalGeneration

if torch.cuda.is_available():
    torch.cuda.empty_cache()
    device = torch.device("cuda")
    print("CUDA is available. Using GPU.")
else:
    device = torch.device("cpu")
    print("CUDA is not available. Using CPU.")
max_seq_len = 512

def load_model(model_path):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    config = AutoConfig.from_pretrained(model_path)
    model_type = config.model_type
    print("model type:\t", model_type)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    if "google/flan-t5-xxl" in model_path:
        model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-xxl", torch_dtype=torch.bfloat16)
    elif "opt-350m" in model_path:
        model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.bfloat16)
    elif model_type in ["t5"]:
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path, torch_dtype=torch.bfloat16)
    elif model_type in ["opt", "mistral"]:
        model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.bfloat16)
    model.to(device)
    return model, model_type, tokenizer

def chunk_article(tokenizer, article_text, max_length=512):
    tokens = tokenizer.tokenize(article_text)
    chunks = [tokens[i:i + max_length] for i in range(0, len(tokens), max_length)]
    chunked_texts = [tokenizer.convert_tokens_to_string(chunk) for chunk in chunks]
    return chunked_texts

def generate_summary(model_path, text_file_path):
    prefix = "Summarize this:"
    model, model_type, tokenizer = load_model(model_path)

    with open(text_file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    if "google/flan-t5-xxl" in model_path:
        def summa(chunk):
            prompt = prefix + chunk
            prompt_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
            outputs = model.generate(prompt_ids, max_new_tokens=1000)
            return tokenizer.decode(outputs[0])
        if len(text) >= max_seq_len:
            summary = ""
            chunks = chunk_article(tokenizer=tokenizer, article_text=text)
            for ch in chunks:
                summary += summa(ch) + " "
            print(summary)
        else:
            print(summa(text))
        
    elif "opt-350m" in model_path:
        summarizer = pipeline("text-generation", model=model, tokenizer=tokenizer, device=device)
        prompt = "Summarize the following text: " + text
        summary = summarizer(prompt, max_new_tokens=1000, do_sample=False)
        # The output of text-generation pipeline is a list of dictionaries
        print(summary[0]['generated_text'].replace(prompt, '').strip())

    elif model_type in ["t5"]:
        summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, device=device)
        summary = summarizer(text, do_sample=False, max_new_tokens=1000)
        print(summary[0]['summary_text'])

    elif model_type in ["opt", "mistral"]:
        prompt = prefix + text
        if "opt-6.7b" in model_path:
            input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
            generated_ids = model.generate(input_ids, do_sample=True, max_new_tokens=1000)
            print(tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].replace(prompt, '').strip())
        else:
            summarizer = pipeline("text-generation", model=model, tokenizer=tokenizer, device=device)
            if model_type in ["mistral"]:
                prompt = "<s>[INST]" + prompt + "[/INST]"
            summary = summarizer(prompt, max_new_tokens=1000)
            # The output of text-generation pipeline is a list of dictionaries
            print(summary[0]['generated_text'].replace(prompt, '').strip())
        
    else:
        print("Model type is not identified as supported. Exiting.")
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model", help="path to language model")
    parser.add_argument("text_path", help="path to text file containing text to summarize")
    args = parser.parse_args()

    print("model:\t", args.model, "\ntext path:\t", args.text_path)

    generate_summary(args.model, args.text_path)