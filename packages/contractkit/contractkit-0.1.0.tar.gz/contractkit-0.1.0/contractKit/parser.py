def split_into_clauses(text):
    """Naively splits text into clauses by double newlines or bullets."""
    import re
    clauses = re.split(r'\n\s*\n|•|- ', text)
    return [clause.strip() for clause in clauses if clause.strip()]



# Add this at bottom of parser.py
if __name__ == "__main__":
    sample_text = "1. This agreement is confidential.\n\n2. Termination may occur anytime."
    clauses = split_into_clauses(sample_text)
    print(clauses)

