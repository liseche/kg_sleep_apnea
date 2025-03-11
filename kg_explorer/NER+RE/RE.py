"""
Script to do relationship extraction on named entities.

Requires a script with NER annotations made on the conll format, with one column for tokens, and one other column with annotation,.

ChatGPT help.

"""

import argparse
import math
from transformers import pipeline
from kg_explorer.utils import make_dataframe
from kg_explorer.config import annotated_lines_icsd3
import pandas as pd
from tqdm import tqdm
from neo4j import GraphDatabase

# Neo4j Connection Details (Update with your credentials)
NEO4J_URI = "bolt://localhost:7687"  # Change this if using a cloud instance
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "REMOVED"

# Create Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# Load REBEL for Relation Extraction
triplet_extractor = pipeline('text2text-generation', model='Babelscape/rebel-large', tokenizer='Babelscape/rebel-large')

def insert_entity(tx, entity, entity_type):
    """
    Insert a named entity into Neo4j if it does not exist.
    """
    query = """
    MERGE (n:Entity {name: $entity})
    SET n.type = $entity_type
    RETURN n
    """
    tx.run(query, entity=entity, entity_type=entity_type)

def insert_relation(tx, entity1, relation, entity2):
    """
    Insert a relationship between two entities into Neo4j.
    """
    query = """
    MATCH (a:Entity {name: $entity1})
    MATCH (b:Entity {name: $entity2})
    MERGE (a)-[:RELATION {type: $relation}]->(b)
    """
    tx.run(query, entity1=entity1, entity2=entity2, relation=relation)

def chunk_large_text(text, max_tokens=100, overlap=10):
    """
    Splits a single large text into chunks of max_tokens size with overlap.
    Uses a generator to avoid storing all chunks in memory.
    Ensures no missing words & tracks chunk positions.
    """
    words = text.split()
    total_chunks = math.ceil((len(words) - overlap) / (max_tokens - overlap))  # ✅ Corrected total_chunks estimation
    processed_words = set()
    start = 0

    with tqdm(total=total_chunks, desc="Chunking Progress", unit="chunk") as pbar:
        while start < (len(words) - overlap):
            end = min(start + max_tokens, len(words))
            chunk = words[start:end]
            
            # Track processed words for validation
            processed_words.update(chunk)

            print(f"Chunk {pbar.n + 1}: {start} → {end} (Words: {len(chunk)})")  # ✅ Debug: Track chunk positions

            yield " ".join(chunk)  # ✅ Yield one chunk at a time
            start = end - overlap  # ✅ Maintain overlap

            pbar.update(1)  # ✅ Update progress bar

    # Debug: Check if all words were covered
    missing_words = set(words) - processed_words
    if missing_words:
        print("⚠ WARNING: Some words were not processed!", missing_words)
    else:
        print("✅ All words processed successfully!")

def process_large_text(text, max_tokens=100, overlap=10):
    """
    Processes a large single text efficiently in batches using REBEL.
    Ensures every chunk is processed correctly.
    """
    results = []
    words = text.split()
    total_chunks = math.ceil((len(words) - overlap) / (max_tokens - overlap))  # ✅ Corrected total_chunks estimation

    with tqdm(total=total_chunks, desc="Processing Chunks", unit="chunk") as pbar:
        for chunk in chunk_large_text(text, max_tokens=max_tokens, overlap=overlap):
            # Ensure chunk is within REBEL's token limit
            num_tokens = len(chunk.split())  # Simple estimate (could use tokenizer)
            if num_tokens > 1024:
                print(f"⚠ WARNING: Chunk too long ({num_tokens} tokens)! Adjusting...")

            extracted_text = triplet_extractor(chunk, return_tensors=True, return_text=False)  # ✅ Enable truncation
            results.extend(outputs)
            pbar.update(1)  # ✅ Update progress

    return results


# We need to use the tokenizer manually since we need special tokens.
extracted_text = triplet_extractor.tokenizer.batch_decode([triplet_extractor("Punta Cana is a resort town in the municipality of Higuey, in La Altagracia Province, the eastern most province of the Dominican Republic", return_tensors=True, return_text=False)[0]["generated_token_ids"]])
print(extracted_text[0])
# Function to parse the generated text and extract the triplets
def extract_triplets(text):
    triplets = []
    relation, subject, relation, object_ = '', '', '', ''
    text = text.strip()
    current = 'x'
    for token in text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").split():
        if token == "<triplet>":
            current = 't'
            if relation != '':
                triplets.append({'head': subject.strip(), 'type': relation.strip(),'tail': object_.strip()})
                relation = ''
            subject = ''
        elif token == "<subj>":
            current = 's'
            if relation != '':
                triplets.append({'head': subject.strip(), 'type': relation.strip(),'tail': object_.strip()})
            object_ = ''
        elif token == "<obj>":
            current = 'o'
            relation = ''
        else:
            if current == 't':
                subject += ' ' + token
            elif current == 's':
                object_ += ' ' + token
            elif current == 'o':
                relation += ' ' + token
    if subject != '' and relation != '' and object_ != '':
        triplets.append({'head': subject.strip(), 'type': relation.strip(),'tail': object_.strip()})
    return triplets
extracted_triplets = extract_triplets(extracted_text[0])
print(extracted_triplets)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Relationship Extraction With CoNLL NER File")
    
    parser.add_argument(
        "--ner_file",
        type=str,
        # default="outputs_ICSD3_NER/dmis-lab_biobert-base-cased-v1.1.tsv",
        default="kg_explorer/NER+RE/outputs_ICSD3_NER/dmis-lab_biobert-base-cased-v1.1.tsv",
        help="path to file containing NER annotations on CoNLL format (first column for tokens, and second column for annotations)"
    )
    
    args = parser.parse_args()
    df = make_dataframe(args.ner_file)
    filtered_df = pd.DataFrame()
    for indices in annotated_lines_icsd3:
        i = indices[0]
        j = indices[1]
        filtered_df = pd.concat([filtered_df, df[i:j+1]])
    
    text = " ".join(filtered_df[0].tolist())
    entity_df = filtered_df[filtered_df[1].notna() & (filtered_df[1] != "") & (filtered_df[1] != "LABEL_0")]

    named_entities_text = " ".join(entity_df[0].tolist())
    relations = process_large_text(named_entities_text, max_tokens=100, overlap=10)
    
    # Output extracted relations
    for relation in relations:
        print(relation)