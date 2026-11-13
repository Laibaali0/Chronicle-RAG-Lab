"""Time and API-version eligibility checks; boundaries are intentionally explicit."""
from datetime import date
from .schema import Document, Question, as_date


def valid_on(document: Document, when: str | date) -> bool:
    day = as_date(when) if isinstance(when, str) else when
    if day < as_date(document.valid_from):
        return False
    return not document.valid_to or day < as_date(document.valid_to)


def eligible(document: Document, question: Question) -> bool:
    return (document.package == question.package
            and document.version == question.version
            and valid_on(document, question.as_of))


def filter_documents(documents: list[Document], question: Question) -> list[Document]:
    return [document for document in documents if eligible(document, question)]


def conflicting_versions(documents: list[Document], package: str, day: str) -> set[str]:
    return {document.version for document in documents
            if document.package == package and valid_on(document, day)}
