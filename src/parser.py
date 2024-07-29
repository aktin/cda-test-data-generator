class ValueSetParser:
    def __init__(self, string_to_parse: str):
        self.string_to_parse = string_to_parse

    def parse(self):
        param_list = self.string_to_parse.split(";")
        param_dict = {}
        for param in param_list:
            key, value = param.split("=")
            if key == "range":
                min_value, max_value = value.split("-")
                param_dict["min_value"] = int(min_value) if '.' in min_value else float(min_value)
                param_dict["max_value"] = int(max_value) if '.' in max_value else float(max_value)
            elif key == "value_set":
                value = value[1:-1] # Remove the brackets
                value_set = value.split(",")
                value_set = set([elem.strip() for elem in value_set])
            elif key == "format":
                param_dict["format"] = value
            elif key == "link":
                # Validate the link
                param_dict["link"] = value
            elif key == "regex":
                param_dict["regex"] = value

        return param_dict