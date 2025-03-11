"""
Script to use the knowledge graph maker library.

Prerequisites to run:
- knowledge_graph_maker library
- neo4j running at port neo4j://localhost:7687
- a .env file in the same directory as this file, with login values.
- a input file with dataset generated with WORD split strategy.
- a list of annotated lines, like in shared.py
"""
from knowledge_graph_maker import GraphMaker, Ontology, GroqClient
from knowledge_graph_maker import Document
from neo4j import GraphDatabase
import datetime
from knowledge_graph_maker import Neo4jGraphModel
from dotenv import dotenv_values, load_dotenv
import os
from concurrent.futures import ThreadPoolExecutor 
import time
import sys
sys.path.append("/Users/lisechen/thesis_code")
from kg_explorer.config import annotated_lines_icsd3

start_time = time.time()
input_file = "../../data/ICSD3.tsv"

def generate_summary(text):
    SYS_PROMPT = (
        "Succintly summarise the text provided by the user. "
        "Respond only with the summary and no other comments"
    )
    try:
        summary = llm.generate(user_message=text, system_message=SYS_PROMPT)
    except:
        summary = ""
    finally:
        return summary


def create_document(text):
    """Function to create a Document instance (object necessary for the knowledge_graph_maker library)."""
    try:
        summary = generate_summary(text)
    except Exception as e:
        summary = ""  # In case of any errors, default to an empty summary
        print(f"Error generating summary: {e}")
    
    return Document(text=text, metadata={"summary": summary, 'generated_at': current_time})

def make_graph(max_retries = 3, delay = 13):
        for attempt in range(max_retries):
            try:
                graph = graph_maker.from_documents(
                list(docs), 
                delay_s_between=2 ## delay_s_between because otherwise groq api maxes out pretty fast. 
                )
                return graph
            except Exception as e:
                print(e)
                if attempt < max_retries:

                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("All attempts failed.")
                    raise

### SETTING UP EVERYTHING ###
print("load_dotenv(): ", load_dotenv(), "\n")
URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
print("os.environ.get('GROQ_API_KEY'): ", os.environ.get("GROQ_API_KEY"), "\n")
print("os.environ: ", os.environ, "\n")
print("AUTH: ", AUTH, "\n")
print("dotenv_values: ", dotenv_values(".env"), "\n") # this should not be an empty dictionary!

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connection with Neo4j established.")


### CONFIG ###
ontology = Ontology(
    labels=[
        {"Symptom": "A characteristic or manifestation of a condition (e.g., snoring, daytime fatigue)."},
        {"Condition": "A medical condition or diagnosis (e.g., Obstructive Sleep Apnea, Hypoxemia)."},
        {"RiskFactor": "Factors that increase the likelihood of a condition (e.g., obesity, age, smoking)."},
        {"Test": "Medical or diagnostic tests (e.g., polysomnography, arterial blood gas)."},
        {"Treatment": "Interventions or therapies for a condition (e.g., CPAP, surgery)."},
        {"Outcome": "Potential results of a condition or treatment (e.g., improved oxygen saturation, reduced fatigue)."},
        {"Concept": "General medical or scientific concepts (e.g., positive airway pressure)."},
        {"Document": "Guidelines, classifications, or references (e.g., ICD-10, DSM-5)."}
    ],
    relationships=[
        "has_symptom",        # Connects a Condition to a Symptom
        "is_risk_factor_for", # Connects a RiskFactor to a Condition
        "requires_test",      # Connects a Condition to a Test
        "treated_by",         # Connects a Condition to a Treatment
        "results_in",         # Connects a Condition or Treatment to an Outcome
        "relates_to",         # Generic relationship for concepts and references
    ]
)
## Groq models
model = "mixtral-8x7b-32768"
# model ="llama3-8b-8192"
# model = "llama3-70b-8192"
# model="gemma-7b-it"

with open(input_file, "r") as file:
    words=file.readlines()

filtered_text = []
for indices in annotated_lines_icsd3:
    i = indices[0]
    j = indices[1]
    filtered_text.append(words[i:j+1])

sentence_list = []
for sentence in filtered_text:
    text = " ".join(word.strip() for word in sentence)
    sentence_list.append(text)

## Use Groq
llm = GroqClient(model=model, temperature=0.1, top_p=0.5)

current_time = str(datetime.datetime.now())

graph_maker = GraphMaker(ontology=ontology, llm_client=llm, verbose=False)

# Adjust number of workers based on your system capability and API limits
num_workers = 5

with ThreadPoolExecutor(max_workers=num_workers) as executor:
    docs = list(executor.map(create_document, sentence_list))

# UNPARALLELIZED
# docs = map(
#     lambda t: Document(text=t, metadata={"summary": generate_summary(t), 'generated_at': current_time}),
#     example_text_list
# )

try:
    graph = make_graph()
    print("Graph sucessfully made.")
except Exception as e:
    print(f"Graph creation failed: {e}.")

try:
    print("Total number of Edges", len(graph))
except Exception as e:
    print(f"Graph creation failed: {e}.")
    
for edge in graph:
    print(edge.model_dump(exclude=['metadata']), "\n\n")

create_indices = False
neo4j_graph = Neo4jGraphModel(edges=graph, create_indices=create_indices)

neo4j_graph.save()

end_time = time.time()

print("Used time: ", end_time - start_time)