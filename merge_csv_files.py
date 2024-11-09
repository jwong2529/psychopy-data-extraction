from glob import glob
import os
import re
import pandas as pd
import sys
from datetime import datetime
import numpy as np

def concat_export_data_files(input_dir, output_dir, output_file='all_data.csv',
                     input_separator=',', output_separator=','):
    dir_not_found_message = 'The {} folder "{}" could not be found. The current directory is {}'
    if not os.path.exists(input_dir):
        raise OSError(dir_not_found_message.format('input', input_dir, os.getcwd()))
    if not os.path.exists(output_dir):
        raise OSError(dir_not_found_message.format('output', output_dir, os.getcwd()))

    output_path = os.path.join(output_dir, output_file)
    if os.path.exists(output_path):
        overwrite = input('The output_file already exists. Overwrite? [y/n]').strip().lower()
        if overwrite != 'y':
            sys.exit(0)

    # Gather all CSV files and sort them by date (oldest -> recent)
    csv_files = glob(os.path.join(input_dir, "*.csv"))

    # Extract dates and sort files
    csv_files.sort(key=lambda f: datetime.strptime(os.path.basename(f).split('_')[2], '%Y-%m-%d'))

    dfs = []  # List to hold DataFrames
    for f in csv_files:
        df = pd.read_csv(f, sep=input_separator)
        dfs.append(df)

    all_data = pd.concat(dfs, ignore_index=True)
    all_data.to_csv(output_path, sep=output_separator, index=False)

    print('Files combined to: "{}"'.format(output_path))

def concat_data_files(input_dir):
    dataframes = []

    for filename in os.listdir(input_dir):
        if filename.endswith('.csv'):
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
            if date_match:
                file_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                file_path = os.path.join(input_dir, filename)
                df = pd.read_csv(file_path)
                dataframes.append((file_date, df))

    # sort by date in descending order (most recent date first)
    dataframes.sort(key=lambda x: x[0], reverse=True)
    # concatenate all dataframes in the list
    concat_df = pd.concat([df for _, df in dataframes], ignore_index=True)

    concat_df_clean = concat_df[concat_df['Participant'].notna() & (concat_df['Participant'] != "Unknown")]

    return concat_df_clean

def merge_data_demographics(data_df, demographics_df, output_dir, output_file='all_data.csv', output_separator=','):
    # use 'participant' as key to combine both dataframes, make sure they are same datatype
    data_df['Participant'] = data_df['Participant'].astype(int)
    demographics_df['Participant'] = demographics_df['Participant'].astype(int)

    final_df = pd.merge(data_df, demographics_df, how='left', on="Participant")

    # columns where each row has different information
    columns_to_keep = [
        "ReactionTime", "CategoryClicked", "ImageName", "AudioName",
        "CongruenceType", "CueType", "CorrectResult"
    ]
    final_df = truncate_columns(final_df, columns_to_keep)

    # we had two date columns so keeping the time and date participant completed survey
    final_df['Date'] = final_df['Date (PDT)']
    final_df = final_df.drop(columns=['Date (PDT)'])

    output_path = os.path.join(output_dir, output_file)
    if os.path.exists(output_path):
        overwrite = input('The output_file already exists. Overwrite? [y/n]').strip().lower()
        if overwrite != 'y':
            sys.exit(0)

    final_df.to_csv(output_path, sep=output_separator, index=False)
    print('Files combined to: "{}"'.format(output_path))

def truncate_columns(df, columns_to_keep):
    # set all values in these columns to NaN (or None) except the first row since it's just repeated cells
    retain_rows = [0] + list(range(120, len(df), 120))

    for index, row in df.iterrows():
        if index not in retain_rows:
            for column in df.columns:
                if column not in columns_to_keep:
                    df.at[index, column] = np.nan

    return df

