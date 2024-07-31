import pandas as pd

from generators.generator_factory import GeneratorFactory
from generators.generator_types import GeneratorType


def calculate_order(second_order):
    pass


def generate_csv(variable_excel_path: str) -> str:
    '''
    
    '''
    # Input from Excel
    input_variables = pd.read_excel(variable_excel_path)

    # Convert first row to column names
    output_data = input_variables['Concept Id'].to_frame().transpose()
    output_data.columns = output_data.iloc[0]
    output_data = output_data[1:]
    output_data = output_data.reset_index(drop=True)

    # Dictionary has form { conceptId -> (Default values, Type, ValueSet) }
    variables_dict = {}
    for _, row in input_variables.iterrows():
        variables_dict[row['Concept Id']] = (
            row['Default values'], row['Generation type'], row['Parameters'], row['Constraints'])

    # Test
    types = ['date', 'period']
    second_order = {}

    # Fill in default values
    for concept_id, (default_values, type, value_set, constraints) in variables_dict.items():
        if type in types:
            if constraints is None:
                generator = GeneratorFactory.create_generator(GeneratorType(type), value_set=value_set)
                # column_list = [next(generator) for _ in range(10)] # Generator
                column_list = [next(generator)]
            else:
                column_list = [""]
                second_order[concept_id] = (default_values, type, value_set, constraints)
        else:
            column_list = [default_values]
        output_data[concept_id] = pd.Series(data=column_list)

    order = calculate_order(second_order)

    for concept_id, (default_values, type, value_set, constraints) in second_order.items():
        generator = GeneratorFactory.create_generator(GeneratorType(type), value_set=value_set)
        # column_list = [next(generator) for _ in range(10)] # Generator
        column_list = [next(generator)]
        output_data[concept_id] = pd.Series(data=column_list)

    # Output
    output_filename = '../res/data.csv'

    output_data.to_csv(output_filename, index=False)
    return output_filename
