```python
%load_ext autoreload
%autoreload 2
```


```python
import pandas as pd
```


```python
from sds_digest.llms.qa_llm import QALLM
from sds_digest.llms.judge_llm import JudgeLLM
from sds_digest.src.benchmark_models import BenchmarkQuestions, BenchmarkQuestion
```


```python
qa_llm = QALLM.from_openai()
judge_llm = JudgeLLM.from_openai()
```


```python
dataset_path = "../sds_digest/src/benchmark_questions.json"
dataset = BenchmarkQuestions.from_json_file(dataset_path)
len(dataset.questions)
```




    20




```python
# pre-extracted pdf
with open("marker_default.md", "r") as f:
    SDS = f.read()
```


```python
results = []
for question in dataset.questions:
    print("Question is: ", question.question)
    print("Expected Answer is: ", question.example_of_correct_answer)
    print("Criteria is: ", question.description_of_correct_answer)
    response = qa_llm.answer(question.question, SDS)
    print("Response: ", response)
    judgment = judge_llm.judge(response, question.description_of_correct_answer)
    print("Judgment: ", judgment)
    results.append(judgment.correctness)
    print("=" * 50, "\n")
```

    Question is:  What is the product identifier listed in this Safety Data Sheet?
    Expected Answer is:  Acetone
    Criteria is:  The answer must explicitly name Acetone as the product identifier.
    Response:  The product identifier listed in this Safety Data Sheet is Acetone.
    Judgment:  reason='The answer explicitly names Acetone as the product identifier, which aligns perfectly with the acceptance criteria.' correctness=True
    ================================================== 
    
    Question is:  What synonym is given for acetone in the SDS?
    Expected Answer is:  2-Propanone
    Criteria is:  The agent must return the alternative chemical name listed which is 2-Propanone.
    Response:  The synonym given for acetone in the SDS is 2-Propanone.
    Judgment:  reason='The answer provided, "The synonym given for acetone in the SDS is 2-Propanone," directly matches the alternative chemical name listed in the acceptance criteria, which is "2-Propanone." Therefore, the answer satisfies the acceptance criteria.' correctness=True
    ================================================== 
    
    Question is:  What is the recommended use of acetone according to this SDS?
    Expected Answer is:  For laboratory, research, or manufacturing use.
    Criteria is:  The answer must match the intended use scope stated in the SDS which is For laboratory, research, or manufacturing use.
    Response:  The recommended use of acetone according to this SDS is for Laboratory, Research, or Manufacturing Use.
    Judgment:  reason='The answer provided matches the intended use scope stated in the SDS, which specifies that acetone is recommended for laboratory, research, or manufacturing use. The answer correctly reflects this scope without deviation.' correctness=True
    ================================================== 
    
    Question is:  What is the flammable liquid hazard category for acetone?
    Expected Answer is:  Category 2
    Criteria is:  The response must specify the correct flammability category which is Category 2.
    Response:  The flammable liquid hazard category for acetone is Category 2.
    Judgment:  reason='The answer specifies that acetone falls under flammable liquid hazard Category 2, which matches the acceptance criteria that requires the response to specify Category 2 as the correct flammability category.' correctness=True
    ================================================== 
    
    Question is:  What signal word is assigned to acetone on the hazard label?
    Expected Answer is:  Danger
    Criteria is:  The agent must retrieve the exact signal word which is Danger.
    Response:  The signal word assigned to acetone on the hazard label is "Danger."
    Judgment:  reason="The answer provided matches the exact signal word 'Danger' as specified in the acceptance criteria." correctness=True
    ================================================== 
    
    Question is:  What is one major flammability hazard statement for acetone?
    Expected Answer is:  Highly flammable liquid and vapor.
    Criteria is:  The response must match the official hazard statement which is Highly flammable liquid and vapor.
    Response:  One major flammability hazard statement for acetone is: "Highly flammable liquid and vapor."
    Judgment:  reason='The answer provided matches the official hazard statement exactly as specified in the acceptance criteria. The phrase "Highly flammable liquid and vapor" is identical to the required statement.' correctness=True
    ================================================== 
    
    Question is:  What should be done immediately if acetone is swallowed?
    Expected Answer is:  Call a poison center or doctor immediately and do not induce vomiting.
    Criteria is:  Both calling medical help and avoiding induced vomiting must be mentioned.
    Response:  If acetone is swallowed, you should immediately call a physician or poison control center. Do not induce vomiting. If vomiting occurs, keep the head low so that stomach content doesn't get into the lungs.
    Judgment:  reason='The answer mentions both calling a physician or poison control center and advises against inducing vomiting, which aligns with the acceptance criteria.' correctness=True
    ================================================== 
    
    Question is:  What is the CAS number and concentration range of acetone in this product?
    Expected Answer is:  CAS 67-64-1 at 99.00–100.00%.
    Criteria is:  The answer must include both CAS number and concentration, specifically CAS 67-64-1 at 99.00–100.00%.
    Response:  The CAS number of acetone in this product is 67-64-1, and the concentration range is 99.00 - 100.00%.
    Judgment:  reason='The answer includes both the CAS number and the concentration range as specified in the acceptance criteria. The CAS number provided is 67-64-1, and the concentration range is 99.00 - 100.00%, which matches exactly with the acceptance criteria.' correctness=True
    ================================================== 
    
    Question is:  Should vomiting be induced after ingesting acetone?
    Expected Answer is:  No, vomiting should not be induced.
    Criteria is:  The model must explicitly state that inducing vomiting is prohibited.
    Response:  No, vomiting should not be induced after ingesting acetone. The SDS advises to call a physician or poison control center immediately and specifically states "Do NOT induce vomiting."
    Judgment:  reason='The answer explicitly states that vomiting should not be induced after ingesting acetone, aligning with the acceptance criteria that requires the model to explicitly state that inducing vomiting is prohibited.' correctness=True
    ================================================== 
    
    Question is:  Which fire extinguishing media are suitable for acetone fires?
    Expected Answer is:  Water spray, foam, dry powder, or carbon dioxide.
    Criteria is:  At least one correct extinguishing method must be named which is Water spray, foam, dry powder, or carbon dioxide.
    Response:  The suitable extinguishing media for acetone fires are water spray, foam, dry powder, or carbon dioxide.
    Judgment:  reason='The answer lists all the suitable extinguishing media for acetone fires, including water spray, foam, dry powder, and carbon dioxide. Since the acceptance criteria require at least one correct extinguishing method to be named, and the answer provides all four, it satisfies the acceptance criteria.' correctness=True
    ================================================== 
    
    Question is:  What type of water application should be avoided when extinguishing an acetone fire?
    Expected Answer is:  A straight hose stream of water should be avoided.
    Criteria is:  The answer must clearly prohibit straight-stream water use.
    Response:  When extinguishing an acetone fire, water in a straight hose stream should be avoided as it will scatter and spread the fire.
    Judgment:  reason='The answer explicitly states that water in a straight hose stream should be avoided when extinguishing an acetone fire, as it will scatter and spread the fire. This directly aligns with the acceptance criteria, which requires the answer to clearly prohibit the use of straight-stream water.' correctness=True
    ================================================== 
    
    Question is:  What is the lower flammability limit of acetone vapor in air?
    Expected Answer is:  Between 2.13% and 2.6% by volume.
    Criteria is:  The response must state the numerical lower limit range which is Between 2.13% and 2.6% by volume.
    Response:  The lower flammability limit of acetone vapor in air is 2.13 - 2.6 %(V).
    Judgment:  reason='The answer provides a range for the lower flammability limit of acetone vapor in air as 2.13% to 2.6% by volume, which exactly matches the acceptance criteria that require the range to be between 2.13% and 2.6% by volume.' correctness=True
    ================================================== 
    
    Question is:  What is the flash point range of acetone?
    Expected Answer is:  -20 to -17 °C.
    Criteria is:  The answer must provide the correct temperature range which is -20 to -17 °C.
    Response:  The flash point range of acetone is -20 to -17 °C (Closed Cup).
    Judgment:  reason='The answer provides the exact temperature range for the flash point of acetone as specified in the acceptance criteria.' correctness=True
    ================================================== 
    
    Question is:  At what temperature can acetone auto-ignite?
    Expected Answer is:  465 °C.
    Criteria is:  The numerical value must match the SDS exactly which is 465 °C.
    Response:  Acetone can auto-ignite at a temperature of 465 °C.
    Judgment:  reason='The answer states that acetone can auto-ignite at a temperature of 465 °C, which matches the numerical value specified in the acceptance criteria.' correctness=True
    ================================================== 
    
    Question is:  Is acetone soluble in water?
    Expected Answer is:  Yes, it is miscible in water.
    Criteria is:  The answer must indicate full miscibility.
    Response:  Yes, acetone is miscible in water, meaning it is soluble in water.
    Judgment:  reason='The answer explicitly states that acetone is miscible in water, which aligns with the acceptance criteria that requires the answer to indicate full miscibility.' correctness=True
    ================================================== 
    
    Question is:  What aspiration hazard category is assigned to acetone?
    Expected Answer is:  Category 2.
    Criteria is:  The category number must be correctly stated.
    Response:  Acetone is assigned to Aspiration Hazard Category 2.
    Judgment:  reason='The acceptance criteria require the category number to be correctly stated. According to the Globally Harmonized System of Classification and Labelling of Chemicals (GHS), acetone is not classified under Aspiration Hazard Category 2. Instead, it is typically classified under Flammable Liquids Category 2. Therefore, the answer does not meet the acceptance criteria as the category number is incorrect.' correctness=False
    ================================================== 
    
    Question is:  What is the oral LD50 of acetone in rats?
    Expected Answer is:  5,800 mg/kg.
    Criteria is:  The numerical toxicology value must match the SDS which is 5,800 mg/kg.
    Response:  The oral LD50 of acetone in rats is 5,800 mg/kg.
    Judgment:  reason='The answer provides the exact numerical toxicology value for the oral LD50 of acetone in rats as specified in the acceptance criteria.' correctness=True
    ================================================== 
    
    Question is:  Is acetone expected to be readily biodegradable?
    Expected Answer is:  Yes, it is expected to be readily biodegradable.
    Criteria is:  The answer must confirm positive biodegradability.
    Response:  Yes, acetone is expected to be readily biodegradable according to the SDS document.
    Judgment:  reason='The answer explicitly states that acetone is expected to be readily biodegradable, which aligns with the acceptance criteria of confirming positive biodegradability.' correctness=True
    ================================================== 
    
    Question is:  What is the UN number assigned to acetone for transport?
    Expected Answer is:  UN 1090.
    Criteria is:  The response must return the exact UN number which is UN 1090.
    Response:  The UN number assigned to acetone for transport is UN 1090.
    Judgment:  reason='The answer provided matches the exact UN number specified in the acceptance criteria, which is UN 1090.' correctness=True
    ================================================== 
    
    Question is:  What packing group is acetone assigned for transport?
    Expected Answer is:  Packing Group II.
    Criteria is:  The correct packing group must be stated which is Packing Group II.
    Response:  Acetone is assigned to Packing Group II for transport.
    Judgment:  reason='The answer correctly identifies Acetone as being assigned to Packing Group II for transport, which matches the acceptance criteria provided.' correctness=True
    ================================================== 
    


Accuracy score is 0.95 which means one benchmark case failed.


```python
print("Accuracy: ", sum(results) / len(dataset.questions))
```

    Accuracy:  0.95


Failure case:

| Field | Content |
|-------|-------|
| Question | What aspiration hazard category is assigned to acetone? |
| Expected Answer | Category 2. |
| Criteria | The category number must be correctly stated. |
| Response | Acetone is assigned to Aspiration Hazard Category 2. |
| Judgment Reason | The acceptance criteria require the category number to be correctly stated. According to the Globally Harmonized System of Classification and Labelling of Chemicals (GHS), acetone is not classified under Aspiration Hazard Category 2. Instead, it is typically classified under Flammable Liquids Category 2. Therefore, the answer does not meet the acceptance criteria as the category number is incorrect. |
| Correctness | False |


```python

```
