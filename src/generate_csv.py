from random import random

import numpy as np
import pandas as pd

from generator import GeneratorFactory
from generator import GeneratorType
from parser import Parser
from value_remover import ValueRemover


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
        variables_dict[row['Concept Id']] = (row['Generation type'], row['Parameters'], row['Nullable'],
            row['Probability missing'])
    return variables_dict


def generate_column_list(generator, num_datasets, nullable, probability_missing=0.5):
    """
    Generate a list of data for a column, with optional handling for missing values.

    Args:
        generator (generator): A generator object that produces data values.
        num_datasets (int): The number of data values to generate.
        nullable (bool): A value indicating if values can be missing.
        probability_missing (float, optional): The probability of a value being missing. Defaults to 0.5.

    Returns:
        list: A list of generated data values, with some values possibly being empty strings if null_flavors is specified.
    """
    if nullable:
        return [next(generator) if np.random.rand() > probability_missing else "" for _ in range(num_datasets)]
    else:
        return [next(generator) for _ in range(num_datasets)]


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
            var_type,
            Parser.parse(params) if isinstance(params, str) else {},
            nullable,
            prob_missing
        )
        for concept_id, (var_type, params, nullable, prob_missing) in variables_dict.items()
    }
    return variables_dict


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


def generate_data_columns(variables_dict, num_datasets):

    output_data = pd.DataFrame()

    for concept_id, (var_type, params, _, _) in variables_dict.items():
        # Generate data column
        column_list = GeneratorFactory.create_generator(GeneratorType(var_type), params).generate(num_datasets)
        # Remove entries if possible
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

    # Dictionary has form { conceptId -> (Default values, Type, Parameters, Nullable) }
    variables_dict = extract_concept_id_attributes(excel_input)

    # Parse parameters inside dictionary (Parameters now in dictionary format)
    variables_dict = parse_parameters_to_dict(variables_dict)

    # Generate data columns
    output_data = generate_data_columns(variables_dict, num_datasets)

    # Remove value with probability
    output_data = ValueRemover.remove_values_with_probability(output_data, variables_dict)

    # Output to CSV
    output_data.to_csv(csv_path, index=False)
