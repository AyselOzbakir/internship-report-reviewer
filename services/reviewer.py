import os
import re
from typing import Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field


load_dotenv()


# ============================================================
# STRUCTURED AI RESPONSE
# ============================================================

class ReviewCheck(BaseModel):
    title: str

    status: Literal[
        "PASS",
        "WARNING",
        "FAIL"
    ]

    message: str

    evidence: str


class InternshipReview(BaseModel):
    status: Literal[
        "APPROVED",
        "NEEDS_REVIEW",
        "REJECTED"
    ]

    score: int = Field(
        ge=0,
        le=100
    )

    summary: str

    checks: list[ReviewCheck]


# ============================================================
# RULE-BASED FALLBACK
# ============================================================

def _clean_words(text):
    words = re.findall(
        r"\b[a-zA-Z]{4,}\b",
        text.lower()
    )

    ignored = {
        "this",
        "that",
        "with",
        "from",
        "have",
        "been",
        "were",
        "they",
        "their",
        "during",
        "throughout",
        "student",
        "internship",
        "report",
        "journal",
        "about",
        "into",
        "also",
    }

    return {
        word
        for word in words
        if word not in ignored
    }


def _rule_based_review(
    learning_text,
    journal_text
):
    checks = []

    # Learning outcomes report
    if len(learning_text.strip()) >= 100:
        checks.append({
            "title": "Learning Outcomes Report",
            "status": "PASS",
            "message": (
                "The learning outcomes report contains "
                "sufficient readable content."
            ),
            "evidence": (
                "Readable learning outcomes content detected."
            )
        })
    else:
        checks.append({
            "title": "Learning Outcomes Report",
            "status": "FAIL",
            "message": (
                "The learning outcomes report appears "
                "too short or incomplete."
            ),
            "evidence": (
                "Insufficient readable report content."
            )
        })

    # Journal
    if len(journal_text.strip()) >= 100:
        checks.append({
            "title": "Internship Journal",
            "status": "PASS",
            "message": (
                "The internship journal contains "
                "sufficient activity records."
            ),
            "evidence": (
                "Readable journal activities detected."
            )
        })
    else:
        checks.append({
            "title": "Internship Journal",
            "status": "FAIL",
            "message": (
                "The internship journal appears "
                "too short or incomplete."
            ),
            "evidence": (
                "Insufficient journal content."
            )
        })

    # Dates
    dates = re.findall(
        r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b",
        journal_text
    )

    if len(dates) >= 3:
        checks.append({
            "title": "Journal Dates",
            "status": "PASS",
            "message": (
                f"{len(dates)} dated internship "
                "entries were detected."
            ),
            "evidence": ", ".join(dates[:5])
        })

    elif dates:
        checks.append({
            "title": "Journal Dates",
            "status": "WARNING",
            "message": (
                "Only a small number of dated "
                "entries were detected."
            ),
            "evidence": ", ".join(dates)
        })

    else:
        checks.append({
            "title": "Journal Dates",
            "status": "FAIL",
            "message": (
                "No dated journal entries were detected."
            ),
            "evidence": "No dates detected."
        })

    # Consistency
    learning_words = _clean_words(
        learning_text
    )

    journal_words = _clean_words(
        journal_text
    )

    common_words = learning_words.intersection(
        journal_words
    )

    overlap = (
        len(common_words) / len(learning_words)
        if learning_words
        else 0
    )

    if overlap >= 0.20:
        consistency = "PASS"
        consistency_message = (
            "The journal contains supporting evidence "
            "for the reported learning outcomes."
        )

    elif overlap >= 0.08:
        consistency = "WARNING"
        consistency_message = (
            "Only limited evidence connects the journal "
            "to the reported learning outcomes."
        )

    else:
        consistency = "FAIL"
        consistency_message = (
            "Little supporting evidence was found "
            "between the two documents."
        )

    checks.append({
        "title": "Document Consistency",
        "status": consistency,
        "message": consistency_message,
        "evidence": (
            ", ".join(sorted(common_words)[:10])
            or "No meaningful overlap detected."
        )
    })

    # Signature evidence
    combined = (
        learning_text + " " + journal_text
    ).lower()

    if (
        "signature" in combined
        or "signed" in combined
    ):
        signature_status = "PASS"
        signature_message = (
            "Signature-related information was detected."
        )
    else:
        signature_status = "WARNING"
        signature_message = (
            "No signature evidence was detected automatically."
        )

    checks.append({
        "title": "Signature Evidence",
        "status": signature_status,
        "message": signature_message,
        "evidence": (
            "Signature keyword check."
        )
    })

    weights = {
        "PASS": 20,
        "WARNING": 10,
        "FAIL": 0,
    }

    score = sum(
        weights[item["status"]]
        for item in checks
    )

    fails = sum(
        item["status"] == "FAIL"
        for item in checks
    )

    warnings = sum(
        item["status"] == "WARNING"
        for item in checks
    )

    if fails >= 2:
        status = "REJECTED"

    elif fails == 1 or warnings >= 2:
        status = "NEEDS_REVIEW"

    else:
        status = "APPROVED"

    return {
        "status": status,
        "score": score,
        "summary": (
            "Rule-based fallback review."
        ),
        "checks": checks,
        "engine": "RULES"
    }


# ============================================================
# AI REVIEWER
# ============================================================

def _ai_review(
    learning_text,
    journal_text
):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5.6-luna"
    )

    system_prompt = """
You are an internship documentation reviewer assisting
an academic internship coordinator.

You receive two documents:

1. Report on the achievement of learning outcomes
2. Student internship journal

Your task is to compare the documents and prepare evidence
for a HUMAN coordinator.

You do NOT make the final academic decision.
You do NOT invent missing information.

Review the documents for:

- completeness of the learning outcomes report
- completeness and credibility of the internship journal
- dated internship activity entries
- whether journal activities support the claimed learning outcomes
- contradictions between the two documents
- missing or unsupported claims
- signature-related evidence if explicitly visible in extracted text

Important rules:

- Base every conclusion only on the supplied documents.
- If evidence is absent, explicitly say it is absent.
- Do not guess student names, dates, employers or activities.
- A PASS requires clear supporting evidence.
- Use WARNING when something is uncertain, incomplete,
  or cannot be verified reliably.
- Use FAIL for meaningful contradiction, missing required
  information, or unsupported learning outcome claims.
- Keep each finding concise and professional.
- Evidence should quote or paraphrase the relevant factual
  information briefly.
- Do not reject a document merely because extracted text
  does not contain the word "signature"; mark this as WARNING
  when visual verification may still be needed.

Scoring guidance:

90-100:
Strong, complete and consistent documentation.

75-89:
Mostly complete with minor issues.

50-74:
Meaningful issues requiring coordinator review.

0-49:
Major missing information, contradictions,
or inadequate supporting evidence.

Overall status:

APPROVED:
No meaningful FAIL findings and documentation
is sufficiently supported.

NEEDS_REVIEW:
Uncertainty, warnings or a limited number of problems
require human review.

REJECTED:
Major contradictions, serious incompleteness,
or multiple unsupported claims.

Remember:
Your result is advisory.
The coordinator makes the final decision.
"""

    user_prompt = f"""
LEARNING OUTCOMES REPORT
========================
{learning_text[:15000]}


STUDENT INTERNSHIP JOURNAL
==========================
{journal_text[:15000]}
"""

    response = client.responses.parse(
        model=model,
        input=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        text_format=InternshipReview,
    )

    result = response.output_parsed

    if result is None:
        raise RuntimeError(
            "AI reviewer returned no structured result."
        )

    data = result.model_dump()

    data["engine"] = "AI"

    return data


# ============================================================
# PUBLIC FUNCTION USED BY APP.PY
# ============================================================

def compare_documents(
    learning_text,
    journal_text
):
    """
    Main reviewer used by app.py.

    Uses AI when OPENAI_API_KEY is configured.
    Falls back to deterministic validation if
    the API is unavailable.
    """

    api_key = os.getenv(
        "OPENAI_API_KEY"
    )

    if not api_key:
        return _rule_based_review(
            learning_text,
            journal_text
        )

    try:
        return _ai_review(
            learning_text,
            journal_text
        )

    except Exception as error:
        fallback = _rule_based_review(
            learning_text,
            journal_text
        )

        fallback["engine"] = "RULES_FALLBACK"
        fallback["ai_error"] = str(error)

        return fallback