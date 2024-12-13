import pymupdf
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from collections import defaultdict
import torch
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'/Users/lisechen/Library/Python/3.9/bin/pytesseract'

# def extract_text(pdf_path):
#     doc = pymupdf.open(pdf_path)
#     text = ""

#     for page in doc:
#         # Try using different get_text modes
#         page_text = page.get_text("text")
        
#         if not page_text.strip():  # No text found
#             print(f"No text found on page {page.number}, trying OCR...")
#             # Convert page to an image
#             pix = page.get_pixmap()
#             img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
#             page_text = pytesseract.image_to_string(img)
        
#         text += page_text

#     return text

# Specify the path to your PDF file
pdf_path = "/Users/lisechen/thesis_code/AASM_Manual2.5.pdf"
# extracted_text = extract_text(pdf_path)


# Load the pretrained NER model and tokenizer
model_name = "dbmdz/bert-large-cased-finetuned-conll03-english"  # A BERT-based model fine-tuned for NER
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# print(extracted_text)

# # Initialize the NER pipeline
# nlp_ner = pipeline("ner", model=model, tokenizer=tokenizer)

# # Split the extracted text into smaller chunks to avoid memory issues
# max_chunk_size = 512
# chunks = [extracted_text[i:i + max_chunk_size] for i in range(0, len(extracted_text), max_chunk_size)]

# # Run the NER model on each chunk
# ner_results = []
# for chunk in chunks:
#     ner_results.extend(nlp_ner(chunk))


# # Organize the recognized entities
# entities = defaultdict(list)

# for result in ner_results:
#     entity = result['entity']
#     word = result['word']
#     score = result['score']
#     start = result['start']
#     end = result['end']
    
#     entities[entity].append((word, score, start, end))

# # Display the results
# for entity, values in entities.items():
#     print(f"{entity}: {', '.join([v[0] for v in values])}")


# # Organize the recognized entities
# entities = defaultdict(list)

# for result in ner_results:
#     entity = result['entity']
#     word = result['word']
#     score = result['score']
#     start = result['start']
#     end = result['end']
    
#     entities[entity].append((word, score, start, end))

# # Display the results
# for entity, values in entities.items():
#     print(f"{entity}: {', '.join([v[0] for v in values])}")