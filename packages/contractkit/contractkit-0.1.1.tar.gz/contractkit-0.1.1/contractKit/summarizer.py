from openai import OpenAI

def summarize_contract(contract_text, api_key: str):
    if not api_key:
        raise ValueError("API key is required for summarization")

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a legal assistant. Summarize the following contract text in 5-7 bullet points.

Keep it concise and easy to understand for a business user.

Contract Text:
\"\"\"{contract_text}\"\"\"
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content


# Optional test
if __name__ == "__main__":
    import os
    import dotenv

    dotenv.load_dotenv()

    doc = "docs/Master_Internal_Policy.pdf"
    from contractKit.pdf_reader import extract_text_from_pdf

    sample_text = extract_text_from_pdf(doc)
    api_key = os.getenv("OPENAI_API_KEY")

    summary = summarize_contract(sample_text, api_key=api_key)
    print(summary)
