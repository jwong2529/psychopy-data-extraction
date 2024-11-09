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

def clean_data_file(input_file, preprocessed_dir):
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
    capitalized_columns = {col: col[0].upper() + col[1:] for col in columns_to_keep}

    # load the CSV file
    df = pd.read_csv(input_file)

    # get the cueTypes for each block from original csv
    df_filtered = df.dropna(subset=['cueType'])
    first_block_cue_type = df_filtered.iloc[0]['cueType']
    second_block_cue_type = df_filtered.iloc[1]['cueType']

    # filter to keep only specified columns
    df = df[columns_to_keep]
    # rename column headers
    df.rename(columns=capitalized_columns, inplace=True)
    df.rename(columns={'Mouse_2.time': 'ReactionTime', 'Mouse_2.clicked_name': 'CategoryClicked'}, inplace=True)

    # trim the category clicked to just 'a' or 'v'
    df['CategoryClicked'] = df['CategoryClicked'].str[0]

    # get rid of blank cells in columns and shift everything up
    df = df.dropna(how='any').reset_index(drop=True)
    # truncate to 121 rows
    df = df.iloc[:121]

    # first 60 rows for the first block, next 60 rows for the second block
    df['CueType'] = [first_block_cue_type if 0 <= i < 60 else second_block_cue_type if 60 <= i < 120 else '' for i in range(len(df))]

    # apply the is_correct function to each row and assign the result to 'correct_result'
    df['CorrectResult'] = df.apply(lambda row: is_correct(row, stimuli_pairs), axis=1)

    # extract the original filename and save the processed file in 'preprocessed_files' with the same name
    output_filename = os.path.basename(input_file)
    output_path = os.path.join(preprocessed_dir, output_filename)
    df.to_csv(output_path, index=False)
    print(f"Processed CSV saved as {output_path}")

def is_correct(row, stimuli_pairs):
    cue_type = row['CueType']
    if cue_type == "visual":
        expected_value = stimuli_pairs.get(row['ImageName'], '')
    elif cue_type == "auditory":
        expected_value = stimuli_pairs.get(row['AudioName'], '')
    else:
        return 'null'  # default if cueType is invalid

    return '1' if row['CategoryClicked'] == expected_value else '0'

def clean_all_data_files(input_dir, preprocessed_dir):
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))

    for input_file in csv_files:
        print(f"Processing file: {input_file}")
        clean_data_file(input_file, preprocessed_dir)

def clean_demographics_file(input_file):
    # read file without treating any row as header (qualtrics auto-generates file that has 3 column headers
    # so drop first and third row before cleaning
    raw_df = pd.read_csv(input_file, header=None)
    raw_df = raw_df.drop([0, 2])
    raw_df.columns = raw_df.iloc[0] # set column header
    raw_df = raw_df[1:] # remove old header row from data
    # print(raw_df)
    columns_to_keep = ["Participant","End Date",
                       "What is your child's gender? - Selected Choice",
                       "What is your child's race? - Selected Choice",
                       "What is your child's race? - Other or Multiracial - Text",
                       "What is your child's ethnicity?",
                       "Is English your child's primary language?",
                       "Is your child's vision normal or corrected to normal?",
                       "Is your child's hearing normal or corrected to normal?",
                       "Please type your child's date of birth in MM/DD/YYYY format.",
                       "What type of device did your child use?",
                       "Did your child use a mouse, touchscreen, or track pad?",
                       "Did your child experience internet issues?",
                       "Did the experiment ever crash?",
                       "Was your child able to hear sounds?",
                       "Was your child able to see images?",
                       "Did the device die while running the experiment?",
                       "Were there any other technical difficulties?"]
    demographics_df = raw_df[columns_to_keep]
    demographics_df = demographics_df.copy()
    demographics_df.rename(columns={
                        'End Date': 'Date (PDT)',
                        "What is your child's gender? - Selected Choice": 'Gender',
                        "What is your child's race? - Selected Choice": 'Race',
                        "What is your child's race? - Other or Multiracial - Text": 'Race (other or multiracial)',
                        "What is your child's ethnicity?": 'Ethnicity',
                        "Is English your child's primary language": "English primary language",
                        "Is your child's vision normal or corrected to normal?": 'Normal/corrected vision',
                        "Is your child's hearing normal or corrected to normal?": 'Normal/corrected hearing',
                        "Please type your child's date of birth in MM/DD/YYYY format.": 'Birth date',
                        "What type of device did your child use?": 'Device',
                        "Did your child use a mouse, touchscreen, or track pad?": 'Mouse/touchscreen/trackpad',
                        "Did your child experience internet issues?": 'Internet issues',
                        "Did the experiment ever crash?": 'Experiment crashed',
                        "Was your child able to hear sounds?": 'Able to hear sounds',
                        "Was your child able to see images?": 'Able to see images',
                        "Did the device die while running the experiment?": 'Device died',
                        "Were there any other technical difficulties?": 'Technical difficulties'},
                        inplace=True)

    # delete row where there is no participant id
    demographics_df_clean = demographics_df[demographics_df['Participant'].notna() & (demographics_df['Participant'] != "Unknown")]
    return demographics_df_clean
