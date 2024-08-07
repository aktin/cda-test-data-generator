import pandas as pd

from generator import GeneratorFactory
from generator import GeneratorType


def convert_row_to_column_names(excel_input: pd.DataFrame) -> pd.DataFrame:
    output_data = excel_input['Concept Id'].to_frame().transpose()
    output_data.columns = output_data.iloc[0]
    output_data = output_data[1:]
    output_data = output_data.reset_index(drop=True)
    return output_data


def extract_vars_with_params(excel_input):
    variables_dict = {}
    for _, row in excel_input.iterrows():
        variables_dict[row['Concept Id']] = (
            row['Default values'], row['Generation type'], row['Parameters'])
    return variables_dict


def generate_csv(excel_path: str, csv_path, num_datasets=1) -> None:
    """
    Generates a CSV file from an Excel file
    :param csv_path:
    :param excel_path:
    :param num_datasets:
    """
    # Input from Excel
    excel_input = pd.read_excel(excel_path)

    # Convert first row to column names
    output_data = convert_row_to_column_names(excel_input)

    # Dictionary has form { conceptId -> (Default values, Type, Parameters) }
    variables_dict = extract_vars_with_params(excel_input)

    # Valid generation types. Test purposes only
    types = ["date", "int", "float", "UUID", "String"]

    # Loop through all variables and generate data
    for concept_id, (default_values, var_type, params) in variables_dict.items():
        if var_type in types:
            if concept_id == 'given_patient':
                x = 1
            # Generate data
            generator = GeneratorFactory.create_generator(GeneratorType(var_type), value_set=params).generate()
            column_list = [next(generator) for _ in range(num_datasets)]

        else:
            # Fill in default values
            column_list = [default_values for _ in range(num_datasets)]

        output_data[concept_id] = pd.Series(data=column_list)

    # Output to CSV
    output_data.to_csv(csv_path, index=False)

