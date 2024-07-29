import pandas as pd

import sys
sys.path.append('/src/generators/')
from generators.generator_factory import GeneratorFactory
from generators.generator_types import GeneratorType

def export_to_csv(variable_excel_path: str) -> str:
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
        variables_dict[row['Concept Id']] = (row['Default values'], row['Type'], row['Value Set'])

    # Fill in default values
    for concept_id, (default_values, type, value_set) in variables_dict.items():
        generator = GeneratorFactory
        column_list = [default_values] # Generator 
        output_data[concept_id] = pd.Series(data=column_list)

    # Output
    output_filename = 'res/data.csv'
    output_data.to_csv(output_filename, index=False)
    return output_filename
