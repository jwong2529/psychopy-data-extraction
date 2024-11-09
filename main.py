import os
import merge_csv_files
import preprocess_csv_files
import re
from datetime import datetime, timedelta

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


if __name__ == '__main__':
    input_dir = os.path.join('input_files')
    output_dir = os.path.join('output_files')
    preprocessed_dir = os.path.join('preprocessed_files')
    ignore_files_path = 'ignore_files.txt'
    demographics_file = 'demographics.csv'
    output_file = 'data_results.csv'

    # initial clear of preprocessed files
    clear_preprocessed_files(preprocessed_dir)

    # preprocess_csv_files.remove_unwanted_files(input_dir, ignore_files_path)
    preprocess_csv_files.clean_all_data_files(input_dir, preprocessed_dir)

    # merge_csv_files.concat_data_files(preprocessed_dir, output_dir, output_file)

    clean_demo_df = preprocess_csv_files.clean_demographics_file(demographics_file)
    concat_data_df = merge_csv_files.concat_data_files(preprocessed_dir)
    merge_csv_files.merge_data_demographics(concat_data_df, clean_demo_df, output_dir, output_file)