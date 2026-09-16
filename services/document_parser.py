from io import BytesIO
from pypdf import PdfReader
from docx import Document


def extract_text(uploaded_file):
    """
    Extract text from a Streamlit UploadedFile.
    Supports PDF and DOCX.
    """

    if uploaded_file is None:
        return ""

    file_name = uploaded_file.name.lower()
    file_bytes = uploaded_file.getvalue()

    if file_name.endswith(".pdf"):
        return extract_pdf_text(file_bytes)

    elif file_name.endswith(".docx"):
        return extract_docx_text(file_bytes)

    else:
        raise ValueError("Unsupported file type. Please upload PDF or DOCX.")


def extract_pdf_text(file_bytes):
    reader = PdfReader(BytesIO(file_bytes))

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n\n".join(pages)


def extract_docx_text(file_bytes):
    document = Document(BytesIO(file_bytes))

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)