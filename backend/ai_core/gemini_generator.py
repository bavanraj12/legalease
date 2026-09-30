import os

from dotenv import load_dotenv


load_dotenv()


try:
    from google import genai
except ImportError:
    genai = None


class GeminiDocumentGenerator:
    """
    Generates AI-assisted legal-document drafts
    using Google's Gemini API.
    """

    def __init__(self):

        self.api_key = os.getenv(
            "GEMINI_API_KEY",
            "",
        ).strip()

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash",
        ).strip()

        self.mock_ai = (
            os.getenv(
                "MOCK_AI",
                "false",
            ).lower()
            == "true"
        )

        self.client = None

        if not self.mock_ai:

            if not self.api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY is not configured."
                )

            if genai is None:
                raise RuntimeError(
                    "google-genai is not installed."
                )

            self.client = genai.Client(
                api_key=self.api_key
            )

    @staticmethod
    def build_prompt(
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:

        prompt = f"""
You are LegalEase, an AI-assisted legal-document
drafting system.

Create a professional FIRST DRAFT of the requested
legal document.

IMPORTANT:

1. Do not claim that the document is legally valid.
2. Do not claim that the document is enforceable.
3. Do not provide jurisdiction-specific legal advice
   unless the user explicitly provides the jurisdiction.
4. Do not invent names.
5. Do not invent dates.
6. Do not invent addresses.
7. Do not invent payment amounts.
8. Do not invent laws.
9. Do not invent facts.
10. Preserve the information supplied by the user.
11. Use [MISSING INFORMATION] where necessary.
12. The result must be suitable for editing.
13. Use professional formal language.
14. Number the major sections.
15. End with a Drafting Note.

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

TERMS AND CONDITIONS:
{terms}

EFFECTIVE DATE:
{dates}

Use this structure when appropriate:

TITLE

PARTIES

EFFECTIVE DATE

RECITALS / PURPOSE

DEFINITIONS

TERMS AND CONDITIONS

PAYMENT

CONFIDENTIALITY

INTELLECTUAL PROPERTY

TERM

TERMINATION

GOVERNING LAW

DISPUTE RESOLUTION

GENERAL PROVISIONS

SIGNATURES

Only include sections that are relevant to the
requested document.

Preserve every important user-supplied term.

At the end write:

Drafting Note:
This is an AI-generated draft for informational
purposes and should be reviewed by a qualified legal
professional before signing or relying upon it.
"""

        return prompt.strip()

    @staticmethod
    def mock_document(
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:

        terms_list = [
            term.strip()
            for term in terms.split(";")
            if term.strip()
        ]

        formatted_terms = "\n".join(
            f"{index}. {term}"
            for index, term in enumerate(
                terms_list,
                start=1,
            )
        )

        if not formatted_terms:
            formatted_terms = (
                "[MISSING INFORMATION]"
            )

        return f"""
{document_type.upper()}

1. PARTIES

{parties}

2. EFFECTIVE DATE

{dates}

3. TERMS AND CONDITIONS

{formatted_terms}

4. GENERAL PROVISIONS

This draft records the terms supplied by the user.
Additional provisions may be required depending on
the nature and jurisdiction of the agreement.

5. SIGNATURES

Party 1:

Name: ______________________________

Signature: _________________________

Date: ______________________________


Party 2:

Name: ______________________________

Signature: _________________________

Date: ______________________________


DRAFTING NOTE

This is an AI-generated draft for informational
purposes and should be reviewed by a qualified legal
professional before signing or relying upon it.
""".strip()

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ) -> str:

        if self.mock_ai:

            return self.mock_document(
                document_type,
                parties,
                terms,
                dates,
            )

        prompt = self.build_prompt(
            document_type,
            parties,
            terms,
            dates,
        )

        try:

            response = (
                self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                )
            )

        except Exception as exc:

            raise RuntimeError(
                f"Gemini generation failed: {exc}"
            ) from exc

        generated_text = getattr(
            response,
            "text",
            None,
        )

        if not generated_text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        generated_text = generated_text.strip()

        if not generated_text:
            raise RuntimeError(
                "Gemini returned an empty document."
            )

        return generated_text