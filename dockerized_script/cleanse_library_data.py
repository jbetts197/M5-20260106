#!/usr/bin/env python3
"""
Library Data Cleansing Script
"""
import pandas as pd
import re
from datetime import datetime
import os
import argparse
from openai import OpenAI

from sqlalchemy import create_engine

def calculate_date_difference(date1, date2):
    """
    Calculates the difference in days between two dates
    """
    try:
        dateformat = "%d/%m/%Y"
        if isinstance(date1, str):
            date1 = datetime.strptime(date1, dateformat)
        if isinstance(date2, str):
            date2 = datetime.strptime(date2, dateformat)
        return (date2 - date1).days
    except Exception as e:
        print(e)
        return False

def enrich_library_books_data(df_to_enrich, ai_api_key):
    """
    Enriches the library books data with days borrowed column
    """
    try:
        df_to_enrich = df_to_enrich.copy()
        df_to_enrich.loc[:, 'days_borrowed'] = df_to_enrich.apply(
            lambda row: calculate_date_difference(
                row['Book checkout'],
                row['Book Returned']
            ),
            axis=1
        )
        print("Enriching book description...")
        df_to_enrich.loc[:, "book_description"] = (
            df_to_enrich["Books"].apply(
                lambda book: generate_book_description(book, ai_api_key)
            )
        )
        print("Finished enriching book description")
        return df_to_enrich
    except (ValueError, TypeError):
        return False

def is_valid_date(date_str):
    """
    Checks if a date string is valid
    """
    try:
        datetime.strptime(str(date_str), '%d/%m/%Y')
        return True
    except (ValueError, TypeError):
        return False

def normalize_llm_output(text: str) -> str:
    """
    Cleanse string
    """
    THINKING_PATTERN = re.compile(r"<think>.*?</think>", re.DOTALL)
    text = THINKING_PATTERN.sub("", text)
    return text.strip()

def generate_book_description(book_name, api_key):
    """
    Function which calls AI model to generate description from book name
    """
    try:
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=api_key,
        )
        completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1",
            messages=[
                {"role": "system", "content": "Answer concisely. Please don't provide a sentence over 60 words."},
                {"role": "user", "content": f"Provide a description for the book {book_name}."}
            ],
            temperature=0.3,
            max_tokens=60,
        )
        cleaned_result = normalize_llm_output(completion.choices[0].message.content)
        return cleaned_result
    except Exception as e:
        print(e)

def save_df_to_sqlite(df: pd.DataFrame, db_path: str, table_name: str):
    """
    Persist a dataframe to a SQLite database.
    """
    try:
        engine = create_engine(f"sqlite:///{db_path}")
        df.to_sql(table_name, engine, if_exists="replace", index=False)
        print(f"Saved {len(df)} rows to SQLite table '{table_name}' at {db_path}")
    except Exception as e:
        print(f"Failed to save table '{table_name}' to SQLite: {e}")

def cleanse_library_customers_data(input_file_path, output_file_path, db_path=None):
    """
    Main function which cleanses library customers data
    """
    try:
        input_df = pd.read_csv(input_file_path)
        print("Step 1: Removing empty and duplicated rows")
        result_df = input_df.dropna(how='all').drop_duplicates()
        print("Step 2: Standardise text space in customer name")
        result_df['Customer Name'] = result_df['Customer Name'].astype(str).str.strip()
        result_df.to_csv(output_file_path, index=False)

        if db_path:
            save_df_to_sqlite(result_df, db_path, "customers")

        return result_df
    except Exception as e:
        print(e)
        return None

def cleanse_library_books_data(input_file_path, output_file_path, ai_api_key, db_path=None):
    """
    Main function which cleanses library books data
    """
    try:
        input_df = pd.read_csv(input_file_path)
        print("Step 1 & 2: Removing empty and duplicated rows")
        result_df = input_df.dropna(how='all').drop_duplicates()
        print("Step 3: Handle NaN Values")
        result_df['valid_record'] = result_df['Customer ID'].notna()
        print("Step 4: Handle invalid date records")
        result_df['Book checkout'] = result_df['Book checkout'].astype(str).str.replace('"', '')
        result_df['Book Returned'] = result_df['Book Returned'].astype(str).str.replace('"', '')

        checkout_date_valid = result_df['Book checkout'].apply(is_valid_date)
        return_date_valid = result_df['Book Returned'].apply(is_valid_date)
        result_df['valid_record'] = result_df['valid_record'] & checkout_date_valid & return_date_valid

        print("Step 5: Standardise text space in book title")
        result_df['Books'] = result_df['Books'].astype(str).str.strip()

        print("Exporting valid records to CSV")
        valid_data = result_df[result_df['valid_record'] == True].copy()
        valid_data = valid_data.drop(columns=['valid_record'])
        valid_data = enrich_library_books_data(valid_data, ai_api_key)
        valid_data.to_csv(output_file_path, index=False)

        if db_path:
            save_df_to_sqlite(valid_data, db_path, "books")

        return valid_data
    except Exception as e:
        print(e)
        return None

def main():
    """
    Main function to run the script
    """
    parser = argparse.ArgumentParser(description="Library data cleansing")

    # Arguments with ENV var fallback
    parser.add_argument("--ai_api_key", default=os.getenv("AI_API_KEY"), help="API key used to call AI")
    parser.add_argument("--customers-input", required=True, help="Path to customers input file")
    parser.add_argument("--customers-output", required=True, help="Path to customers output file")
    parser.add_argument("--books-input", required=True, help="Path to books input file")
    parser.add_argument("--books-output", required=True, help="Path to books output file")
    parser.add_argument("--db-path", default=os.getenv("DB_PATH", "/data/library.db"), help="SQLite DB path")
    args = parser.parse_args()

    if not args.ai_api_key:
        raise SystemExit("Missing AI API key. Provide --ai_api_key or set AI_API_KEY environment variable.")

    print("Starting customers data cleanse")
    cleanse_library_customers_data(args.customers_input, args.customers_output, db_path=args.db_path)

    print("Starting books data cleanse")
    cleanse_library_books_data(args.books_input, args.books_output, args.ai_api_key, db_path=args.db_path)

    print("Data cleansing completed!")

if __name__ == "__main__":
    main()
