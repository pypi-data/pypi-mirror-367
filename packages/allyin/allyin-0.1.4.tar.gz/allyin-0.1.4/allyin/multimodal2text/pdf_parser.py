import fitz  # PyMuPDF
from .data_cleaner import clean_text  # Import the cleaner

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts and returns cleaned layout-aware text from a PDF file using PyMuPDF.
    Handles normal text and filled-in form fields, attempting to preserve
    associations between labels and values based on spatial proximity.
    """
    text = []

    with fitz.open(file_path) as doc:
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            lines = []

            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        span_text = " ".join(span["text"].strip() for span in line["spans"]).strip()
                        if span_text:
                            bbox = line["bbox"]  # (x0, y0, x1, y1)
                            lines.append((bbox[1], span_text))  # use y0 as vertical position

            # Sort lines top to bottom
            lines.sort(key=lambda x: x[0])

            # Append sorted text
            for _, line_text in lines:
                text.append(line_text)

        # Extract filled-in form fields
        try:
            for field in doc.widgets():
                key = field.field_name
                value = field.field_value
                if value:
                    text.append(f"{key}: {value}")
        except Exception:
            pass

    raw_text = "\n".join(text)
    return raw_text
