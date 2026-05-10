from __future__ import annotations

from pathlib import Path
import re

import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = ROOT / "data" / "external_reports" / "pdf"
OUT_PATH = ROOT / "output" / "tables" / "external_pdf_claim_snippets.csv"

KEYWORDS = [
    "equity",
    "ada",
    "accessible",
    "safety",
    "improved",
    "improvement",
    "progress",
    "resolved",
    "closure",
    "compliance",
]


def normalize_spaced_text(text: str) -> str:
    """Collapse spaced-out PDF text like 'A n n u a l' → 'Annual'.

    Many PDFs encode characters with a space between each letter and a double
    space between words.  Detect this pattern and collapse it so keyword
    matching works correctly.
    """
    words = text.split()
    if not words:
        return text
    single_char_ratio = sum(1 for w in words if len(w) == 1) / len(words)
    if single_char_ratio > 0.4:
        # Remove spaces between adjacent alphanumeric characters
        text = re.sub(r"(?<=[A-Za-z0-9]) (?=[A-Za-z0-9])", "", text)
        # Normalise remaining whitespace
        text = re.sub(r"[ \t]+", " ", text)
    return text


def split_sentences(text: str) -> list[str]:
    text = normalize_spaced_text(text)
    candidates = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in candidates if s.strip()]


def main() -> None:
    if not PDF_DIR.exists():
        PDF_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    if not pdf_files:
        print("No PDFs found. Add files under data/external_reports/pdf and rerun.")
        return

    try:
        from pypdf import PdfReader
    except Exception:
        print("pypdf is not installed. Install dependencies with: pip install -r requirements.txt")
        return

    rows: list[dict[str, object]] = []

    for pdf in pdf_files:
        try:
            reader = PdfReader(str(pdf))
        except Exception as exc:
            rows.append(
                {
                    "source_document": pdf.name,
                    "page": None,
                    "snippet": f"FAILED_TO_READ: {exc}",
                    "matched_keyword": None,
                }
            )
            continue

        for idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            for sentence in split_sentences(text):
                lowered = sentence.lower()
                for keyword in KEYWORDS:
                    if keyword in lowered:
                        rows.append(
                            {
                                "source_document": pdf.name,
                                "page": idx,
                                "snippet": sentence[:800],
                                "matched_keyword": keyword,
                            }
                        )
                        break

    df = pd.DataFrame(rows)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)

    print("PDF claim extraction completed.")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
