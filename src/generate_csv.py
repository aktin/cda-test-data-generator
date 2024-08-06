import pandas as pd

from generators.generator_factory import GeneratorFactory
from generators.generator_types import GeneratorType
from parser import Parser


def generate_csv(excel_path: str, num_datasets=1) -> str:

    # Input from Excel
    excel_input = pd.read_excel(excel_path)

    # Convert first row to column names
    output_data = excel_input['Concept Id'].to_frame().transpose()
    output_data.columns = output_data.iloc[0]
    output_data = output_data[1:]
    output_data = output_data.reset_index(drop=True)

    # Dictionary has form { conceptId -> (Default values, Type, ValueSet) }
    variables_dict = {}
    for _, row in excel_input.iterrows():
        variables_dict[row['Concept Id']] = (
            row['Default values'], row['Generation type'], row['Parameters'])

    # Test
    types = ["date", "int", "float", "UUID", "String"]

    # Fill in default values
    for concept_id, (default_values, type, value_set) in variables_dict.items():
        if type in types:

            if concept_id == "zuweisung":
                x = 1

            generator = GeneratorFactory.create_generator(GeneratorType(type), value_set=value_set, constraints=None)
            column_list = [next(generator) for _ in range(num_datasets)]

        else:
            column_list = [default_values for _ in range(num_datasets)]

        output_data[concept_id] = pd.Series(data=column_list)

    # Output
    output_filename = '../resources/data.csv'

    output_data.to_csv(output_filename, index=False)
    return output_filename
