

````markdown
# Internship Report Reviewer

A lightweight internship completion review system for validating student internship documentation, supporting coordinator review, and signing approved reports.

## Overview

The Internship Report Reviewer is designed for the final stage of an internship workflow.

Students submit:

- Report on the achievement of learning outcomes
- Student internship journal

The system:

1. Extracts text from both documents
2. Performs deterministic validation checks
3. Compares the learning outcomes report with the internship journal
4. Produces PASS / WARNING / FAIL findings
5. Gives the internship coordinator a final decision interface
6. Allows the coordinator to draw or upload a signature
7. Generates a signed PDF for download

The coordinator remains in control of the final academic decision.

---

## Current MVP

The current version supports:

- PDF and DOCX upload
- Text extraction
- Rule-based document validation
- Journal date detection
- Document consistency checks
- Review score
- PASS / WARNING / FAIL findings
- Human-in-the-loop coordinator decision
- Request correction flow
- Drawn signature with mouse or trackpad
- Uploaded signature image
- PDF signing
- Signed PDF download
- Dark brown / amber Streamlit interface

---

## Workflow

```text
Student Submission
        |
        v
Learning Outcomes Report + Internship Journal
        |
        v
Document Extraction
        |
        v
Validation & Comparison
        |
        v
Review Findings
        |
        v
Coordinator Decision
       / \
      /   \
Correction  Approve
              |
              v
           Sign PDF
              |
              v
       Download Signed Report
````

---

## Project Structure

```text
internship-report-reviewer/
│
├── app.py
├── requirements.txt
├── .gitignore
│
├── services/
│   ├── document_parser.py
│   ├── reviewer.py
│   ├── signer.py
│   └── pdf_backend.py
│
├── n8n/
├── assets/
├── uploads/
└── outputs/
```

---

## Technology Stack

* Python
* Streamlit
* PyPDF
* python-docx
* PyMuPDF
* Pillow
* streamlit-drawable-canvas
* n8n
* Gmail API

---

## Validation Logic

The current MVP uses deterministic checks instead of making the final decision with AI.

Example checks include:

* Learning Outcomes Report completeness
* Internship Journal completeness
* Dated journal entries
* Consistency between journal activities and learning outcomes
* Signature-related evidence

The output contains:

* Review score
* Overall recommendation
* PASS / WARNING / FAIL findings
* Supporting messages for the coordinator

The automated recommendation is advisory.

The internship coordinator makes the final decision.

---

## PDF Signing

The coordinator can either:

* Draw a signature using a mouse or trackpad
* Upload an existing PNG / JPG signature

After approval, the system places the signature into the Learning Outcomes Report and creates a signed PDF.

---

## Email Automation

An n8n workflow is currently being developed to support:

```text
Gmail
  |
  v
Internship email detected
  |
  v
Download attachments
  |
  v
Identify internship documents
  |
  v
Send submission to review workflow
```

Manual upload remains available as a fallback and testing method.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/AyselOzbakir/internship-report-reviewer.git
cd internship-report-reviewer
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

---

## Security

Secrets and local environment files are not committed to the repository.

The following are ignored by Git:

* `.env`
* `.venv`
* Streamlit secrets
* Local upload/output files
* VS Code settings

Do not commit API keys, OAuth secrets, or student documents.

---

## Planned Improvements

* Gmail + n8n attachment intake
* Automatic document classification
* Submission metadata extraction
* Review history / queue
* Automatic correction email
* Signed report email delivery
* Improved signature-field detection
* Optional semantic / AI-assisted review
* Persistent storage with SQLite

---

## Human-in-the-loop

The reviewer is designed to assist, not replace, the internship coordinator.

Automated checks provide evidence and recommendations, while final approval and signing remain under human control.

````

