# NER using en_core_med7_lg from Spacy

Clinical Biomedical Named Entity Recognition following the guide on Scispacy.ipynb from 
https://huggingface.co/Precious1/Clinical-Biomedical-Named-Entity-Recognition-Using-Scispacy/blob/main/Clinical%20Biomedical%20Named%20Entity%20Recognition%20Using%C2%A0Scispacy.ipynb

labels: `DOSAGE`, `DRUG`, `DURATION`, `FORM`, `FREQUENCY`, `ROUTE`, `STRENGTH`

**Evaluation of NER models for Sleep Apnea Related Documents**

AASM 2.5:
- just horrible for all labels. Possibly since the format is so different from the EHR-like format from the tutorial. There's also little text.

ICSD3:
- A lot of false positives on article publication dates, page numbers, names and abbreviations.
- Some labels' annotations are acceptable

Human evaluation of performance (by myself):

| LABEL       | JUDGED PERFORMANCE | ACTUAL LABEL FOR COMMON MISCLASSIFICATIONS | Comment                                                                           |
| ----------- | ------------------ | ------------------------------------------ | --------------------------------------------------------------------------------- |
| `DOSAGE`    | bad                | article publication dates                  | No identified entities were correct                                               |
| `DRUG`      | medium             | names,                                     | Does annotate the drugs, but also lots of other things.                           |
| `DURATION`  | good               | -                                          | All entities are correctly labelled.                                              |
| `FORM`      | good               | -                                          | All entities are correctly labelled.                                              |
| `FREQUENCY` | ?                  | name                                       | 2 identified entities, one is somewhat correct ("usual bedtimes"), one is a name. |
| `ROUTE`     | medium             | names, abbreviations ("iv" in "DSM-IV-TR") | Substantial FPs.                                                                  |
| `STRENGTH`  | bad                | article publication dates, page numbers,   | No identified entities were correct                                               |
