from transformers import BertTokenizer, BertForTokenClassification
import pandas as pd
import numpy as np
import en_ner_bc5cdr_md
import en_core_med7_lg

# Load pre-trained BERT tokenizer and model for NER
model_name = "dmis-lab/biobert-base-cased-v1.2"
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertForTokenClassification.from_pretrained(model_name)

filename = "data/aasm_manual_v25 spell corrected.txt"
with open(filename) as file:
    text = file.read()

def split_text(text, max_length=400):
    words = text.split()
    return [' '.join(words[i:i + max_length]) for i in range(0, len(words), max_length)]

chunks = split_text(text)
    
tokenized_chunks = [tokenizer(chunk, return_tensors="pt", truncation=True, padding=True) for chunk in chunks]


# print(tokenized_output)
# Load the NER pipeline using the tokenizer and model
# ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

# prompt = "Sleep apnea is a disease about [MASK]."

# # Use the NER pipeline on the file content
# ner_results = ner_pipeline(text)

# with open("NE.txt", "w") as f:
#     json.dump(ner_results, f, indent=4)


# # Use a pre-trained model for relation extraction (this one uses a text-to-text approach)
# re_tokenizer = AutoTokenizer.from_pretrained("allenai/PRIMERA")
# re_model = AutoModelForSeq2SeqLM.from_pretrained("allenai/PRIMERA")

# # Prepare the input by tokenizing the file text for RE
# inputs = re_tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=512)

# # Get the outputs from the model
# outputs = re_model.generate(inputs.input_ids)

# # Decode the output to get the extracted relations
# decoded_output = re_tokenizer.decode(outputs[0], skip_special_tokens=True)
# f = open("R.txt", "w")
# f.write(str(decoded_output))
# f.close()
