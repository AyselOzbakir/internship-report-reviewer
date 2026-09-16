from io import BytesIO
import requests


SUBMISSIONS_URL = (
    "https://steve107-20107.mikrus.cloud/webhook/internship-submissions"
)

FILE_URL = (
    "https://steve107-20107.mikrus.cloud/webhook/internship-file"
)

STATUS_URL = (
    "https://steve107-20107.mikrus.cloud/webhook/internship-status"
)

APPROVED_URL = (
    "https://steve107-20107.mikrus.cloud/webhook/internship-approved"
)


def get_new_submissions():
    response = requests.get(SUBMISSIONS_URL, timeout=20)
    response.raise_for_status()

    if not response.content.strip():
        return []

    return response.json()


def download_submission_file(drive_file_id, file_name):
    response = requests.get(
        FILE_URL,
        params={"fileId": drive_file_id},
        timeout=30,
    )
    response.raise_for_status()

    file_obj = BytesIO(response.content)
    file_obj.name = file_name
    return file_obj


def update_submission_status(message_id, status):
    response = requests.post(
        STATUS_URL,
        json={
            "messageId": message_id,
            "status": status,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json() if response.content else None

def send_approved_submission(message_id, signed_pdf_path):
    with open(signed_pdf_path, "rb") as signed_pdf:
        response = requests.post(
            APPROVED_URL,
            data={
                "messageId": message_id,
            },
            files={
                "data": (
                    "signed_internship_report.pdf",
                    signed_pdf,
                    "application/pdf",
                )
            },
            timeout=60,
        )

    response.raise_for_status()
    return response.json() if response.content else None