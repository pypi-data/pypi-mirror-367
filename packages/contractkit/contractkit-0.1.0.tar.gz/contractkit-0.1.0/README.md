# contractkit

A simple Python library for contract intelligence using LLMs.

## Features

- 📄 Extracts text from PDF contracts
- 🔍 Parses and cleans contract text
- 🧠 Extracts key clauses using OpenAI
- 🧾 Summarizes contracts for business understanding

## Usage

```python
from contractkit import pdf_reader, extractor, summarizer

text = pdf_reader.extract_text_from_pdf("contract.pdf")
clauses = extractor.extract_clauses(text, api_key="YOUR_KEY")
summary = summarizer.summarize_contract(text, api_key="YOUR_KEY")
