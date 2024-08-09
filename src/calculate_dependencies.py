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


def apply_generator_to_column(df, column_name, generator):
    df[column_name] = df.apply(lambda x: next(generator), axis=1)


def calculate_dependencies(filename: str) -> None:
    """
    Calculate and update dependent variables in a CSV file.

    Args:
        filename (str): The path to the input CSV file.

    Returns:
        None
    """
    df = pd.read_csv(filename, dtype=str, na_values=[], keep_default_na=False)

    for _, row in df.iterrows():
        calculate_timestamps(row)

    # Read the diagnostic value set
    df_diagnostik = pd.read_csv("../resources/value_sets/diagnostik.csv", delimiter=";", dtype=str)
    # Create a dictionary with the mapping code to id
    diagnostik_dict = dict(zip(df_diagnostik['diagnostik_code'], df_diagnostik['diagnostik_id']))
    # Add for each diagnostic code the corresponding diagnostic id
    df['_diagnostik_id'] = df['diagnostik_code'].map(diagnostik_dict)

    # Read the city value_set
    df_city = pd.read_csv("../resources/value_sets/cities.csv", delimiter=";", dtype=str)
    # Create a dictionary with the mapping code to clinic
    city_dict = dict(zip(df_city['city'], df_city['klinik_name']))
    # Add for each city the corresponding clinic
    df['organisation_name'] = df['city'].map(city_dict)
    city_dict = dict(zip(df_city['city'], df_city['postleitzahl']))
    df['postleitzahl'] = df['city'].map(city_dict)

    # GCS Sum
    df['gcs_summe'] = df['gcs_motorisch'].astype(int) + df['gcs_verbal'].astype(int) + df['gcs_augen'].astype(int)

    # Remove pregnant men
    df.loc[df['gender'] == 'M', 'schwangerschaft'] = 0

    # Add Associated Person if Person has family insurance
    given_name_generator = GeneratorFactory.create_generator(GeneratorType.STRING,
                                                             'link=first_names.csv;column=first_name').generate()
    df['_associatedPerson_given'] = df.apply(lambda x: next(given_name_generator), axis=1)

    family_name_generator = GeneratorFactory.create_generator(GeneratorType.STRING,
                                                              'link=family_names.csv;column=family_name').generate()
    df['_associatedPerson_family'] = df.apply(lambda x: next(family_name_generator), axis=1)

    df.to_csv(filename, index=False)
