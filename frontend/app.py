import base64
import html
import os
from datetime import date

import requests
import streamlit as st

from dotenv import load_dotenv


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000",
).rstrip("/")


st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>

    .hero {
        padding: 30px;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            #111827,
            #273449
        );
        color: white;
        margin-bottom: 25px;
    }

    .hero h1 {
        margin: 0;
        font-size: 42px;
    }

    .hero p {
        margin-top: 8px;
        color: #d1d5db;
        font-size: 17px;
    }

    .preview {
        background: #111827;
        color: #f9fafb;
        border-radius: 16px;
        padding: 25px;
        max-height: 650px;
        overflow-y: auto;
        white-space: pre-wrap;
        font-family: Georgia, serif;
        line-height: 1.7;
    }

    .info-box {
        padding: 15px;
        border-left: 4px solid #64748b;
        background: #f3f4f6;
        border-radius: 8px;
        margin-top: 20px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>⚖️ LegalEase</h1>
        <p>
            AI-assisted legal document drafting,
            editing and export.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "document" not in st.session_state:

    st.session_state.document = ""


if "generated_type" not in st.session_state:

    st.session_state.generated_type = (
        "Legal Document"
    )


# --------------------------------------------------
# LAYOUT
# --------------------------------------------------

left_column, right_column = st.columns(
    [0.9, 1.1],
    gap="large",
)


# ==================================================
# LEFT COLUMN
# ==================================================

with left_column:

    st.subheader(
        "1. Document Details"
    )

    document_type = st.text_input(
        "Document Type",
        placeholder=(
            "Example: Freelance Work Contract"
        ),
    )

    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=110,
    )

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=180,
        help=(
            "Separate individual terms using "
            "semicolons (;)."
        ),
    )

    effective_date = st.date_input(
        "Effective Date",
        value=date.today(),
    )

    logo = st.file_uploader(
        "Optional Company Logo",
        type=[
            "png",
            "jpg",
            "jpeg",
        ],
    )

    st.divider()

    generate_button = st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True,
    )


# ==================================================
# GENERATE
# ==================================================

if generate_button:

    if not document_type.strip():

        st.error(
            "Please enter the document type."
        )

    elif not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

    elif not terms.strip():

        st.error(
            "Please enter the terms and conditions."
        )

    else:

        payload = {
            "document_type": (
                document_type.strip()
            ),
            "parties": (
                parties.strip()
            ),
            "terms": (
                terms.strip()
            ),
            "dates": (
                effective_date.strftime(
                    "%B %d, %Y"
                )
            ),
        }

        with st.spinner(
            "Generating your legal document..."
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=120,
                )

                if response.ok:

                    data = response.json()

                    st.session_state.document = (
                        data["document"]
                    )

                    st.session_state.generated_type = (
                        document_type.strip()
                    )

                    if data.get("mock"):

                        st.info(
                            "Demo mode is active. "
                            "Set MOCK_AI=false and "
                            "configure GEMINI_API_KEY "
                            "for real AI generation."
                        )

                    else:

                        st.success(
                            "Document generated successfully."
                        )

                else:

                    try:

                        detail = response.json().get(
                            "detail",
                            response.text,
                        )

                    except Exception:

                        detail = response.text

                    st.error(
                        f"Backend error: {detail}"
                    )

            except requests.RequestException as exc:

                st.error(
                    "Cannot connect to the FastAPI "
                    f"backend at {BACKEND_URL}.\n\n"
                    f"Error: {exc}"
                )


# ==================================================
# RIGHT COLUMN
# ==================================================

with right_column:

    st.subheader(
        "2. Preview & Edit"
    )

    if st.session_state.document:

        edited_document = st.text_area(
            "Editable Document",
            value=st.session_state.document,
            height=500,
            label_visibility="collapsed",
        )

        st.session_state.document = (
            edited_document
        )

        st.markdown(
            "### Styled Preview"
        )

        safe_document = html.escape(
            edited_document
        ).replace(
            "\n",
            "<br>",
        )

        st.markdown(
            f"""
            <div class="preview">
                {safe_document}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        st.markdown(
            "### 3. Download Document"
        )

        # --------------------------------------------------
        # LOGO
        # --------------------------------------------------

        logo_base64 = None

        if logo is not None:

            encoded_logo = base64.b64encode(
                logo.getvalue()
            ).decode()

            if logo.type == "image/png":

                mime_type = "image/png"

            else:

                mime_type = "image/jpeg"

            logo_base64 = (
                f"data:{mime_type};base64,"
                f"{encoded_logo}"
            )

        # --------------------------------------------------
        # EXPORT PAYLOAD
        # --------------------------------------------------

        export_payload = {
            "text": (
                st.session_state.document
            ),
            "document_type": (
                st.session_state.generated_type
            ),
            "terms": terms,
            "logo_base64": logo_base64,
        }

        txt_column, docx_column, pdf_column = (
            st.columns(3)
        )

        # --------------------------------------------------
        # TXT
        # --------------------------------------------------

        with txt_column:

            if st.button(
                "Generate TXT",
                use_container_width=True,
            ):

                try:

                    response = requests.post(
                        f"{BACKEND_URL}/export/txt",
                        json=export_payload,
                        timeout=60,
                    )

                    if response.ok:

                        st.download_button(
                            "⬇️ Save TXT",
                            response.content,
                            file_name=(
                                f"{st.session_state.generated_type}"
                                ".txt"
                            ),
                            mime=(
                                "text/plain"
                            ),
                            use_container_width=True,
                        )

                    else:

                        st.error(
                            response.text
                        )

                except requests.RequestException as exc:

                    st.error(
                        f"TXT export failed: {exc}"
                    )

        # --------------------------------------------------
        # DOCX
        # --------------------------------------------------

        with docx_column:

            if st.button(
                "Generate DOCX",
                use_container_width=True,
            ):

                try:

                    response = requests.post(
                        f"{BACKEND_URL}/export/docx",
                        json=export_payload,
                        timeout=60,
                    )

                    if response.ok:

                        st.download_button(
                            "⬇️ Save DOCX",
                            response.content,
                            file_name=(
                                f"{st.session_state.generated_type}"
                                ".docx"
                            ),
                            mime=(
                                "application/"
                                "vnd.openxmlformats-officedocument."
                                "wordprocessingml.document"
                            ),
                            use_container_width=True,
                        )

                    else:

                        st.error(
                            response.text
                        )

                except requests.RequestException as exc:

                    st.error(
                        f"DOCX export failed: {exc}"
                    )

        # --------------------------------------------------
        # PDF
        # --------------------------------------------------

        with pdf_column:

            if st.button(
                "Generate PDF",
                use_container_width=True,
            ):

                try:

                    response = requests.post(
                        f"{BACKEND_URL}/export/pdf",
                        json=export_payload,
                        timeout=60,
                    )

                    if response.ok:

                        st.download_button(
                            "⬇️ Save PDF",
                            response.content,
                            file_name=(
                                f"{st.session_state.generated_type}"
                                ".pdf"
                            ),
                            mime=(
                                "application/pdf"
                            ),
                            use_container_width=True,
                        )

                    else:

                        st.error(
                            response.text
                        )

                except requests.RequestException as exc:

                    st.error(
                        f"PDF export failed: {exc}"
                    )

    else:

        st.info(
            "Your generated document will appear here."
        )


# ==================================================
# DISCLAIMER
# ==================================================

st.markdown(
    """
    <div class="info-box">
        <strong>Important:</strong>
        LegalEase creates AI-assisted drafts for
        informational purposes. Review the document
        with a qualified legal professional before
        signing or relying on it.
    </div>
    """,
    unsafe_allow_html=True,
)