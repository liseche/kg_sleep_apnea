import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from knowledge_graph_maker import Ontology

ontology = Ontology(
    labels = [
        {"AHI": "Apnea Hypopnea Index"},
        "Disease",
        {"Disease category": "Category of a disease"},
        {"Symptom": "Symptom of some disease"},
        "Medical test",
        {"Test result": "Result of the medical test"},
        "Medical equipment",
        ],
    relationships=["Relationship between Any two labeled entities"])

prompt = str("You are an expert at creating Knowledge Graphs."
    "Consider the following ontology. \n"
    f"{ontology} \n"
    "The user will provide you with an input text delimited by ```. "
    "Extract all the entities and relationships from the user-provided text as per the given ontology. Do not use any previous knowledge about the context."
    "Remember there can be multiple direct (explicit) or implied relationships between the same pair of nodes. "
    "Be consistent with the given ontology. Use ONLY the labels and relationships mentioned in the ontology. "
    "Format your output as a json with the following schema. \n"
    "[\n"
    "   {\n"
    '       node_1: Required, an entity object with attributes: {"label": "as per the ontology", "name": "Name of the entity"},\n'
    '       node_2: Required, an entity object with attributes: {"label": "as per the ontology", "name": "Name of the entity"},\n'
    "       relationship: Describe the relationship between node_1 and node_2 as per the context, in a few sentences.\n"
    "   },\n"
    "]\n"
    "Do not add any other comment before or after the json. Respond ONLY with a well formed json that can be directly read by a program.")

def load_model_and_tokenizer(model_name):
    """Load the model and tokenizer from Hugging Face."""
    print(f"Loading model and tokenizer from '{model_name}'...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model

def generate_text(model, tokenizer, prompt, max_length=50, device='cpu'):
    """Generate text from a prompt using the model and tokenizer."""
    # Ensure model is on the correct device
    model.to(device)

    # Encode the input text
    input_ids = tokenizer.encode(prompt, return_tensors='pt').to(device)

    # Generate text
    with torch.no_grad():
        output_ids = model.generate(
            input_ids,
            max_length=max_length,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.7
        )
    
    # Decode the generated text
    generated_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return generated_text

def main():
    input_file = "../../data/ICSD3_dataset2.txt"
    with open(input_file, "r") as file:
        text = file.read()
    
    question = prompt + "```" + text + "```"
    
    with open("prompt.txt", "w+") as output_file:
        output_file.write(question)
        
    # Define model name and input prompt
    # model_name = "mistralai/Mistral-7B-Instruct-v0.2"
    model_name = "google-t5/t5-base"

    # Load model and tokenizer
    # tokenizer, model = load_model_and_tokenizer(model_name)
    # Determine device to use
    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Generate and print text
    # generated_text = generate_text(model, tokenizer, question, device=device)
    print("\nGenerated Text:\n")
    # print(generated_text)

if __name__ == "__main__":
    main()
