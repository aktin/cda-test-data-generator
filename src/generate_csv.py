import numpy as np
import pandas as pd

from generator import GeneratorFactory
from generator import GeneratorType
from parser import Parser


def extract_concept_id_attributes(input_df: pd.DataFrame) -> dict:
    """
    Extract variables with their default values, generation type, and parameters from an Excel input.

    Args:
        input_df (pd.DataFrame): The input DataFrame read from the Excel file.

    Returns:
        dict: A dictionary where the keys are concept IDs and the values are tuples containing
              default values, generation type, and parameters.
    """
    variables_dict = {}
    for _, row in input_df.iterrows():
        variables_dict[row['Concept Id']] = (
            row['Default values'], row['Generation type'], row['Parameters'], row['Nullflavor'])
    return variables_dict


def generate_column_list(generator, num_datasets, null_flavors, probability_missing=0.5):
    """
    Generate a list of data for a column, with optional handling for missing values.

    Args:
        generator (generator): A generator object that produces data values.
        num_datasets (int): The number of data values to generate.
        null_flavors (str or None): A value indicating if null values should be included.
        probability_missing (float, optional): The probability of a value being missing. Defaults to 0.5.

    Returns:
        list: A list of generated data values, with some values possibly being empty strings if null_flavors is specified.
    """
    if pd.isna(null_flavors):
        return [next(generator) for _ in range(num_datasets)]
    else:
        return [next(generator) if np.random.rand() > probability_missing else "" for _ in range(num_datasets)]


def parse_parameters_to_dict(variables_dict: dict) -> dict:
    """
    Parse the parameters in the variables dictionary to a dictionary format.

    Args:
        variables_dict (dict): A dictionary where the keys are concept IDs and the values are tuples containing
                               default values, generation type, parameters, and null flavors.

    Returns:
        dict: A dictionary with the same keys, where the parameters are parsed into a dictionary format if they are strings.
    """
    variables_dict = {
        concept_id: (
            default_values,
            var_type,
            Parser.parse(params) if isinstance(params, str) else {},
            null_flavors
        )
        for concept_id, (default_values, var_type, params, null_flavors) in variables_dict.items()
    }
    return variables_dict


def add_new_variables_to_dict(new_variables, variables_dict):
    """
    Add new variables to the dictionary by expanding variables with a 'number' parameter.

    Args:
        new_variables (dict): A dictionary of new variables to add, where the keys are concept IDs and the values are tuples containing
                              default values, generation type, parameters, and null flavors.
        variables_dict (dict): The original dictionary to update with the new variables.

    Returns:
        None
    """
    for concept_id, (default_values, var_type, params, null_flavors) in new_variables.items():
        # Remove the original variable from the dictionary
        variables_dict.pop(concept_id)
        # How many times should the variable be generated
        num = remove_number_from_params(concept_id, new_variables)

        for i in range(num):
            variables_dict[f"{concept_id}_{i}"] = (default_values, var_type, params, null_flavors)


def remove_number_from_params(concept_id, new_variables):
    """
    Remove the 'number' parameter from the parameters of a given concept ID in the new variables dictionary.

    Args:
        concept_id (str): The concept ID whose parameters are to be updated.
        new_variables (dict): A dictionary of new variables to update, where the keys are concept IDs and the values are tuples containing
                              default values, generation type, parameters, and null flavors.

    Returns:
        int: The value of the 'number' parameter that was removed.
    """
    new_params = new_variables[concept_id][2]
    num = new_params.pop("number")
    new_variables[concept_id] = (
        new_variables[concept_id][0], new_variables[concept_id][1], new_params, new_variables[concept_id][3])
    return num


def generate_data_columns(variables_dict, num_datasets, output_data, probability_missing=0.5):
    """
    Loop through all variables and generate data columns.

    Args:
        variables_dict (dict): A dictionary where the keys are concept IDs and the values are tuples containing
                               default values, generation type, parameters, and null flavors.
        num_datasets (int): The number of data values to generate.
        output_data (pd.DataFrame): The DataFrame to update with the generated data columns.
        probability_missing (float, optional): The probability of a value being missing. Defaults to 0.5.

    Returns:
        pd.DataFrame: The updated DataFrame with the generated data columns.
    """
    for concept_id, (default_values, var_type, params, null_flavors) in variables_dict.items():
        # Generate data column
        generator = GeneratorFactory.create_generator(GeneratorType(var_type), params).generate()
        column_list = generate_column_list(generator, num_datasets, null_flavors, probability_missing)

        new_column = pd.Series(data=column_list, name=concept_id)
        output_data = pd.concat([output_data, new_column], axis=1)

    return output_data


def generate_csv(excel_path: str, csv_path, num_datasets) -> None:
    """
    Generate a CSV file from an Excel input file.

    Args:
        excel_path (str): Path to the input Excel file.
        csv_path (str): Path to the output CSV file.
        num_datasets (int, optional): Number of datasets to generate. Defaults to 1.

    Returns:
        None
    """
    excel_input = pd.read_excel(excel_path)

    # Dictionary has form { conceptId -> (Default values, Type, Parameters, NullFlavors) }
    variables_dict = extract_concept_id_attributes(excel_input)

    # Parse parameters in dictionary
    variables_dict = parse_parameters_to_dict(variables_dict)

    # Extract only the variables that should be generated more than once (they have a number parameter)
    new_variables = dict(filter(lambda x: "number" in x[1][2], variables_dict.items()))

    # Add new variables to the dictionary by expanding variables with a 'number' parameter
    add_new_variables_to_dict(new_variables, variables_dict)

    # Output declaration
    output_data = pd.DataFrame()

    # Generate data columns
    output_data = generate_data_columns(variables_dict, num_datasets, output_data, 0.2)

    # Output to CSV
    output_data.to_csv(csv_path, index=False)
