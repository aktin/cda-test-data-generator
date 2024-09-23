import datetime as dt
import os
import random
import re
from typing import Optional

import pandas as pd


def _add_minutes_to_timestamp(timestamp, minutes, format_in="%Y%m%d%H%M%S", format_out="%Y%m%d%H%M%S"):
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


def calculate_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate and update various timestamp dependencies in a DataFrame.

    Args:
        df (pd.DataFrame): A DataFrame containing timestamp and minute offset information.

    Returns:
        pd.DataFrame: The updated DataFrame with calculated timestamp dependencies.
    """

    # Define the sequence of operations: (timestamp, start_timestamp, minutes_to_add, format_input, format_output)
    operations = [
        ("therapiebeginn_ts", "aufnahme_ts", "_aufnahme_therapiebeginn"),
        ("arztkontakt_ts", "therapiebeginn_ts", "_therapiebeginn_arztkontakt"),
        ("end_arztkontakt_ts", "arztkontakt_ts", "_arztkontakt_endarztkontakt"),
        ("entlassung_ts", "end_arztkontakt_ts", "_endarztkontakt_entlassung"),
        ("triage_ts_start", "entlassung_ts", "_entlassung_triagestart", "%Y%m%d%H%M%S", "%Y%m%d%H%M"),
        ("triage_ts_end", "triage_ts_start", "_triagestart_triageend", "%Y%m%d%H%M", "%Y%m%d%H%M")
    ]

    for output_key, input_key, minutes_key, *formats in operations:
        format_in, format_out = formats if formats else ("%Y%m%d%H%M%S", "%Y%m%d%H%M%S")
        df[output_key] = df.apply(
            lambda row: _add_minutes_to_timestamp(row[input_key], row[minutes_key], format_in, format_out), axis=1)

    return df


def map_csv_to_dataframe(
    df: pd.DataFrame,
    csv_path: str,
    df_key_column: str,
    df_value_column: str,
    df_target_column: str,
    csv_key_column: Optional[str] = None,
    csv_value_column: Optional[str] = None,
    csv_delimiter: Optional[str] = ';'
) -> pd.DataFrame:
    """
    Map values from a CSV file to a DataFrame based on specified columns.

    This function reads a CSV file, creates a mapping between two of its columns,
    and uses this mapping to populate a new column in the input DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame to update.
        csv_path (str): The path to the CSV file containing the mapping data.
        df_key_column (str): The column in the DataFrame to use as the key for mapping.
        df_value_column (str): The column in the DataFrame containing the values to be mapped.
        df_target_column (str): The new column in the DataFrame to store the mapped values.
        csv_key_column (str, optional): The column in the CSV file to use as the key.
                                        If None, defaults to df_key_column.
        csv_value_column (str, optional): The column in the CSV file to use as the value.
                                          If None, defaults to df_value_column.
        csv_delimiter (str, optional): The delimiter used in the CSV file. Defaults to ';'.

    Returns:
        pd.DataFrame: The updated DataFrame with the new mapped column.

    Example:
        df = pd.DataFrame({'ID': ['1', '2', '3'], 'Value': ['A', 'B', 'C']})
        result = map_csv_to_dataframe(
            df,
            'mapping.csv',
            'ID',
            'Value',
            'MappedValue'
        )
    """
    # Use DataFrame column names for CSV if not specified
    csv_key_column = csv_key_column or df_key_column
    csv_value_column = csv_value_column or df_value_column

    # Read the CSV file
    csv_df = pd.read_csv(csv_path, dtype=str, delimiter=csv_delimiter)

    # Create a mapping dictionary from the CSV data
    mapping = dict(zip(csv_df[csv_key_column], csv_df[csv_value_column]))

    # Apply the mapping to create the new column
    df[df_target_column] = df[df_key_column].map(mapping).fillna('')

    return df


def make_associated_person_family_member(df):
    """
    Maps the 'family_patient' column to the '_associatedPerson_family' column in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.

    Returns:
        None
    """
    df['_associatedPerson_nachname'] = df['nachname_patient']


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


def define_tasks_for_diagnoses(df, tasks):
    """
    Define tasks for each diagnose column in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        tasks (list): The list to which the tasks will be appended.

    Returns:
        None
    """
    diagnose_csv = os.environ['DIAGNOSES_CSV']

    # Identify all diagnose columns in the DataFrame
    diagnose_cols = [col for col in df.columns if re.match(r'diagnose_code_\d+', col)]

    for diagnose in diagnose_cols:
        # Extract the number from the column name
        num = re.match(r'diagnose_code_(\d+)', diagnose).group(1)

        task = {
            'csv_path': diagnose_csv,
            'df_key_column': diagnose,
            'df_value_column': "diagnose_name_" + num,
            'df_target_column': "diagnose_name_" + num,
            'csv_key_column': "Schlüsselnummer ohne Strich, Stern und  Ausrufezeichen",
            'csv_value_column': "Titel des dreistelligen Kodes"
        }

        # Append the task to the tasks list
        tasks.append(task)


def add_insurace_information(df):
    df['versicherung_txt'] = df['versicherungsfall'].apply(lambda x: 'Selbstzahler' if x == 'SELF' else 'Familienversicherung')


def add_allergie_information(df):
    df['allergie_txt'] = df['allergie'].apply(lambda x: f"")


def assign_names_to_patients(individual_attributes_csv, df):
    csv_df = pd.read_csv(individual_attributes_csv, dtype=str, delimiter=';')
    df['vorname_patient'] = df['gender'].apply(lambda x:
        random.choice(csv_df['vorname_m']) if x == 'M' else random.choice(csv_df['vorname_f']))


def calculate_dependencies(filename: str) -> None:
    """
    Calculate and update dependent variables in a CSV file.

    Args:
        filename (str): The path to the input CSV file.

    Returns:
        None
    """
    df = pd.read_csv(filename, dtype=str, na_values=[], keep_default_na=False)

    calculate_timestamps(df)

    clinics_csv = os.environ['CLINICS_CSV']
    cedis_csv = os.environ['CEDIS_CSV']
    individual_attributes_csv = os.environ['INDIVIDUAL_ATTRIBUTES_CSV']

    tasks = [
        {
            'csv_path': clinics_csv,
            'df_key_column': 'stadt',
            'df_value_column': 'klinik_name',
            'df_target_column': 'organisation_name',
        },
        {
            'csv_path': clinics_csv,
            'df_key_column': 'stadt',
            'df_value_column': 'postleitzahl',
            'df_target_column': 'postleitzahl',
        },
        {
            'csv_path': cedis_csv,
            'df_key_column': 'cedis',
            'df_value_column': 'display_name',
            'df_target_column': 'beschwerden_txt',
        }
    ]

    define_tasks_for_diagnoses(df, tasks)

    for task in tasks:
        map_csv_to_dataframe(df, **task)

    calculate_gcs_sum(df)

    make_pregnant_man_not_pregnant(df)

    make_associated_person_family_member(df)

    add_insurace_information(df)

    add_allergie_information(df)

    assign_names_to_patients(individual_attributes_csv, df)

    df.to_csv(filename, index=False)
