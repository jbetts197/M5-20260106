#!/usr/bin/env python3
"""
Library Data Cleansing Script
"""
import pandas as pd
import re
from datetime import datetime
import os

def is_valid_date(date_str):
    """
    Checks if a date string is valid
    """
    try:
        datetime.strptime(str(date_str), '%d/%m/%Y')
        return True
    except (ValueError, TypeError):
        return False
    
def cleanse_library_data(input_file_path, output_file_path):
    """
    Main function which clanses library data
    """
    try:
        input_df = pd.read_csv(input_file_path)
        print("Step 1 & 2: Removing empty and duplicated rows")
        result_df = input_df.dropna(how='all').drop_duplicates()
        print("Step 3: Handle NaN Values")
        result_df['valid_record'] = result_df['Customer ID'].notna()
        print("Step 4: Handle invalide date records")
        result_df['Book checkout'] = result_df['Book checkout'].str.replace('"', '')
        result_df['Book Returned'] = result_df['Book Returned'].str.replace('"', '')
        date_pattern = r'^\d{2}/\d{2}/\d{4}$'
        checkout_date_valid = result_df['Book checkout'].apply(is_valid_date)
        return_date_valid = result_df['Book Returned'].apply(is_valid_date)
        result_df['valid_record'] = result_df['valid_record'] & checkout_date_valid & return_date_valid
        print("Step 5: Standardise text space in book title")
        result_df['Books'] = result_df['Books'].str.strip()
        print("Exporting to valid records to CSV")
        valid_data = result_df[result_df['valid_record'] == True]
        valid_data.drop(columns=['valid_record']).to_csv("../output_cleansed_data/cleansed_system_book.csv", index=False)
    except Exception as e:
        print(e)

def main():
    """
    Main function to run the script
    """
    input_file = "./raw_data/03_Library Systembook.csv"
    output_file = "./output_cleansed_data/cleansed_system_book.csv"
    cleanse_library_data(input_file, output_file)
    print("Starting data cleanse activity...")
    print("Data cleansing completed!")

if __name__ == "__main__":
    main()