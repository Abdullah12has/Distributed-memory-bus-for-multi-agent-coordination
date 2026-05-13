"""PII redaction.

Two-stage:
* Regex sweep for obvious patterns (emails, phone, IBAN, IP addresses).
* Optional NER sweep via ``en_core_web_lg`` for PERSON / ORG / GPE entities.

Used by :class:`m6.corpus.loader.InstitutionalCorpus`; refuses to return a
document that has not passed redaction.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Pre-compiled regexes — common European campus-document PII patterns.
_EMAIL_RE = re.compile(r"\b[\w.\-+]+@[\w.\-]+\.[A-Za-z]{2,}\b")
_PHONE_RE = re.compile(r"\b(?:\+?\d[\d\s\-()]{6,}\d)\b")
_IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b")
_IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_PERSON_NAME_RE = re.compile(r"\b(?:[A-Z][a-z]+)\s+(?:[A-Z][a-z]+){1,2}\b")  # heuristic


@dataclass(frozen=True)
class RedactionReport:
    """What was redacted, by category. Counts only — never the original."""

    emails: int = 0
    phones: int = 0
    ibans: int = 0
    ips: int = 0
    persons: int = 0
    organizations: int = 0


def redact(text: str, *, use_ner: bool = False) -> tuple[str, RedactionReport]:
    """Return ``(redacted_text, report)``."""
    redacted = text
    emails = len(_EMAIL_RE.findall(redacted))
    redacted = _EMAIL_RE.sub("[EMAIL]", redacted)
    phones = len(_PHONE_RE.findall(redacted))
    redacted = _PHONE_RE.sub("[PHONE]", redacted)
    ibans = len(_IBAN_RE.findall(redacted))
    redacted = _IBAN_RE.sub("[IBAN]", redacted)
    ips = len(_IP_RE.findall(redacted))
    redacted = _IP_RE.sub("[IP]", redacted)

    persons = 0
    orgs = 0
    if use_ner:
        try:
            import spacy

            nlp = spacy.load("en_core_web_lg")
            doc = nlp(redacted)
            spans = sorted(doc.ents, key=lambda e: e.start_char, reverse=True)
            for ent in spans:
                if ent.label_ == "PERSON":
                    redacted = redacted[: ent.start_char] + "[PERSON]" + redacted[ent.end_char :]
                    persons += 1
                elif ent.label_ == "ORG":
                    redacted = redacted[: ent.start_char] + "[ORG]" + redacted[ent.end_char :]
                    orgs += 1
        except (ImportError, OSError):
            # spacy or model missing — fall back to the regex-only sweep.
            pass

    return redacted, RedactionReport(
        emails=emails, phones=phones, ibans=ibans, ips=ips,
        persons=persons, organizations=orgs,
    )
