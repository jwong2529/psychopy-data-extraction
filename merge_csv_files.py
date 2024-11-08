from glob import glob
import os
import pandas as pd
import sys
from datetime import datetime

def concat_csv_files(input_dir, output_dir, output_file='all_data.csv',
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


