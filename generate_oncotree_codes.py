import requests
import json
import re

API_URL = "https://oncotree.info:443/api/tumor_types.txt?version=oncotree_latest_stable"
OUTPUT_FILE = "oncotree_codes.json"

def fetch_oncotree_codes():
    try:
        # Fetch the text data
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        
        # Split into lines
        lines = response.text.strip().split("\n")
        
        headers = lines[0].split("\t")
        
        # Dictionary to store code -> name mappings
        code_to_name = {}
        
        # Extract codes and names from level_1 to level_7
        for line in lines[1:]:
            columns = line.split("\t")
            for col in columns[:7]:  # level_1 to level_7
                if col:
                    match = re.search(r"(.*?)\((.*?)\)", col)
                    if match:
                        name = match.group(1).strip()
                        code = match.group(2).strip()
                        if code and re.match(r"^[A-Za-z][A-Za-z0-9_]*$", code):  # Alphabetic start, no semicolons
                            code_to_name[code] = name
        
        result = []
        for code in sorted(code_to_name.keys()):
            result.append({
                "code": code,
                "name": code_to_name[code]
            })
        
        with open(OUTPUT_FILE, "w") as f:
            json.dump({"oncotree_entries": result}, f, indent=4)
        
        print(f"Generated {len(result)} OncoTree entries. Saved to {OUTPUT_FILE}")
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from OncoTree API: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

if __name__ == "__main__":
    entries = fetch_oncotree_codes()
    if entries:
        print("\nFirst 5 entries as a sample:")
        for entry in entries[:5]:
            print(f"{entry['code']}: {entry['name']}")
        
        print("\nLast 5 entries as a sample:")
        for entry in entries[-5:]:
            print(f"{entry['code']}: {entry['name']}")
    else:
        print("Failed to fetch entries. Check API response or script.")