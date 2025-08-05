# MRT MODULE
MRT_COLUMNS = ['reason_to_end_the_behavioral_task_code', #'participant_quality', 
           'participant_id', 'group_id', 'provider_id', 'module_name',
           'project_identifier', 'reaction_time', 'task_name', 'trial_name','given_response_label_presented', 'procedure_name',
           'trial_stimulus_category','expected_response', 'given_response_accuracy', 'given_response_label_english', 'Gender', 'Age'
          ]
PROJECT = 'neurons-ml'
LOCATION = 'us-central1'

MODEL_TYPE = 'gemini-2.0-flash'
PARAMETERS = {
    "candidate_count": 1,
    "max_output_tokens": 32,
    "temperature": 0.1,
    "top_p": 0.4,
    "top_k": 10
}

# FRT MODULE

FRT_COLUMNS_RENAME = {
    'procedure_stimulus' : 'frt_stimulus',
    'trial_association_english' : 'frt_association',
    'given_response_label_english': 'frt_response'
}

SPELLCHECK_PROMPT_TEMPLATE = """
You are a **Brand Name Spell Checker**.

## Task
Given:
- A list of valid brand names:  
  **potential_responses = {potential_responses}**

- A single input to validate:  
  **brand_to_check = {brand_to_check}**

Determine if `brand_to_check` approximately matches any entry in `potential_responses` using:
- Spelling similarity ≥ 98%
- Edit distance ≤ 2
- Semantic similarity ≥ 90%

## Output Rules
- If a close match exists, return only the **closest valid brand name** from `potential_responses`.
- If no suitable match exists, return exactly: **"Not Found"**


## Examples
- "Addidas" → "Adidas"
- "Nke" → "Nike"
- "ume" → "Puma"
- "Bang" → "Bang & Olufsen"
- "Can't remember" → "Not Found"
- "I don't know" → "Not Found"
- "Life" → "Not Found"

**Return format: ONE brand name from `potential_responses` or "Not Found" — nothing else.**
## Response Template
example: Prada
example: Not Found
"""
