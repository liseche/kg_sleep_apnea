# Exploration Phase 1 - Report and reflection

Time: December-February

This document is intended as a report on what was done in this period, and a reflection on the findings.

## Experiments

There were two main experiment categories where all other experiments fall under in this phase. These are:

1. Explore NER performance with existing models without fine-tuning.
2. Explore LLM prompting with the knowledge-graph-maker library in Python.

Within these, multiple smaller experiments were conducted. These are listed with the belonging category in the two subsections below.

# NER Performance For Existing Models

I explored different existing models with NER capabilities, to see how they performed.

## Data
Two data documents created previously were used: ICSD version 3 (data/ICSD3.txt) and AASM version 25 (data/aasm_manual_v25 spell corrected). 

The AASM I got from Truls. It was generated using Adobe Acrobat to convert to Word, then Word to convert from .docx to a .txt document, and then manually edited to correct spelling. 

The ICSD was converted from a PDF to a .txt document using the "Automator" app version 2.10 (523) for Mac. The automation file is attached, and the workflow looks like this: 

![workflow](pdf2txt.workflow/contents/QuickLook/Preview.png)

Then the format of the file was changed using the script scripts/MakeDatasetWOTarget.py. It was changed to get each word on one line, for easier overview of the annotation of each word, and to be easier to label and evaluate.

## Model Choice

Two popular machine learning libraries are spaCy and HuggingFace's transformers. The models I tried are from these two libraries, since these are the most common.

### spaCy
The Spacy models were found through Spacy's documentation on what models it had available for biomedical data (https://spacy.io/universe/category/biomedical 27.01.2025). They were all dowloaded with pip and loaded with spaCy.

Out of the options, scispaCy was chosen, and the models listed in the README in the github repository home page were all tested (https://github.com/allenai/scispacy 27.01.2025), these are:

- en_core_sci_lg
- en_core_sci_md
- en_core_sci_scibert
- en_core_sci_sm
- en_ner_bc5cdr_md
- en_ner_bionlp13cg_md
- en_ner_craft_md
- en_ner_jnlpba_md

all version 0.5.4.

In addition, three models mentioned in https://huggingface.co/Precious1/Clinical-Biomedical-Named-Entity-Recognition-Using-Scispacy/blob/main/Clinical%20Biomedical%20Named%20Entity%20Recognition%20Using%C2%A0Scispacy.ipynb were also evaluated, these are:

- en_ner_bc5cdr_md (version 0.5.1)
- en_core_med7_lg (version 3.4.2.1) https://huggingface.co/kormilitzin/en_core_med7_lg
- en_core_med7_trf (version 3.4.2.1) https://huggingface.co/kormilitzin/en_core_med7_trf

medspaCy was not used, because they stated that it was currently in beta (27.01.2025) on the github page
(https://github.com/medspacy/medspacy).


### HuggingFace

The models used with PyTorch were found through "Papers With Code" (https://paperswithcode.com/task/medical-named-entity-recognition 27.01.2025) and the HuggingFace m42-health's clinical NER leaderboard (https://huggingface.co/spaces/m42-health/clinical_ner_leaderboard 27.01.2025). BioBERT models were also mentioned in multiple papers. They were all loaded with the HuggingFace transformers library.

The HuggingFace names of the models tried, together with why they were tried, are:
- alvaroalon2/biobert_diseases_ner
    - found through m42-health's clinical NER leaderboard
- dmis-lab/biobert-base-cased.v1.1
    - found through "Papers With Code"
- dmis-lab/biobert-base-cased.v1.2
    - found through "Papers With Code"
- kamalkraj/bioelectra-base-discriminator-pubmed-pmc
    - best performing model in "Papers With Code"
- knowledgator/gliner-multitask-large-v0.5
    - next best performing model in m42-health's clinical NER leaderboard.
    - A GLiNER model, which uses a different tactic for building the model than BERT and ELECTRA: "[treats] the task of Open NER as matching entity type embeddings to textual span representations in latent space, rather than as a generation task".
- pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb
    - pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb was found through a HuggingFace search, and I just decided to try it.

So we try BERT-based, ELECTRA-based and a GLiNER.

## NER

The named entity recognition were performed on both the AASM and the ICSD3 using the script NER+RE/PyTorch/TraditionalNER.py for HuggingFace models and NER+RE/spaCy/TraditionalNER.py for spaCy models. The resulting NER labelling are located in the same directory as the respective scripts.

## Evaluation

What are good evaluation metrics for NER?
- UAS

| Model | 

### Annotation
No suitable datasets were found for NER on sleep apnea related free text. Due to this, there was an ad-hoc informal annotation done on both the ICSD and AASM. See own annotation documents for documentation on the annotation process.

## Takeaways

TODO

# LLM Prompting With knowledge-graph-maker

Inspired by, and used the library presented in https://medium.com/towards-data-science/text-to-knowledge-graph-made-easy-with-graph-maker-f3f890c0dbe8.

## Motivation

TODO

## Execution

Adapted this to an own script, namely Prompting/KnowledgeGraphMaker.py. Tried different ontologies.

Self-made ontology:
```python
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
```

This didn't work very well, based on just looking at the graph.

TODO: evaluation and metrics for why it didn't perform well.

ChatGPT generated ontology:
```python
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
```

Worked better. 

TODO: Explain why.

## Evaluation / Results

Questions:
- how does the knowledge graph perform?
- in the knowledge graph: what kind of sentence lead to this relationship? Can look at the clusters in the KG too and try to connect it to the text  

TODO

## Takeaways

TODO

# Key Findings

## AASM vs. ICSD

Questions:
- How does the input text affect the result?
- Can the same entity labels be applied to both?
- Does/should anything (prompts, KG ++) be different for the two texts?
- 

- should have had cause?
Represent test results.