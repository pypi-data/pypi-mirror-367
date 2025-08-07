from openai import OpenAI

def extract_clauses(contract_text, api_key: str):
    if not api_key:
        raise ValueError("API key is required for clause extraction")

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a legal assistant. Extract all key clauses from the following contract text.

For each clause, return:
- type (e.g., Termination, Confidentiality, Payment)
- text (the actual clause)
- summary (short explanation)

Respond in JSON format as a list of objects:
[
  {{
    "type": "...",
    "text": "...",
    "summary": "..."
  }},
  ...
]

Contract Text:
\"\"\"{contract_text}\"\"\"
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content


# Optional test run
if __name__ == "__main__":
    import os
    import dotenv

    dotenv.load_dotenv()

    doc = "docs/Master_Internal_Policy.pdf"
    from pdf_reader import extract_text_from_pdf

    if not os.path.exists(doc):
        raise FileNotFoundError(f"{doc} not found.")

    sample_text = extract_text_from_pdf(doc)
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set in environment.")

    result = extract_clauses(sample_text, api_key=api_key)
    print(result)
