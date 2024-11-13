import pandas as pd

from generator import GeneratorFactory
from generator import GeneratorType
from parser import ConfigParser
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
            ConfigParser.parse(params) if isinstance(params, str) else {},
            nullable,
            prob_missing
        )
        for concept_id, (var_type, params, nullable, prob_missing) in variables_dict.items()
    }
    return variables_dict


def generate_data_columns(variables_dict: dict, num_datasets: int) -> pd.DataFrame:
    output_data = pd.DataFrame()

    for concept_id, (var_type, params, _, _) in variables_dict.items():
        if var_type == 'empty':
            continue

        # Generate data column
        column_list = GeneratorFactory.create_generator(GeneratorType(var_type), params).generate(num_datasets)

        if 'dependent_concept_id_1' in params:
            new_df = pd.DataFrame.from_records(column_list, columns=[concept_id, params['dependent_concept_id_1']])
            if new_df.columns.intersection(output_data.columns).any():
                output_data.update(new_df)
            else:
                output_data = pd.concat([output_data, new_df], axis=1)
        else:
            output_data[concept_id] = pd.Series(column_list)

    return output_data


def generate_csv(excel_path: str, csv_path: str, num_datasets: int) -> None:
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
