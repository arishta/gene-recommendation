import json
from langchain_core.prompts import PromptTemplate

# Define the template
template = PromptTemplate.from_template("""
    You are a genomics expert specializing in cancer genomics. 
    Which genes and pathways are relevant for classifying {cancer_type} (OncoTree code: {oncotree_code})? 
    Consider genes that are:
    1. Commonly mutated in this cancer type
    2. Used for molecular subtyping
    3. Associated with prognosis or treatment decisions
    4. Well-established in clinical or research settings
    Please only include well-established genes that are known to be important for the molecular 
    classification of {cancer_type}. Do not include speculative or rarely used markers.
    {format_instructions}
    """)

# Create a JSON-serializable dictionary with only the required fields
template_dict = {
    "template": template.template,
    "input_variables": template.input_variables
}

# Save to template.json
with open('template.json', 'w') as f:
    json.dump(template_dict, f, indent=2)

print("Template saved to 'template.json'")