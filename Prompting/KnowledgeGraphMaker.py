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
    
ontology = Ontology(
    labels=[
        {"AHI": "apnea hypopnea index"},
        "Disease",
        {"Disease category": "category of a disease"},
        {"Symptom": "symptom of some disease"},
        "Medical test",
        {"Test result": "result of the medical test"},
        "Medical equipment",
    ],
    relationships=[
        "Relation between any pair of Entities"
    ],
)

## Groq models
model = "mixtral-8x7b-32768"
# model ="llama3-8b-8192"
# model = "llama3-70b-8192"
# model="gemma-7b-it"

## Use Groq
llm = GroqClient(model=model, temperature=0.1, top_p=0.5)

current_time = str(datetime.datetime.now())

graph_maker = GraphMaker(ontology=ontology, llm_client=llm, verbose=False)

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


docs = map(
    lambda t: Document(text=t, metadata={"summary": generate_summary(t), 'generated_at': current_time}),
    example_text_list
)

graph = graph_maker.from_documents(
    list(docs), 
    delay_s_between=0 ## delay_s_between because otherwise groq api maxes out pretty fast. 
    ) 
print("Total number of Edges", len(graph))

for edge in graph:
    print(edge.model_dump(exclude=['metadata']), "\n\n")
    


create_indices = False
neo4j_graph = Neo4jGraphModel(edges=graph, create_indices=create_indices)

neo4j_graph.save()