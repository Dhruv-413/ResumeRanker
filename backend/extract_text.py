import fitz
import docx
import os

def extract_text_from_pdf(pdf_path):
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")

    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            extracted_text = page.get_text("text")
            if extracted_text.strip():
                text += extracted_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

    if not text.strip():
        print(f"Warning: No text found in {pdf_path}. Consider OCR for scanned PDFs.")
    
    return text.strip()

def extract_text_from_docx(docx_path):
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"File not found: {docx_path}")

    text = ""
    try:
        doc = docx.Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX {docx_path}: {e}")
        return ""

    return text.strip()

def extract_text(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")
