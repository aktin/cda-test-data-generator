import datetime
import re


class Parser:
    @staticmethod
    def parse(string_to_parse):
        param_list = string_to_parse.split(";")
        param_dict = {}
        for param in param_list:
            key, value = param.split("=")
            if key == "scope":
                min_value, max_value = value.split("-")
                param_dict["min_value"] = int(min_value) if '.' not in min_value else float(min_value)
                param_dict["max_value"] = int(max_value) if '.' not in max_value else float(max_value)
            elif key == "value_set":
                value = value[1:-1]  # Remove the brackets
                value_set = value.split(",")
                param_dict["value_set"] = set([elem.strip() for elem in value_set])
            elif key == "format":
                param_dict["format"] = value
            elif key == "link":
                # TODO: Validate the link 
                param_dict["link"] = value
            elif key == "regex":
                param_dict["regex"] = value
            elif key == "start_date":
                param_dict["start_date"] = datetime.datetime.strptime(value, "%Y%m%d")
            elif key == "end_date":
                param_dict["end_date"] = datetime.datetime.strptime(value, "%Y%m%d")
            else:
                raise ValueError("Input string does not match the expected format")

        return param_dict

    @staticmethod
    def parse_constraints(string_to_parse):
        string_to_parse = str(string_to_parse)
        param_list = string_to_parse.split(";")
        param_dict = {}
        for param in param_list:
            key, value = param.split("=")
            if key == "min":
                param_dict["min"] = value
            elif key == "range":
                pattern = r'(\d+\.?\d*)([a-zA-Z]+)'

                # Use re.match to apply the pattern to the input string
                match = re.match(pattern, value)

                if match:
                    # Extract the value and unit from the match groups
                    param_dict["range"] = int(match.group(1))  # Convert the numeric part to a float
                    param_dict["unit"] = match.group(2)  # Extract the unit part as a string
                else:
                    raise ValueError("Input string does not match the expected format")
            elif key == "interval":
                value = value[1:-1]  # Remove the brackets
                min_value, max_value = value.split(",")
                param_dict["min"] = min_value
                param_dict["max"] = max_value

        return param_dict
