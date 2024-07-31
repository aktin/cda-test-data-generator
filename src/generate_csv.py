import pandas as pd

from generators.generator_factory import GeneratorFactory
from generators.generator_types import GeneratorType
from parser import Parser


def calculate_order(first_order, second_order):
    variables = {concept: 0 for concept in first_order}
    iterator = 1
    length_vars = len(variables)
    while length_vars != len(variables) or iterator == 1:
        length_vars = len(variables)
        for concept_id, (default_values, type, value_set, constraints) in second_order.items():
            dependencies = Parser.parse_constraints(constraints)
            if "range" in dependencies.keys():
                dependencies.pop("range")
            if "unit" in dependencies.keys():
                dependencies.pop("unit")

            dependency_set = set(dependencies.values())
            variables_set = set(variables.keys())

            if dependency_set.issubset(variables_set) and not variables_set.__contains__(concept_id):
                variables[concept_id] = iterator
                iterator += 1
                # second_order.pop(concept_id)
        if iterator == len(second_order) + 1:
            break
        if length_vars == len(variables):
            raise ValueError("Looping Constraints" + str(length_vars) + " " + str(iterator))

    return variables



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
    first_order = {}
    second_order = {}

    # Fill in default values
    for concept_id, (default_values, type, value_set, constraints) in variables_dict.items():
        if type in types:
            if not isinstance(constraints, str):
                generator = GeneratorFactory.create_generator(GeneratorType(type), value_set=value_set)
                # column_list = [next(generator) for _ in range(10)] # Generator
                column_list = [next(generator)]
                first_order[concept_id] = (default_values, type, value_set, constraints)

            else:
                column_list = [""]
                second_order[concept_id] = (default_values, type, value_set, constraints)
        else:
            column_list = [default_values]
            first_order[concept_id] = (default_values, type, value_set, constraints)

        output_data[concept_id] = pd.Series(data=column_list)

    generation_order = list(calculate_order(first_order,second_order).items())
    generation_order = sorted(generation_order, key=lambda x: x[1])

    for (concept_id, order) in generation_order:
        if order != 0:
            #generate
            pass





    #Output
    output_filename = '../res/data.csv'

    output_data.to_csv(output_filename, index=False)
    return output_filename
