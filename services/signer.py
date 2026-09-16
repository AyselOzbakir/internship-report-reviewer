import os
import tempfile

import fitz

from services.pdf_backend import (
    find_signature_areas,
    place_signature,
)


def sign_uploaded_pdf(pdf_file, signature_file):
    if pdf_file is None:
        raise ValueError("PDF file is required.")

    if signature_file is None:
        raise ValueError("Signature image is required.")

    # Temporary working directory
    temp_dir = tempfile.mkdtemp()

    pdf_path = os.path.join(
        temp_dir,
        pdf_file.name
    )

    signature_path = os.path.join(
        temp_dir,
        signature_file.name
    )

    # Save uploaded PDF
    with open(pdf_path, "wb") as f:
        f.write(pdf_file.getvalue())

    # Save uploaded signature image
    with open(signature_path, "wb") as f:
        f.write(signature_file.getvalue())

    # --------------------------------------------------
    # FIND SIGNATURE AREA
    # --------------------------------------------------
    doc = fitz.open(pdf_path)

    detected_area = None
    detected_page = None

    try:
        for page_number in range(len(doc)):
            areas = find_signature_areas(
                doc,
                page_number
            )

            if areas:
                detected_area = areas[0]
                detected_page = page_number
                break

    finally:
        doc.close()

    # --------------------------------------------------
    # FALLBACK POSITION
    # --------------------------------------------------
    # If no signature keyword/area is found,
    # place the signature near the bottom-right
    # of the last page.
    if detected_area is None:
        doc = fitz.open(pdf_path)

        try:
            detected_page = len(doc) - 1
            page = doc[detected_page]

            detected_area = {
                "x": max(page.rect.width - 190, 20),
                "y": max(page.rect.height - 100, 20),
                "w": 150,
                "h": 50,
            }

        finally:
            doc.close()

    # --------------------------------------------------
    # CREATE SIGNED PDF
    # --------------------------------------------------
    output_path = os.path.join(
        temp_dir,
        "signed_" + pdf_file.name
    )

    signed_path = place_signature(
        pdf_path=pdf_path,
        page_number=detected_page,
        x_pt=detected_area["x"],
        y_pt=detected_area["y"],
        signature_img_path=signature_path,
        width=detected_area["w"],
        height=detected_area["h"],
        output_path=output_path,
    )

    return signed_path