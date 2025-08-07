
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"
    return full_text

# Add fallback OCR if text extraction fails

# Test block (optional)
if __name__ == "__main__":
    path = "docs/Master_Internal_Policy.pdf"
    print(extract_text_from_pdf(path))
