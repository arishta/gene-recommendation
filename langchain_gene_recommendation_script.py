import json
import time
import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic.v1 import BaseModel, Field 

class GeneRecommendations(BaseModel):
    mutation_based: List[str] = Field(description="Genes commonly mutated in this cancer type")
    expression_based: List[str] = Field(description="Genes with expression changes relevant for this cancer type")
    pathways: List[str] = Field(description="Biological pathways relevant for this cancer type")

def load_oncotree_data() -> Dict[str, str]:
    try:
        with open("oncotree_codes.json", "r") as f:
            data = json.load(f)
        code_to_name = {}
        for entry in data.get("oncotree_entries", []):
            code = entry.get("code")
            name = entry.get("name")
            if code and name:
                code_to_name[code] = name
        return code_to_name
    except Exception as e:
        print(f"Error loading OncoTree data: {e}")
        return {}

def load_sample_counts() -> Dict[str, int]:
    with open("oncotree_sample_counts.json", "r") as f:
        data = json.load(f)
    return data

ONCOTREE_CODE_TO_NAME = {}

def get_oncotree_name(code: str) -> str:
    global ONCOTREE_CODE_TO_NAME
    return ONCOTREE_CODE_TO_NAME.get(code, code)

def setup_langchain_pipeline():
    llm = ChatOpenAI(model="gpt-4", temperature=0.2)
    parser = JsonOutputParser(pydantic_object=GeneRecommendations)
    prompt_template = PromptTemplate(
        template=json.load(open('template.json', 'r'))["template"],
        input_variables=json.load(open('template.json', 'r'))["input_variables"]
    )
    return prompt_template | llm | parser

def generate_gene_recommendations(cancer_type: str, oncotree_code: str, chain) -> Dict[str, List[str]]:
    try:
        format_instructions = """
        Return a JSON object with the following structure:
        {
            "mutation_based": ["Gene1", "Gene2", "Gene3"],
            "expression_based": ["GeneX", "GeneY", "GeneZ"],
            "pathways": ["PathwayA", "PathwayB"]
        }
        """
        result = chain.invoke({
            "cancer_type": cancer_type,
            "oncotree_code": oncotree_code,
            "format_instructions": format_instructions
        })
        return {
            "Mutation-Based": result.get("mutation_based", []),
            "Expression-Based": result.get("expression_based", []),
            "Pathways": result.get("pathways", [])
        }
    except Exception as e:
        print(f"Error generating recommendations for {cancer_type} ({oncotree_code}): {e}")
        return {"Mutation-Based": [], "Expression-Based": [], "Pathways": [], "error": str(e)}

def main():
    MIN_SAMPLES = 10
    global ONCOTREE_CODE_TO_NAME
    ONCOTREE_CODE_TO_NAME = load_oncotree_data()
    
    if not ONCOTREE_CODE_TO_NAME:
        print("Error: Failed to load OncoTree code to name mapping. Exiting.")
        return
    
    print(f"Loaded {len(ONCOTREE_CODE_TO_NAME)} OncoTree code to name mappings")
    sample_counts = load_sample_counts()
    valid_codes = {code: count for code, count in sample_counts.items() 
                   if count >= MIN_SAMPLES and code != "MIXED"}
    
    print(f"Found {len(valid_codes)} OncoTree codes with at least {MIN_SAMPLES} samples")
    chain = setup_langchain_pipeline()
    sorted_codes = sorted(valid_codes.items(), key=lambda x: x[1], reverse=True)
    all_recommendations = {}
    
    os.makedirs("recommendations", exist_ok=True)
    
    for i, (code, sample_count) in enumerate(sorted_codes, 1):
        print(f"[{i}/{len(sorted_codes)}] Processing {code} with {sample_count} samples...")
        cancer_type_name = get_oncotree_name(code)
        recommendations = generate_gene_recommendations(cancer_type_name, code, chain)
        all_recommendations[code] = {
            "name": cancer_type_name,
            "sample_count": sample_count,
            "recommendations": recommendations
        }
        
        individual_file = os.path.join("recommendations", f"gene_recommendations_{code}.json")
        with open(individual_file, "w") as f:
            json.dump({code: all_recommendations[code]}, f, indent=2)
        with open("all_gene_recommendations.json", "w") as f:
            json.dump(all_recommendations, f, indent=2)
        
        time.sleep(2)
    
    print("Process complete. Results saved to all_gene_recommendations.json and individual files in 'recommendations' folder")

if __name__ == "__main__":
    main()