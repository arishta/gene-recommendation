import streamlit as st
import json
from typing import Dict

# Load precomputed recommendations
def load_all_recommendations() -> Dict:
    try:
        with open('all_gene_recommendations.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Error: 'all_gene_recommendations.json' not found. Please run generate_recommendations.py first.")
        return {}
    except Exception as e:
        st.error(f"Error loading recommendations: {e}")
        return {}

# Streamlit app
def main():
    st.title("Cancer Gene Recommendation Demo")
    st.write("Enter an OncoTree code to view precomputed gene and pathway recommendations.")

    # Load precomputed recommendations
    all_recommendations = load_all_recommendations()
    
    if not all_recommendations:
        st.stop()  # Stop execution if file loading fails

    # Input fields
    cancer_type = st.text_input("Cancer Type (optional)", value="Breast Cancer")
    oncotree_code = st.text_input("OncoTree Code", value="BRCA")

    # Button to display recommendations
    if st.button("Get Recommendations"):
        if oncotree_code in all_recommendations:
            st.success(f"OncoTree Code '{oncotree_code}' found!")
            recommendations = all_recommendations[oncotree_code]["recommendations"]
            
            # Display results with corrected keys
            st.subheader(f"Recommendations for {all_recommendations[oncotree_code]['name']} ({oncotree_code})")
            st.write("**Mutation-Based Genes:**")
            st.write(", ".join(recommendations["Mutation-Based"]) or "None")
            st.write("**Expression-Based Genes:**")
            st.write(", ".join(recommendations["Expression-Based"]) or "None")
            st.write("**Pathways:**")
            st.write(", ".join(recommendations["Pathways"]) or "None")
        else:
            st.error(f"OncoTree Code '{oncotree_code}' not found.")

if __name__ == "__main__":
    main()