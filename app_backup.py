import io
from datetime import datetime, timezone


import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
from services.n8n_client import (
    get_new_submissions,
    download_submission_file,
)

from services.document_parser import extract_text
from services.reviewer import compare_documents
from services.signer import sign_uploaded_pdf


# ============================================================
# 1) PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Internship Report Reviewer",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# 2) SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "review_result": None,
    "learning_text": "",
    "journal_text": "",
    "decision": None,
    "signed_pdf_path": None,
    "email_learning_file": None,
    "email_journal_file": None,
    "email_submission_id": None,
    "email_submission_loaded": False,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# 3) CSS
# ============================================================

st.markdown(
    """
    <style>
    :root {
        --bg: #15110E;
        --bg-soft: #1A1511;
        --panel: #1D1713;
        --panel-2: #241C17;

        --orange: #D98A37;
        --amber: #EFB35F;

        --cream: #F2EBE4;
        --text: #DDD4CC;
        --muted: #9C8F85;
        --muted-2: #7E7269;

        --border: rgba(239,179,95,0.13);
        --border-soft: rgba(255,255,255,0.07);

        --ok: #93c598;
        --warn: #e2ad58;
        --bad: #d98070;
    }

    html, body, [class*="css"] {
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 72% 0%, rgba(185, 101, 36, 0.08), transparent 27%),
            radial-gradient(circle at 8% 90%, rgba(105, 66, 39, 0.10), transparent 25%),
            var(--bg);
        color: var(--text);
    }

    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    .block-container {
        max-width: 1380px;
        padding-top: 1.5rem;
        padding-bottom: 5rem;
    }

    section[data-testid="stSidebar"] {
        background: #100D0B;
        border-right: 1px solid var(--border-soft);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.4rem;
    }

    .brand-mark {
        width: 42px;
        height: 42px;
        border-radius: 13px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(145deg, rgba(217,138,55,0.25), rgba(217,138,55,0.06));
        border: 1px solid rgba(239,179,95,0.34);
        color: var(--amber);
        font-family: Georgia, "Times New Roman", serif;
        font-size: 21px;
        margin-bottom: 18px;
    }

    .sidebar-brand {
        font-family: Georgia, "Times New Roman", serif;
        color: var(--cream);
        font-size: 21px;
        line-height: 1.15;
        margin-bottom: 5px;
    }

    .sidebar-sub {
        color: var(--muted);
        font-size: 12px;
        margin-bottom: 28px;
    }

    .sidebar-label {
        color: #796d64;
        font-size: 10px;
        letter-spacing: 1.6px;
        font-weight: 700;
        margin-top: 22px;
        margin-bottom: 13px;
    }

    .sidebar-row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 9px 2px;
        color: #9f9389;
        font-size: 12px;
    }

    .sidebar-row.active { color: var(--cream); }

    .sidebar-index {
        width: 22px;
        color: var(--orange);
        font-size: 10px;
    }

    .online-box {
        margin-top: 24px;
        padding: 13px 14px;
        border-radius: 12px;
        background: rgba(100, 137, 96, 0.08);
        border: 1px solid rgba(115, 162, 110, 0.15);
        color: #9bc39a;
        font-size: 11px;
    }

    .human-card {
        margin-top: 28px;
        padding: 17px;
        border-radius: 14px;
        background: var(--panel);
        border: 1px solid var(--border-soft);
        color: var(--muted);
        font-size: 11px;
        line-height: 1.65;
    }

    .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 5px 0 20px 0;
        border-bottom: 1px solid var(--border-soft);
        margin-bottom: 28px;
    }

    .topbar-name {
        font-size: 12px;
        color: var(--muted);
    }

    .topbar-accent { color: var(--orange); }

    .topbar-status {
        font-size: 11px;
        color: #80746c;
    }

    .hero {
        padding: 28px 0 35px 0;
    }

    .eyebrow {
        color: var(--orange);
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 2.2px;
        margin-bottom: 15px;
    }

    .hero-title {
        font-family: Georgia, "Times New Roman", serif;
        color: var(--cream);
        font-size: clamp(42px, 5vw, 68px);
        font-weight: 400;
        line-height: 1.02;
        letter-spacing: -2.5px;
        max-width: 900px;
        margin-bottom: 18px;
    }

    .hero-copy {
        color: var(--muted);
        max-width: 740px;
        font-size: 14px;
        line-height: 1.7;
    }

    .section-header {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        margin-top: 14px;
        margin-bottom: 16px;
    }

    .section-kicker {
        color: var(--orange);
        font-size: 10px;
        letter-spacing: 1.7px;
        font-weight: 700;
        margin-bottom: 6px;
    }

    .section-title {
        font-family: Georgia, "Times New Roman", serif;
        color: var(--cream);
        font-size: 27px;
        font-weight: 400;
    }

    .section-description {
        color: var(--muted);
        font-size: 12px;
        margin-top: 5px;
    }

    .doc-label {
        color: var(--cream);
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 5px;
    }

    .doc-description {
        color: var(--muted);
        font-size: 11px;
        margin-bottom: 9px;
    }

    div[data-testid="stFileUploader"] {
        padding: 10px;
        background: var(--panel);
        border: 1px solid var(--border-soft);
        border-radius: 15px;
    }

    div[data-testid="stFileUploaderDropzone"] {
        background: #17120f;
        border: 1px dashed rgba(239,179,95,0.24);
        border-radius: 12px;
        min-height: 125px;
    }

    div[data-testid="stFileUploaderDropzone"]:hover {
        border-color: rgba(239,179,95,0.55);
    }

    div.stButton > button {
        min-height: 48px;
        border-radius: 11px;
        background: #211a15;
        color: var(--cream);
        border: 1px solid rgba(239,179,95,0.17);
        font-weight: 600;
        transition: transform 0.15s ease, border-color 0.15s ease, background 0.15s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-1px);
        background: #292019;
        border-color: rgba(239,179,95,0.47);
        color: white;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #d68a38, #bd6c27);
        color: #17100b;
        border: none;
    }

    div[data-testid="stDownloadButton"] > button {
        width: 100%;
        min-height: 48px;
        border-radius: 11px;
        background: var(--amber);
        border: none;
        color: #21160d;
        font-weight: 700;
    }

    div[data-testid="stMetric"] {
        min-height: 112px;
        padding: 18px 19px;
        background: var(--panel);
        border: 1px solid var(--border-soft);
        border-radius: 14px;
    }

    div[data-testid="stMetricLabel"] { color: var(--muted); }
    div[data-testid="stMetricValue"] { color: var(--cream); }

    .status-banner {
        margin: 4px 0 20px 0;
        padding: 13px 16px;
        border-radius: 12px;
        background: rgba(217,138,55,0.075);
        border: 1px solid rgba(217,138,55,0.22);
        color: #dcb27c;
        font-size: 12px;
    }

    .finding {
        display: flex;
        align-items: flex-start;
        gap: 13px;
        padding: 16px 16px;
        margin-bottom: 9px;
        background: var(--panel);
        border: 1px solid var(--border-soft);
        border-radius: 13px;
    }

    .finding-icon {
        width: 26px;
        height: 26px;
        flex: 0 0 26px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 800;
    }

    .finding-icon.pass {
        background: rgba(112,163,119,0.13);
        color: var(--ok);
    }

    .finding-icon.warning {
        background: rgba(217,162,75,0.12);
        color: var(--warn);
    }

    .finding-icon.fail {
        background: rgba(199,105,89,0.12);
        color: var(--bad);
    }

    .finding-title {
        color: var(--cream);
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .finding-copy {
        color: var(--muted);
        font-size: 11px;
        line-height: 1.5;
    }

    .action-panel-title {
        font-family: Georgia, "Times New Roman", serif;
        color: var(--cream);
        font-size: 25px;
        font-weight: 400;
        margin-bottom: 5px;
    }

    .action-panel-copy {
        color: var(--muted);
        font-size: 11px;
        line-height: 1.6;
        margin-bottom: 14px;
    }

    .action-card {
        padding: 19px;
        background: linear-gradient(145deg, #211914, #1b1511);
        border: 1px solid rgba(239,179,95,0.14);
        border-radius: 15px;
        margin-bottom: 16px;
    }

    .signature-title {
        color: var(--cream);
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .signature-copy {
        color: var(--muted);
        font-size: 11px;
        margin-bottom: 10px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 5px;
        background: #17120f;
        padding: 4px;
        border-radius: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: var(--muted);
        font-size: 11px;
    }

    .stTabs [aria-selected="true"] {
        background: #2b2018 !important;
        color: var(--amber) !important;
    }

    div[data-testid="stExpander"] {
        background: var(--panel);
        border: 1px solid var(--border-soft);
        border-radius: 12px;
    }

    hr { border-color: var(--border-soft) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 4) HELPER FUNCTIONS
# ============================================================

def render_finding(check: dict) -> None:
    status = check["status"].lower()

    icons = {
        "pass": "✓",
        "warning": "!",
        "fail": "×",
    }

    icon = icons.get(status, "•")

    st.html(
        f"""
        <div class="finding">
            <div class="finding-icon {status}">{icon}</div>
            <div>
                <div class="finding-title">{check["title"]}</div>
                <div class="finding-copy">{check["message"]}</div>
            </div>
        </div>
        """
    )


def reset_file_pointer(file_obj):
    if hasattr(file_obj, "seek"):
        try:
            file_obj.seek(0)
        except Exception:
            pass


def parse_created_at(value):
    fallback = datetime.min.replace(tzinfo=timezone.utc)

    if not value:
        return fallback

    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except (TypeError, ValueError):
        return fallback


def fetch_latest_email_submission():
    rows = get_new_submissions() or []
    grouped = {}

    for row in rows:
        message_id = row.get("messageId")
        document_type = row.get("documentType")

        if not message_id:
            continue

        if document_type not in {"internship_journal", "learning_outcomes"}:
            continue

        created_at = parse_created_at(row.get("createdAt"))

        group = grouped.setdefault(
            message_id,
            {
                "message_id": message_id,
                "created_at": created_at,
                "documents": {},
            },
        )

        if created_at > group["created_at"]:
            group["created_at"] = created_at

        existing_row = group["documents"].get(document_type)
        if (
            existing_row is None
            or created_at >= parse_created_at(existing_row.get("createdAt"))
        ):
            group["documents"][document_type] = row

    complete_groups = [
        group
        for group in grouped.values()
        if "internship_journal" in group["documents"]
        and "learning_outcomes" in group["documents"]
    ]

    if not complete_groups:
        return None

    latest_group = max(
        complete_groups,
        key=lambda item: (item["created_at"], item["message_id"]),
    )

    learning_row = latest_group["documents"]["learning_outcomes"]
    journal_row = latest_group["documents"]["internship_journal"]

    learning_file = download_submission_file(
        learning_row["driveFileId"],
        learning_row["fileName"],
    )
    journal_file = download_submission_file(
        journal_row["driveFileId"],
        journal_row["fileName"],
    )

    reset_file_pointer(learning_file)
    reset_file_pointer(journal_file)

    return {
        "message_id": latest_group["message_id"],
        "learning_file": learning_file,
        "journal_file": journal_file,
    }


def canvas_to_signature(canvas_result):
    if canvas_result.image_data is None:
        return None

    if canvas_result.json_data is None:
        return None

    objects = canvas_result.json_data.get("objects", [])

    if not objects:
        return None

    image = Image.fromarray(
    canvas_result.image_data.astype("uint8"),
    "RGBA"
).copy()

    pixels = image.load()

    # Remove light/cream canvas background
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = pixels[x, y]

            # Any very light background becomes transparent
            if r > 215 and g > 210 and b > 200:
                pixels[x, y] = (255, 255, 255, 0)

    # Crop transparent empty space around signature
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()

    if bbox:
        image = image.crop(bbox)

    # Small transparent padding around the signature
    padded = Image.new(
        "RGBA",
        (image.width + 20, image.height + 20),
        (255, 255, 255, 0)
    )

    padded.paste(
        image,
        (10, 10),
        image
    )

    buffer = io.BytesIO()

    padded.save(
        buffer,
        format="PNG"
    )

    buffer.seek(0)
    buffer.name = "drawn_signature.png"

    return buffer


# ============================================================
# 5) SIDEBAR
# ============================================================

with st.sidebar:
    st.html(
        """
        <div class="brand-mark">R</div>

        <div class="sidebar-brand">Report Reviewer</div>
        <div class="sidebar-sub">Internship completions</div>

        <div class="sidebar-label">WORKFLOW</div>

        <div class="sidebar-row active"><span class="sidebar-index">01</span>Submission</div>
        <div class="sidebar-row"><span class="sidebar-index">02</span>Extraction</div>
        <div class="sidebar-row"><span class="sidebar-index">03</span>Validation</div>
        <div class="sidebar-row"><span class="sidebar-index">04</span>Decision & signing</div>

        <div class="online-box">● Review engine online</div>

        <div class="human-card">
            <b style="color:#eee4da;">Human-in-the-loop</b><br><br>
            Automated checks prepare evidence and recommendations.
            The internship coordinator retains final approval authority.
        </div>
        """
    )


# ============================================================
# 6) HEADER / HERO
# ============================================================

st.html(
    """
    <div class="topbar">
        <div class="topbar-name">
            Internship Coordinator
            <span class="topbar-accent"> / </span>
            Report Reviewer
        </div>
        <div class="topbar-status">academic workflow automation</div>
    </div>
    """
)

st.html(
    """
    <div class="hero">
        <div class="eyebrow">INTERNSHIP COMPLETIONS</div>
        <div class="hero-title">
            Review the work.<br>
            Keep the final word.
        </div>
        <div class="hero-copy">
            Compare the student's learning outcomes with the internship
            journal, surface missing evidence and inconsistencies, then
            prepare the submission for coordinator approval and signing.
        </div>
    </div>
    """
)


# ============================================================
# 7) UPLOAD FORM
# ============================================================

st.html(
    """
    <div class="section-header">
        <div>
            <div class="section-kicker">NEW SUBMISSION</div>
            <div class="section-title">Internship documents</div>
            <div class="section-description">
                Add both documents before beginning the review.
            </div>
        </div>
    </div>
    """
)

upload_left, upload_right = st.columns(2, gap="large")

with upload_left:
    st.html(
        """
        <div class="doc-label">Learning Outcomes Report</div>
        <div class="doc-description">
            Report on the achievement of learning outcomes
        </div>
        """
    )
    learning_report = st.file_uploader(
        "Learning Outcomes Report",
        type=["pdf", "docx"],
        key="learning_report",
        label_visibility="collapsed",
    )

with upload_right:
    st.html(
        """
        <div class="doc-label">Student Internship Journal</div>
        <div class="doc-description">
            Student's dated internship activity journal
        </div>
        """
    )
    internship_journal = st.file_uploader(
        "Student Internship Journal",
        type=["pdf", "docx"],
        key="internship_journal",
        label_visibility="collapsed",
    )

st.write("")

st.caption("Or load the latest complete document pair received by email.")

load_email_submission = st.button(
    "Load latest email submission",
    key="load_latest_email_submission",
)

if load_email_submission:
    try:
        submission = fetch_latest_email_submission()

        if submission is None:
            st.session_state.email_learning_file = None
            st.session_state.email_journal_file = None
            st.session_state.email_submission_id = None
            st.session_state.email_submission_loaded = False
            st.warning("No complete email submission is available right now.")
        else:
            st.session_state.email_learning_file = submission["learning_file"]
            st.session_state.email_journal_file = submission["journal_file"]
            st.session_state.email_submission_id = submission["message_id"]
            st.session_state.email_submission_loaded = True
    except Exception as error:
        st.error(f"Unable to load email submission: {error}")

if (
    st.session_state.email_submission_loaded
    and st.session_state.email_learning_file is not None
    and st.session_state.email_journal_file is not None
):
    st.info(
        "Email submission loaded\n\n"
        f"- {st.session_state.email_learning_file.name}\n"
        f"- {st.session_state.email_journal_file.name}"
    )

effective_learning_file = (
    learning_report
    if learning_report is not None
    else st.session_state.email_learning_file
)

effective_journal_file = (
    internship_journal
    if internship_journal is not None
    else st.session_state.email_journal_file
)

analyze = st.button(
    "Run document review",
    type="primary",
    use_container_width=True,
)


# ============================================================
# 8) REVIEW PROCESSING
# ============================================================

if analyze:
    st.session_state.signed_pdf_path = None
    st.session_state.decision = None

    if effective_learning_file is None or effective_journal_file is None:
        st.warning(
            "Upload both the Learning Outcomes Report and the Student Internship Journal first."
        )
    else:
        try:
            reset_file_pointer(effective_learning_file)
            reset_file_pointer(effective_journal_file)

            with st.spinner("Reading and comparing the internship documents..."):
                learning_text = extract_text(effective_learning_file)
                journal_text = extract_text(effective_journal_file)

            if not learning_text.strip():
                st.error("No readable text was found in the Learning Outcomes Report.")
            elif not journal_text.strip():
                st.error("No readable text was found in the Student Internship Journal.")
            else:
                review = compare_documents(learning_text, journal_text)
                st.session_state.learning_text = learning_text
                st.session_state.journal_text = journal_text
                st.session_state.review_result = review
        except Exception as error:
            st.error(f"Document review failed: {error}")


# ============================================================
# 9) REVIEW DASHBOARD
# ============================================================

review = st.session_state.review_result

if review is not None:
    checks = review.get("checks", [])

    passed = sum(check.get("status") == "PASS" for check in checks)
    warnings = sum(check.get("status") == "WARNING" for check in checks)
    failed = sum(check.get("status") == "FAIL" for check in checks)

    st.html("<br>")

    st.html(
        f"""
        <div class="section-header">
            <div>
                <div class="section-kicker">REVIEW</div>
                <div class="section-title">Submission overview</div>
                <div class="section-description">
                    Automated evidence prepared for coordinator review.
                </div>
            </div>
        </div>

        <div class="status-banner">
            Current recommendation:
            <strong>{review.get("status", "UNKNOWN").replace("_", " ")}</strong>
        </div>
        """
    )

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Review score", f'{review.get("score", 0)} / 100')
    with m2:
        st.metric("Checks passed", passed)
    with m3:
        st.metric("Warnings", warnings)
    with m4:
        st.metric("Issues", failed)

    st.write("")

    review_column, action_column = st.columns([1.75, 0.85], gap="large")

    with review_column:
        st.html(
            """
            <div class="section-kicker">FINDINGS</div>
            <div class="section-title">Validation evidence</div>
            <div class="section-description">
                Review the automated checks before making a final decision.
            </div>
            <br>
            """
        )

        for check in checks:
            render_finding(check)

        st.html(
            """
            <br>
            <div class="section-kicker">SOURCE DOCUMENTS</div>
            <div class="section-title">Extracted text</div>
            <div class="section-description">
                Use these excerpts to verify finding context.
            </div>
            """
        )

        with st.expander("Learning Outcomes Report", expanded=False):
            st.text(st.session_state.learning_text[:8000])

        with st.expander("Student Internship Journal", expanded=False):
            st.text(st.session_state.journal_text[:8000])

    # ========================================================
    # 10) COORDINATOR DECISION / SIGNATURE
    # ========================================================

    with action_column:
        st.html(
            """
            <div class="action-panel-title">Coordinator decision</div>
            <div class="action-panel-copy">
                The automated review is advisory.
                Review the evidence, sign the report or return it to the student for correction.
            </div>
            """
        )

        st.html(
            """
            <div class="action-card">
                <div class="signature-title">Coordinator signature</div>
                <div class="signature-copy">
                    Draw with your mouse or trackpad, or upload an existing signature.
                </div>
            </div>
            """
        )

        draw_tab, upload_tab = st.tabs(["Draw signature", "Upload image"])

        drawn_signature = None
        uploaded_signature = None

        with draw_tab:
                canvas_result = st_canvas(
                    fill_color="rgba(0,0,0,0)",
                    stroke_width=3,
                    stroke_color="#1b1714",
                    background_color="#FFFFFF",
                    height=180,
                    width=430,
                    drawing_mode="freedraw",
                    update_streamlit=True,
                    return_image_data=True,
                    key="signature_canvas",
                )
                drawn_signature = canvas_to_signature(canvas_result)

        with upload_tab:
            uploaded_signature = st.file_uploader(
                "Signature image",
                type=["png", "jpg", "jpeg"],
                key="uploaded_signature",
                label_visibility="collapsed",
            )

        signature_file = uploaded_signature if uploaded_signature is not None else drawn_signature

        st.write("")

        correction = st.button(
            "Request correction",
            use_container_width=True,
            key="request_correction",
        )

        approve = st.button(
            "Approve & Sign",
            type="primary",
            use_container_width=True,
            key="approve_sign",
        )

        if correction:
            st.session_state.decision = "CORRECTION"
            st.session_state.signed_pdf_path = None

        if approve:
            if signature_file is None:
                st.error("Draw or upload the coordinator signature first.")
            elif effective_learning_file is None:
                st.error("Learning Outcomes Report is missing.")
            elif not getattr(effective_learning_file, "name", "").lower().endswith(".pdf"):
                st.error("Signing currently requires the Learning Outcomes Report in PDF format.")
            else:
                try:
                    reset_file_pointer(effective_learning_file)
                    reset_file_pointer(signature_file)

                    with st.spinner("Signing the approved report..."):
                        signed_path = sign_uploaded_pdf(
                            effective_learning_file,
                            signature_file,
                        )

                    st.session_state.decision = "APPROVED"
                    st.session_state.signed_pdf_path = signed_path
                except Exception as error:
                    st.error(f"Signing failed: {error}")

        if st.session_state.decision == "CORRECTION":
            st.warning(
                "Correction requested. The submission should be returned to the student."
            )
        elif st.session_state.decision == "APPROVED":
            st.success("Approved and signed successfully.")

        # ====================================================
        # 11) DOWNLOAD STATE
        # ====================================================

        if st.session_state.signed_pdf_path:
            with open(st.session_state.signed_pdf_path, "rb") as signed_pdf:
                signed_data = signed_pdf.read()

            st.download_button(
                "Download signed report",
                data=signed_data,
                file_name="signed_internship_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

else:
    st.html(
        """
        <br>
        <div style="
            border-top: 1px solid rgba(255,255,255,0.06);
            padding-top: 28px;
            color: #756a62;
            font-size: 12px;
        ">
            Upload both internship documents and run the review
            to open the coordinator workspace.
        </div>
        """
    )
