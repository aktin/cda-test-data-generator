import os
import re

import numpy as np
import pandas as pd
import datetime as dt

from generator import GeneratorFactory, GeneratorType


def calculate_timestamps(row: pd.Series) -> None:
    """
    Calculate and update various timestamp dependencies in a row of a DataFrame.

    Args:
        row (pd.Series): A row from a DataFrame containing timestamp and minute offset information.

    Returns:
        None
    """

    def add_minutes_to_timestamp(timestamp, minutes, format_in="%Y%m%d%H%M%S", format_out="%Y%m%d%H%M%S"):
        """
        Add a specified number of minutes to a timestamp and return the new timestamp in the desired format.

        Args:
            timestamp (str): The original timestamp as a string.
            minutes (int): The number of minutes to add to the timestamp.
            format_in (str, optional): The format of the input timestamp. Defaults to "%Y%m%d%H%M%S".
            format_out (str, optional): The format of the output timestamp. Defaults to "%Y%m%d%H%M%S".

        Returns:
            str: The new timestamp after adding the specified minutes, formatted according to format_out.
        """
        return (dt.datetime.strptime(timestamp, format_in) + dt.timedelta(minutes=int(minutes))).strftime(format_out)

    # Define the sequence of operations: (timestamp, start_timestamp, minutes_to_add, format_input, format_output)
    operations = [
        ("therapiebeginn_ts", "aufnahme_ts", "_aufnahme_therapiebeginn"),
        ("arztkontakt_ts", "therapiebeginn_ts", "_therapiebeginn_arztkontakt"),
        ("end_arztkontakt_ts", "arztkontakt_ts", "_arztkontakt_endarztkontakt"),
        ("entlassung_ts", "end_arztkontakt_ts", "_endarztkontakt_entlassung"),
        ("triage_ts_start", "entlassung_ts", "_entlassung_triagestart", "%Y%m%d%H%M%S", "%Y%m%d%H%M"),
        ("triage_ts_end", "triage_ts_start", "_triagestart_triageend", "%Y%m%d%H%M", "%Y%m%d%H%M")
    ]

    # Process each operation
    for output_key, input_key, minutes_key, *formats in operations:
        format_in, format_out = formats if formats else ("%Y%m%d%H%M%S", "%Y%m%d%H%M%S")
        row[output_key] = add_minutes_to_timestamp(row[input_key], row[minutes_key], format_in, format_out)


def read_csv_and_map(df, csv, key_column, value_column, concept_id, key_csv=None, value_csv=None):
    """
    Read a CSV file and map its values to a DataFrame based on specified columns.

    Args:
        df (pd.DataFrame): The DataFrame to update.
        csv (str): The path to the CSV file.
        key_column (str): The column in the DataFrame to use as the key for mapping.
        value_column (str): The column in the DataFrame to use as the value for mapping.
        concept_id (str): The column in the DataFrame to store the mapped values.
        key_csv (str, optional): The column in the CSV file to use as the key. Defaults to key_column.
        value_csv (str, optional): The column in the CSV file to use as the value. Defaults to value_column.

    Returns:
        None
    """
    key_csv = key_csv if key_csv else key_column
    value_csv = value_csv if value_csv else value_column
    df_csv = pd.read_csv(csv, dtype=str, delimiter=';')
    tuples = dict(zip(df_csv[key_csv], df_csv[value_csv]))
    df[concept_id] = df[key_column].apply(lambda x: tuples.get(x) if x in tuples.keys() else "")


def make_associated_person_family_member(df):
    """
    Maps the 'family_patient' column to the '_associatedPerson_family' column in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.

    Returns:
        None
    """
    df['_associatedPerson_family'] = df['family_patient']


def make_pregnant_man_not_pregnant(df):
    """
    Sets the 'schwangerschaft' column to 0 for all rows where the 'gender' column is 'M'.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.

    Returns:
        None
    """
    df.loc[df['gender'] == 'M', 'schwangerschaft'] = 0


def calculate_gcs_sum(df):
    """
    Calculates the sum of 'gcs_motorisch', 'gcs_verbal', and 'gcs_augen' columns and stores it in the 'gcs_summe' column.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.

    Returns:
        None
    """
    df['gcs_summe'] = df['gcs_motorisch'].astype(int) + df['gcs_verbal'].astype(int) + df['gcs_augen'].astype(int)


def calculate_dependencies(filename: str) -> None:
    """
    Calculate and update dependent variables in a CSV file.

    Args:
        filename (str): The path to the input CSV file.

    Returns:
        None
    """
    # Read the CSV file with generated data
    df = pd.read_csv(filename, dtype=str, na_values=[], keep_default_na=False)

    # Calculate timestamps
    for _, row in df.iterrows():
        calculate_timestamps(row)

    # Get environment variables for each csv path
    cities_csv = os.environ['CITIES_CSV']
    diagnose_csv = os.environ['DIAGNOSES_CSV']

    # Define tasks for reading CSV files and mapping values
    tasks = [
        (cities_csv, "city", "klinik_name", "organisation_name"),
        (cities_csv, "city", "postleitzahl", "postleitzahl")
    ]

    # Define tasks for each diagnose
    # Set originalText(diagnose_name) matching to diagnose_code
    diagnose_cols = [col for col in df.columns if re.match(r'diagnose_code_\d+', col)]
    for diagnose in diagnose_cols:
        num = re.match(r'diagnose_code_(\d+)', diagnose).group(1)
        task = (diagnose_csv, diagnose, "diagnose_name_" + num, "diagnose_name_" + num,
                "Schlüsselnummer ohne Strich, Stern und  Ausrufezeichen", "Titel des dreistelligen Kodes")
        tasks.append(task)

    # Do the Tasks
    # Read CSV files and map values to DataFrame
    for task in tasks:
        read_csv_and_map(df, *task)

    # GCS Sum
    calculate_gcs_sum(df)

    # Abort pregnant men
    make_pregnant_man_not_pregnant(df)

    # Associated persons are only family member
    make_associated_person_family_member(df)

    df.to_csv(filename, index=False)
