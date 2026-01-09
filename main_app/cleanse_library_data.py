#!/usr/bin/env python3
"""
Library Data Cleansing Script

- Cleans customer and book CSV data
- Tracks dropped records with reasons
- Enriches valid book records with:
    - days_borrowed (date difference)
    - AI-generated book descriptions (cached to avoid re-calls)
"""

import pandas as pd
import re
import requests
from datetime import datetime
import os
import argparse
import time
import sqlite3
from typing import Dict, Optional

from sqlalchemy import create_engine

# ============================================================
# Utility functions
# ============================================================

def calculate_date_difference(date1, date2):
    """
    Calculates the number of days between two dd/mm/YYYY dates.
    """
    try:
        fmt = "%d/%m/%Y"
        d1 = datetime.strptime(date1, fmt)
        d2 = datetime.strptime(date2, fmt)
        return (d2 - d1).days
    except Exception:
        return None


def is_valid_date(date_str):
    """
    Checks whether a string matches dd/mm/YYYY format.
    """
    try:
        datetime.strptime(str(date_str), "%d/%m/%Y")
        return True
    except (ValueError, TypeError):
        return False


def normalize_llm_output(text: str) -> str:
    """
    Removes internal <think> blocks and trims whitespace.
    """
    THINKING_PATTERN = re.compile(r"<think>.*?</think>", re.DOTALL)
    return THINKING_PATTERN.sub("", text).strip()


# ============================================================
# SQLite helpers
# ============================================================

def save_df_to_sqlite(df: pd.DataFrame, db_path: str, table_name: str):
    """
    Writes a dataframe to a SQLite table.
    """
    engine = create_engine(f"sqlite:///{db_path}")
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"Saved {len(df)} rows to table '{table_name}'")


# ============================================================
# LLM client + caching
# ============================================================

CACHE_TABLE = "book_description_cache"

def ensure_description_cache(db_path: str):
    """
    Ensures a SQLite table exists for caching book descriptions.
    """
    conn = sqlite3.connect(db_path)
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {CACHE_TABLE} (
            book_name TEXT PRIMARY KEY,
            description TEXT,
            updated_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def load_cached_descriptions(db_path: str, titles) -> Dict[str, str]:
    """
    Loads cached descriptions for known book titles.
    """
    if not titles.any():
        return {}

    ensure_description_cache(db_path)
    conn = sqlite3.connect(db_path)

    placeholders = ",".join(["?"] * len(titles))
    rows = conn.execute(
        f"SELECT book_name, description FROM {CACHE_TABLE} WHERE book_name IN ({placeholders})",
        list(titles),
    ).fetchall()

    conn.close()
    return {name: desc for name, desc in rows}


def upsert_cached_descriptions(db_path: str, mapping: Dict[str, str]):
    """
    Inserts or updates cached book descriptions.
    """
    if not mapping:
        return

    ensure_description_cache(db_path)
    conn = sqlite3.connect(db_path)

    now = datetime.utcnow().isoformat()
    conn.executemany(
        f"""
        INSERT INTO {CACHE_TABLE} (book_name, description, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(book_name) DO UPDATE SET
            description=excluded.description,
            updated_at=excluded.updated_at
        """,
        [(k, v, now) for k, v in mapping.items()],
    )

    conn.commit()
    conn.close()

def generate_book_description_local(book_name: str) -> str:
    """
    Calls local Ollama to generate a 1-sentence description.
    Returns a non-empty string, or raises with useful diagnostics.
    """
    base_url = os.getenv("OLLAMA_BASE_URL", "http://ai_model:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")

    # Guard against empty/NaN titles
    if book_name is None:
        raise ValueError("book_name is None")
    book_name = str(book_name).strip()
    if not book_name or book_name.lower() in {"nan", "none"}:
        raise ValueError(f"book_name is empty/invalid: {book_name!r}")

    payload = {
        "model": model,
        "prompt": f'Provide a one-sentence description (max 25 words) for the book titled "{book_name}". Do not include any quote or doublequote characters in output.',
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 80,  # ensures the model is allowed to output tokens
        },
    }

    url = f"{base_url}/api/generate"
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()

    data = r.json()

    # Defensive parsing
    text = (data.get("response") or "").strip()
    if not text:
        # Include the most useful fields for debugging
        raise RuntimeError(
            "Ollama returned an empty response. "
            f"model={model!r}, book_name={book_name!r}, "
            f"done={data.get('done')!r}, done_reason={data.get('done_reason')!r}, "
            f"full_payload_keys={list(data.keys())!r}"
        )

    return text
# ============================================================
# Enrichment logic
# ============================================================

def enrich_library_books_data(
    df: pd.DataFrame,
    ai_api_key: str,
    db_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Adds derived and AI-enriched fields to valid book records.
    """
    enriched = df.copy()

    # ------------------------------------
    # Calculate days between checkout and return dates
    # ------------------------------------
    checkout = pd.to_datetime(enriched["Book checkout"], format="%d/%m/%Y")
    returned = pd.to_datetime(enriched["Book Returned"], format="%d/%m/%Y")
    enriched["days_borrowed"] = (returned - checkout).dt.days

    # ------------------------------------
    # Generate book descriptions (unique titles only)
    # ------------------------------------
    print("Enriching book descriptions...")

    titles = enriched["Books"].astype(str).str.strip()
    unique_titles = titles.unique()

    cached = load_cached_descriptions(db_path, pd.Series(unique_titles)) if db_path else {}
    missing = [t for t in unique_titles if t not in cached]

    generated = {}
    if missing:
        for title in missing:
            try:
                generated[title] = generate_book_description_local(title)
                time.sleep(0.3)  # small pause to avoid free-tier throttling
            except Exception as e:
                print(f"AI failed for '{title}': {e}")
                generated[title] = f"Description unavailable for '{title}'."

        if db_path:
            upsert_cached_descriptions(db_path, generated)

    title_to_desc = {**cached, **generated}
    enriched["book_description"] = titles.map(title_to_desc)

    return enriched


# ============================================================
# Cleansing workflows
# ============================================================

def cleanse_library_customers_data(input_file, output_file, db_path=None):
    """
    Cleans customer data by removing empty and duplicate rows.
    """
    df = pd.read_csv(input_file)
    df = df.dropna(how="all").drop_duplicates()
    df["Customer Name"] = df["Customer Name"].astype(str).str.strip()
    df.to_csv(output_file, index=False)

    if db_path:
        save_df_to_sqlite(df, db_path, "customers")

    return df


def cleanse_library_books_data(
    input_file,
    output_file,
    ai_api_key,
    db_path=None,
    metrics_output_file_path=None
):
    """
    Cleans, enriches, and exports book data with metrics for dropped records.
    """
    input_df = pd.read_csv(input_file)
    drop_events = []

    def log_drops(df, mask, step, reason):
        """
        Records dropped rows with the rule that caused removal.
        """
        dropped = df.loc[mask].copy()
        if dropped.empty:
            return
        dropped.insert(0, "row_index", dropped.index)
        dropped.insert(1, "rule_step", step)
        dropped.insert(2, "drop_reason", reason)
        drop_events.append(dropped)

    # ------------------------------------
    # Remove fully empty rows
    # ------------------------------------
    empty_mask = input_df.isna().all(axis=1)
    log_drops(input_df, empty_mask, "Step 1", "Empty row")
    df = input_df.loc[~empty_mask].copy()

    # ------------------------------------
    # Remove duplicate rows
    # ------------------------------------
    dup_mask = df.duplicated()
    log_drops(df, dup_mask, "Step 2", "Duplicate row")
    df = df.loc[~dup_mask].copy()

    # ------------------------------------
    # Drop rows without customer ID
    # ------------------------------------
    missing_customer = df["Customer ID"].isna()
    log_drops(df, missing_customer, "Step 3", "Missing Customer ID")
    df = df.loc[~missing_customer].copy()

    # ------------------------------------
    # Drop rows with invalid date formats
    # ------------------------------------
    # Clean raw values (remove quotes + whitespace)
    df["Book checkout"] = (
        df["Book checkout"].astype(str)
        .str.replace('"', '', regex=False)
        .str.strip()
    )
    df["Book Returned"] = (
        df["Book Returned"].astype(str)
        .str.replace('"', '', regex=False)
        .str.strip()
    )
    # If the field contains timestamps, keep only the date portion
    df["Book checkout"] = df["Book checkout"].str.split().str[0]
    df["Book Returned"] = df["Book Returned"].str.split().str[0]
    checkout_valid = df["Book checkout"].apply(is_valid_date)
    returned_valid = df["Book Returned"].apply(is_valid_date)
    log_drops(df, ~checkout_valid, "Step 4", "Invalid checkout date")
    log_drops(df, ~returned_valid, "Step 4", "Invalid return date")
    df = df.loc[checkout_valid & returned_valid].copy()

    # ------------------------------------
    # Normalise book titles
    # ------------------------------------
    df["Books"] = df["Books"].astype(str).str.strip()

    # ------------------------------------
    # Enrich valid records
    # ------------------------------------
    enriched = enrich_library_books_data(df, ai_api_key, db_path)
    enriched.to_csv(output_file, index=False)

    if db_path:
        save_df_to_sqlite(enriched, db_path, "books")

    # ------------------------------------
    # Export metrics
    # ------------------------------------
    metrics_df = pd.concat(drop_events, ignore_index=True) if drop_events else pd.DataFrame()
    if metrics_output_file_path:
        metrics_df.to_csv(metrics_output_file_path, index=False)

    if db_path and not metrics_df.empty:
        save_df_to_sqlite(metrics_df, db_path, "books_dropped_records")

    return enriched, metrics_df


# ============================================================
# CLI entrypoint
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Library data cleansing")
    parser.add_argument("--ai_api_key", default=os.getenv("AI_API_KEY"))
    parser.add_argument("--customers-input", required=True)
    parser.add_argument("--customers-output", required=True)
    parser.add_argument("--books-input", required=True)
    parser.add_argument("--books-output", required=True)
    parser.add_argument("--books-metrics-output", required=True)
    parser.add_argument("--db-path", default=os.getenv("DB_PATH", "/data/library.db"))

    args = parser.parse_args()

    if not args.ai_api_key:
        raise SystemExit("AI API key missing")

    cleanse_library_customers_data(
        args.customers_input,
        args.customers_output,
        args.db_path
    )

    cleanse_library_books_data(
        args.books_input,
        args.books_output,
        args.ai_api_key,
        args.db_path,
        args.books_metrics_output
    )

    print("Data cleansing completed")


if __name__ == "__main__":
    main()
