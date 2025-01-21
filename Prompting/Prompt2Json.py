"""
UNFINISHED
Script to play around with prompts using GroqAPI, and saving them to Neo4j.
"""

from knowledge_graph_maker import GraphMaker, Ontology, GroqClient
from knowledge_graph_maker import Document
from neo4j import GraphDatabase
import datetime
from knowledge_graph_maker import Neo4jGraphModel

from dotenv import load_dotenv
import os
load_dotenv()
os.environ.get("GROQ_API_KEY")

URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
    print("Connection with Neo4j established.")
    
with open("data/ICSD3_dataset.txt", "r") as file:
    example_text_list=file.readlines()

print(len(example_text_list))

## Groq models
model = "mixtral-8x7b-32768"
# model ="llama3-8b-8192"
# model = "llama3-70b-8192"
# model="gemma-7b-it"

## Use Groq
llm = GroqClient(model=model, temperature=0.1, top_p=0.5)

current_time = str(datetime.datetime.now())

