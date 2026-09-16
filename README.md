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
