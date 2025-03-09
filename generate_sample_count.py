import requests
import json
import time

BASE_URL = "https://www.cbioportal.org/api"
INPUT_FILE = "oncotree_codes.json"
OUTPUT_FILE = "oncotree_sample_counts.json"

def get_all_studies():
    studies = []
    page_size = 1000
    page_number = 0
    
    try:
        while True:
            url = f"{BASE_URL}/studies?pageSize={page_size}&pageNumber={page_number}"
            print(f"Fetching studies page {page_number}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            studies.extend(data)
            if len(data) < page_size:
                break
            page_number += 1
            time.sleep(1)
        print(f"Fetched {len(studies)} studies.")
        return studies
    except Exception as e:
        print(f"Error fetching studies: {e}")
        return []

def get_sample_counts_from_studies(studies):
    sample_counts = {}
    
    for study in studies:
        cancer_type_id = study.get("cancerTypeId", "").lower()
        sample_count = study.get("allSampleCount", 0)
        if cancer_type_id and sample_count > 0:
            sample_counts[cancer_type_id] = sample_counts.get(cancer_type_id, 0) + sample_count
            print(f"Study {study['studyId']}: {cancer_type_id} - {sample_count} samples")
    
    print(f"Found {len(sample_counts)} unique cancerTypeIds across studies.")
    return sample_counts

def generate_sample_counts():
    try:
        with open(INPUT_FILE, "r") as f:
            data = json.load(f)
            codes = data["oncotree_codes"]
    except Exception as e:
        print(f"Error loading {INPUT_FILE}: {e}")
        return
    
    print(f"Loaded {len(codes)} OncoTree codes.")
    
    studies = get_all_studies()
    if not studies:
        return
    
    sample_counts_map = get_sample_counts_from_studies(studies)
    
    # Map OncoTree codes to counts
    oncotree_counts = {}
    for code in codes:
        oncotree_counts[code] = sample_counts_map.get(code.lower(), 0)
    
    # Sort by count (descending)
    sorted_counts = dict(sorted(oncotree_counts.items(), key=lambda item: item[1], reverse=True))
    
    # Save sorted results
    with open(OUTPUT_FILE, "w") as f:
        json.dump(sorted_counts, f, indent=4)
    
    print(f"Saved sorted sample counts to {OUTPUT_FILE}")
    print("Sample counts for top 10 codes (sorted by count):")
    for code, count in list(sorted_counts.items())[:10]:
        print(f"{code}: {count} samples")

if __name__ == "__main__":
    generate_sample_counts()