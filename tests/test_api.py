import os


# Force mock mode during testing.
# This means tests do not require a Gemini API key.
os.environ["MOCK_AI"] = "true"
os.environ["GEMINI_API_KEY"] = "test-key"


from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_root():

    response = client.get("/")

    assert response.status_code == 200

    assert response.json()["status"] == (
        "running"
    )


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "healthy"
    }


def test_generate_mock():

    payload = {
        "document_type": (
            "Freelance Work Contract"
        ),
        "parties": (
            "Jane Doe (Provider), "
            "Example Ltd (Client)"
        ),
        "terms": (
            "Payment within 30 days; "
            "Confidentiality applies"
        ),
        "dates": (
            "September 29, 2026"
        ),
    }

    response = client.post(
        "/generate",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert (
        "FREELANCE WORK CONTRACT"
        in data["document"]
    )


def test_export_txt():

    response = client.post(
        "/export/txt",
        json={
            "text": "HELLO",
            "document_type": "Test",
        },
    )

    assert response.status_code == 200

    assert response.content == b"HELLO"


def test_export_docx():

    response = client.post(
        "/export/docx",
        json={
            "text": "HELLO",
            "document_type": "Test",
        },
    )

    assert response.status_code == 200

    assert (
        response.headers["content-type"]
        .startswith(
            "application/"
        )
    )

    assert len(response.content) > 100


def test_export_pdf():

    response = client.post(
        "/export/pdf",
        json={
            "text": "HELLO",
            "document_type": "Test",
        },
    )

    assert response.status_code == 200

    assert (
        response.headers["content-type"]
        == "application/pdf"
    )

    assert response.content.startswith(
        b"%PDF"
    )


def test_invalid_export_format():

    response = client.post(
        "/export/zip",
        json={
            "text": "HELLO",
        },
    )

    assert response.status_code == 400