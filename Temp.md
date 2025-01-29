In the background chapter of the thesis the general methods related to the thesis topic are presented. You have used this knowledge that should be presented in this background chapter to do some NER and LLM prompting, as a small exploration of the field of the thesis (which is creating knowledge graphs for sleep apnea with NLP methods). Now, present how you came to your findings in a format that allows you to elaborate in the thesis.  
  
"Form":  
- [\] what did you try  
- [\] why did you try exactly this?  
- [ ] how did it work. Good/bad? Why? Give metrics, or some scientific way of evaluating the result.  
- [ ] what can we learn from this? What could be some good ways forward to improve the results?  
- explain the path  
  
Include:  
- why do AASM perform worse than ICSD3?  
- annotation  
- choose a subset of the dataset  
- most critical text bits?  
- explain why you did it a certain way  
- metrics  
- how does the input text affect the result?  
- in the knowledge graph: what kind of sentence lead to this relationship? Can look at the clusters in the KG too and try to connect it to the text  
- different methods that you tested on different input text  
  
Annotation:  
- objective criteria  
- do not try to improve the results  
- same way for all of the text  
  
AASM and ICSD3:  
- check if it makes sense to use the same labels
- maybe the prompts, KG, +++ needs to be different for the different text
  
Remember to:  
- write absolutely everything you did  
  
Other talking points:  
- might have to do some preprocessing.