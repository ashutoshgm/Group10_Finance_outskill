from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import pandas as pd
from PyPDF2 import PdfReader

from financial_coach.config import CANONICAL_TABLES, INGESTED_DIR
from financial_coach.schemas import SCHEMAS


@dataclass
class IngestionResult:
    tables: Dict[str, pd.DataFrame]
    raw_text: str
    warnings: List[str]


def extract_pdf_text(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def extract_csv_text(file_path: Path) -> str:
    try:
        from langchain.document_loaders.csv_loader import CSVLoader

        loader = CSVLoader(str(file_path))
        docs = loader.load()
        return "\n".join(doc.page_content for doc in docs)
    except ImportError:
        frame = pd.read_csv(file_path)
        return frame.to_csv(index=False)


def extract_source_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf_text(file_path)
    if suffix == ".csv":
        return extract_csv_text(file_path)
    if suffix in {".xlsx", ".xls"}:
        sheets = pd.read_excel(file_path, sheet_name=None)
        return "\n".join(df.to_csv(index=False) for df in sheets.values())
    if suffix == ".json":
        return Path(file_path).read_text(encoding="utf-8")
    return Path(file_path).read_text(encoding="utf-8")


def _coerce_numeric(frame: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    for column in columns:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0.0)
    return frame


def normalize_tables(raw_frames: Dict[str, pd.DataFrame], user_id: str, source_id: str) -> Dict[str, pd.DataFrame]:
    normalized: Dict[str, pd.DataFrame] = {}
    for table_name in CANONICAL_TABLES:
        schema = SCHEMAS[table_name]
        frame = raw_frames.get(table_name, pd.DataFrame(columns=schema.columns)).copy()
        for column in schema.columns:
            if column not in frame.columns:
                frame[column] = None
        frame["user_id"] = user_id
        frame["scope"] = frame["scope"].fillna("private")
        frame["source_id"] = source_id
        frame["confidence"] = pd.to_numeric(frame["confidence"], errors="coerce").fillna(0.9)
        frame = frame[schema.columns]
        normalized[table_name] = frame

    normalized["income"] = _coerce_numeric(normalized["income"], ["gross_monthly", "net_monthly", "confidence"])
    normalized["expenses"] = _coerce_numeric(normalized["expenses"], ["amount", "confidence"])
    normalized["debts"] = _coerce_numeric(normalized["debts"], ["balance", "apr", "minimum_payment", "confidence"])
    normalized["assets"] = _coerce_numeric(normalized["assets"], ["balance", "confidence"])
    return normalized


def ingest_structured_files(file_paths: List[Path], user_id: str) -> IngestionResult:
    raw_tables: Dict[str, pd.DataFrame] = {}
    warnings: List[str] = []
    raw_text_parts: List[str] = []

    for file_path in file_paths:
        raw_text_parts.append(extract_source_text(file_path))
        suffix = file_path.suffix.lower()
        try:
            if suffix == ".csv":
                frame = pd.read_csv(file_path)
                table_name = file_path.stem.lower()
                raw_tables[table_name] = frame
            elif suffix in {".xlsx", ".xls"}:
                workbook = pd.read_excel(file_path, sheet_name=None)
                for sheet_name, frame in workbook.items():
                    raw_tables[sheet_name.lower()] = frame
        except Exception as exc:  # pragma: no cover - defensive parsing
            warnings.append(f"{file_path.name}: {exc}")

    source_id = "-".join(path.stem for path in file_paths) or "manual-upload"
    tables = normalize_tables(raw_tables, user_id=user_id, source_id=source_id)

    for table_name, frame in tables.items():
        output_path = INGESTED_DIR / f"{user_id}_{table_name}.csv"
        frame.to_csv(output_path, index=False)

    return IngestionResult(
        tables=tables,
        raw_text="\n".join(raw_text_parts),
        warnings=warnings,
    )
