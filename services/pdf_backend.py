import io
import re

import fitz
from PIL import Image


SIGNATURE_KEYWORDS = [
    "signature",
    "sign here",
    "authorized signature",
    "imza",
    "yetkili imza",
]


def find_signature_areas(doc, page_number):
    """
    Try to detect a signature area using common signature keywords.
    Returns PDF coordinates.
    """

    page = doc[page_number]
    page_width = page.rect.width
    page_height = page.rect.height

    areas = []

    words = page.get_text("words")

    for word in words:
        x0, y0, x1, y1, text, *_ = word
        normalized = re.sub(r"\W+", "", text.lower())

        for keyword in SIGNATURE_KEYWORDS:
            keyword_normalized = re.sub(
                r"\W+",
                "",
                keyword.lower()
            )

            if keyword_normalized in normalized:
                areas.append({
                    "x": min(x1 + 10, page_width - 170),
                    "y": max(y0 - 15, 0),
                    "w": 150,
                    "h": 50,
                    "reason": f"Keyword: {keyword}",
                })

    return areas


def place_signature(
    pdf_path,
    page_number,
    x_pt,
    y_pt,
    signature_img_path,
    width=150,
    height=60,
    output_path=None,
):
    """
    Insert signature image into PDF.
    """

    if output_path is None:
        output_path = pdf_path.replace(
            ".pdf",
            "_signed.pdf"
        )

    doc = fitz.open(pdf_path)

    try:
        page = doc[page_number]

        with Image.open(signature_img_path) as image:
            image = image.convert("RGBA")

            buffer = io.BytesIO()
            image.save(buffer, format="PNG")

            image_bytes = buffer.getvalue()

        rect = fitz.Rect(
            x_pt,
            y_pt,
            x_pt + width,
            y_pt + height,
        )

        page.insert_image(
    rect,
    stream=image_bytes,
    overlay=True,
    keep_proportion=True,
)

        doc.save(output_path)

    finally:
        doc.close()

    return output_path