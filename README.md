# Knowledge Graph Generation Two Ways: NER + RE and Prompting LLM

This code was created as a part of the master's thesis "Natural Language Processing to Create a Knowledge Graph About Sleep Apnea" at University of Oslo. The thesis will soon be available through DUO, the University of Oslo's archive.

`kg_explorer` is a package containing code to generate knowledge graphs with NLP two different ways. One using **direct prompting** to LLMs, and the other with a **NER and RE** pipeline.

`kg_explorer/Prompting` directory: contains code to prompt an LLM with knowledge-graph-maker library and GroqAPI and insert the input into a knowledge graph in Neo4j.

`kg_explorer/NER+RE` directory: contains code to do NER with spaCy and PyTorch, do RE using the NER annotated files, and create a knowledge graph in Neo4j with the triples. 

`kg_explorer/scripts`: other scripts used to achieve the final goal of generating knowledge graphs.

In the directory named `data` we provide a data set for NER on a selection of the medical manual ICSD-3, annotated by ourselves. The annotation guidelines used is provided in the directory `reports`. See the thesis for more details on this data set. `outputs` contain NER annotations of the ICSD-3 annotated by different models, and logs from evaluation scripts.

# Prerequisites

- Python (for instance version 3.11.9)

Dependencies for running code using spaCy (the scripts `kg_explorer/NER+RE/NER_spaCy.py`, `kg_explorer/scripts/MakeDatasetWOTarget.py`) are provided in `requirements-spacy.txt`.

Dependencies for running all other code, including the code in the `Prompting` directory (works with the knowledge_graph_maker library, but not with spacy NER) are provided in `requirements.txt`.

# How To Run

This project contains multiple individual scripts. The use is documented for most of the scripts with argparse. Add --help at the end of the scripts to see details of use.

NB! To reproduce the results in the thesis, always use the file `data/ICSD3_annotated_unfiltered.tsv` as the file containing the gold annotations.