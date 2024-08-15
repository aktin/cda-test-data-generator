import numpy as np
import pandas as pd

from generator import GeneratorFactory
from generator import GeneratorType


def convert_concept_id_to_header(excel_input: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the column "Concept Id" from Excel input to header row of output DataFrame.

    Args:
        excel_input (pd.DataFrame): The input DataFrame read from the Excel file.

    Returns:
        pd.DataFrame: A DataFrame with the first row converted to column names.
    """
    output_data = excel_input['Concept Id'].to_frame().transpose()
    output_data.columns = output_data.iloc[0]
    output_data = output_data[1:]
    output_data = output_data.reset_index(drop=True)
    return output_data


def parse_variable_parameters(excel_input: pd.DataFrame) -> dict:
    """
    Extract variables with their default values, generation type, and parameters from an Excel input.

    Args:
        excel_input (pd.DataFrame): The input DataFrame read from the Excel file.

    Returns:
        dict: A dictionary where the keys are concept IDs and the values are tuples containing
              default values, generation type, and parameters.
    """
    variables_dict = {}
    for _, row in excel_input.iterrows():
        variables_dict[row['Concept Id']] = (
            row['Default values'], row['Generation type'], row['Parameters'], row['NullFlavor'])
    return variables_dict


def generate_csv(excel_path: str, csv_path, num_datasets=1) -> None:
    """
    Generate a CSV file from an Excel input file.

    Args:
        excel_path (str): Path to the input Excel file.
        csv_path (str): Path to the output CSV file.
        num_datasets (int, optional): Number of datasets to generate. Defaults to 1.

    Returns:
        None
    """
    # Input from Excel
    excel_input = pd.read_excel(excel_path)

    # Convert first row to column names
    output_data = convert_concept_id_to_header(excel_input)

    # Dictionary has form { conceptId -> (Default values, Type, Parameters) }
    variables_dict = parse_variable_parameters(excel_input)

    # Valid generation types. Test purposes only
    types = ["date", "int", "float", "UUID", "String"]

    # Loop through all variables and generate data
    for concept_id, (default_values, var_type, params, null_flavors) in variables_dict.items():
        if var_type in types:
            # Generate data column
            generator = GeneratorFactory.create_generator(GeneratorType(var_type), value_set=params).generate()
            if null_flavors is np.nan:
                column_list = [next(generator) for _ in range(num_datasets)]
            else:
                column_list = [next(generator) if np.random.rand() > 0.5 else "" for _ in range(num_datasets)]
        else:
            # Fill in default values
            column_list = [default_values for _ in range(num_datasets)]

        output_data[concept_id] = pd.Series(data=column_list)

    # Output to CSV
    output_data.to_csv(csv_path, index=False)
