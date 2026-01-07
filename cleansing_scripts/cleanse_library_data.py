#!/usr/bin/env python3
"""
Library Data Cleansing Script
"""
import pandas as pd
import re
from datetime import datetime
import os

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
    
def enrich_library_books_data(df_to_enrich):
    """
    Enriches the library books data with days borrowed column
    """
    try:
        df_to_enrich['days_borrowed'] = df_to_enrich.apply(
            lambda row: calculate_date_difference(
                row['Book checkout'], 
                row['Book Returned']),
                axis=1
            )
        return df_to_enrich
    except(ValueError, TypeError):
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
    
def cleanse_library_customers_data(input_file_path, output_file_path):
    """
    Main function which cleanses library customers data
    """
    try:
        input_df = pd.read_csv(input_file_path)
        print("Step 1: Removing empty and duplicated rows")
        result_df = input_df.dropna(how='all').drop_duplicates()
        print("Step 2: Standardise text space in book title")
        result_df['Customer Name'].str.strip()
        result_df.to_csv(output_file_path, index=False)
    except Exception as e:
        print(e)

def cleanse_library_books_data(input_file_path, output_file_path):
    """
    Main function which clanses library books data
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
        valid_data.drop(columns=['valid_record'])
        valid_data = enrich_library_books_data(valid_data)
        valid_data.to_csv(output_file_path, index=False)
    except Exception as e:
        print(e)

def main():
    """
    Main function to run the script
    """
    customers_input_file = "./raw_data/03_Library SystemCustomers.csv"
    customers_output_file = "./output_cleansed_data/cleansed_system_customers.csv"
    print("Starting books data cleanse")
    cleanse_library_customers_data(customers_input_file, customers_output_file)
    books_input_file = "./raw_data/03_Library Systembook.csv"
    books_output_file = "./output_cleansed_data/cleansed_system_book.csv"
    print("Starting customers data cleanse")
    cleanse_library_books_data(books_input_file, books_output_file)
    print("Data cleansing completed!")

if __name__ == "__main__":
    main()