from io import BytesIO
import requests


SUBMISSIONS_URL = (
    "https://steve107-20107.mikrus.cloud/webhook/internship-submissions"
)

FILE_URL = (
    "https://steve107-20107.mikrus.cloud/webhook/internship-file"
)


def get_new_submissions():
    response = requests.get(SUBMISSIONS_URL, timeout=20)
    response.raise_for_status()
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
