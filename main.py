import os
import merge_csv_files
import preprocess_csv_files
import re
from datetime import datetime

def clear_preprocessed_files(preprocessed_dir):
    if os.path.exists(preprocessed_dir):
        for filename in os.listdir(preprocessed_dir):
            file_path = os.path.join(preprocessed_dir, filename)
            try:
                # check if it's a file (not a subdirectory) and delete it
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(f"Error removing file {file_path}: {e}")
    else:
        print(f"The directory {preprocessed_dir} does not exist.")


def print_sorted_dates_from_csvs(input_dir):
    # List to store tuples of (filename, formatted_date)
    files_with_dates = []

    # Loop through all files in the input directory
    for filename in os.listdir(input_dir):
        # Check if the file is a CSV
        if filename.endswith('.csv'):
            file_path = os.path.join(input_dir, filename)

            # Use regex to match the date and time in the filename
            match = re.search(r'(\d{4}-\d{2}-\d{2})_(\d{2})h(\d{2})\.(\d{2})\.(\d{3})', filename)

            if match:
                # Extract date and time components
                date_str = match.group(1)  # YYYY-MM-DD
                hour = match.group(2)  # Hour
                minute = match.group(3)  # Minute
                second = match.group(4)  # Second
                millisecond = match.group(5)  # Millisecond (not needed for this format)

                # Create a cleaned date-time string and convert to datetime object
                cleaned_time_str = f"{date_str}_{hour}:{minute}:{second}"  # Format to YYYY-MM-DD_HH:MM:SS
                date_obj = datetime.strptime(cleaned_time_str, '%Y-%m-%d_%H:%M:%S')

                # Format the date as MM-DD-YYYY_hh:mmAM/PM
                formatted_date = date_obj.strftime('%m-%d-%Y_%I:%M%p')

                # Store the filename and formatted date as a tuple
                files_with_dates.append((filename, formatted_date, date_obj))
            else:
                print(f"Invalid date-time format in {filename}")

    # Sort the files by the datetime object in descending order (most recent first)
    files_with_dates.sort(key=lambda x: x[2], reverse=True)

    # Print the sorted filenames and their formatted dates
    for filename, formatted_date, _ in files_with_dates:
        print(f"{filename}: {formatted_date}")

if __name__ == '__main__':
    input_dir = os.path.join('input_files')
    output_dir = os.path.join('output_files')
    preprocessed_dir = os.path.join('preprocessed_files')
    ignore_files_path = 'ignore_files.txt'
    demographics_file = 'Animal or Vehicle Demographics Survey_November 6, 2024_21.43.csv'
    output_file = 'data_results.csv'

    # initial clear of preprocessed files
    # clear_preprocessed_files(preprocessed_dir)

    # preprocess_csv_files.remove_unwanted_files(input_dir, ignore_files_path)
    # preprocess_csv_files.clean_all_files(input_dir, preprocessed_dir)

    print_sorted_dates_from_csvs(preprocessed_dir)
    # merge_csv_files.concat_csv_files(preprocessed_dir, output_dir, output_file)