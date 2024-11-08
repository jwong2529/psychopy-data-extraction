import os
import glob
import pandas as pd
import numpy as np

def remove_unwanted_files(input_dir, ignore_file_path):

    # read files to ignore from ignore_files.txt
    if os.path.exists(ignore_file_path):
        with open(ignore_file_path, 'r') as file:
            ignore_files = set(line.strip() for line in file)
    else:
        ignore_files = set()

    # loop through files in the input_files directory
    for filename in os.listdir(input_dir):
        file_path = os.path.join(input_dir, filename)

        #check if the file should be removed
        if (
                filename in ignore_files or
                filename.endswith('.log.gz') or
                filename.endswith('.log') or
                filename.endswith('.psydat') or
                os.path.getsize(file_path) <= 20 * 1024  # remove files that are 20 KB or smaller
        ):
            try:
                os.remove(file_path)
                print(f"Removed: {filename}")
            except Exception as e:
                print(f"Error removing {filename}: {e}")

    remaining_files = len(os.listdir(input_dir))
    print(f"Number of files in {input_dir}: {remaining_files}")

def clean_csv_file(input_file, preprocessed_dir):
    # a -> animal, v -> vehicle
    stimuli_pairs = {
        'cat': 'a',
        'frog': 'a',
        'dog': 'a',
        'monkey': 'a',
        'elephant': 'a',
        'car': 'v',
        'boat': 'v',
        'train': 'v',
        'bike': 'v',
        'motorcycle': 'v'
    }

    columns_to_keep = ["participant", "date", "expName", "psychopyVersion", "OS",
                       "frameRate", "mouse_2.time", "mouse_2.clicked_name", "imageName",
                       "audioName", "congruenceType"]

    # load the CSV file
    df = pd.read_csv(input_file)

    # get the cueTypes for each block from original csv
    df_filtered = df.dropna(subset=['cueType'])
    first_block_cue_type = df_filtered.iloc[0]['cueType']
    second_block_cue_type = df_filtered.iloc[1]['cueType']

    # filter to keep only specified columns
    df = df[columns_to_keep]
    # rename column headers
    df.rename(columns={'mouse_2.time': 'reactionTime', 'mouse_2.clicked_name': 'categoryClicked'}, inplace=True)

    # trim the category clicked to just 'a' or 'v'
    df['categoryClicked'] = df['categoryClicked'].str[0]

    # get rid of blank cells in columns and shift everything up
    df = df.dropna(how='any').reset_index(drop=True)
    # truncate to 121 rows
    df = df.iloc[:121]

    # set all values in these columns to NaN (or None) except the first row since it's just repeated cells
    columns_to_truncate = ["participant", "date", "expName", "psychopyVersion", "OS", "frameRate"]
    for col in columns_to_truncate:
        df.loc[1:, col] = np.nan

    # first 60 rows for the first block, next 60 rows for the second block
    df['cueType'] = [first_block_cue_type if 0 <= i < 60 else  second_block_cue_type if 60 <= i < 120 else '' for i in range(len(df))]

    # apply the is_correct function to each row and assign the result to 'correct_result'
    df['correct_result'] = df.apply(lambda row: is_correct(row, stimuli_pairs), axis=1)

    # extract the original filename and save the processed file in 'preprocessed_files' with the same name
    output_filename = os.path.basename(input_file)
    output_path = os.path.join(preprocessed_dir, output_filename)
    df.to_csv(output_path, index=False)
    print(f"Processed CSV saved as {output_path}")

def is_correct(row, stimuli_pairs):
    cue_type = row['cueType']
    if cue_type == "visual":
        expected_value = stimuli_pairs.get(row['imageName'], '')
    elif cue_type == "auditory":
        expected_value = stimuli_pairs.get(row['audioName'], '')
    else:
        return 'null'  # default if cueType is invalid

    return '1' if row['categoryClicked'] == expected_value else '0'

def clean_all_files(input_dir, preprocessed_dir):
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))

    for input_file in csv_files:
        print(f"Processing file: {input_file}")
        clean_csv_file(input_file, preprocessed_dir)