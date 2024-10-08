import os
from datetime import datetime


class Parser:
    @staticmethod
    def parse(string_to_parse):
        """
        Parse a semicolon-separated string into a dictionary of parameters.

        Args:
            string_to_parse (str): The string to parse, formatted as 'key1=value1;key2=value2;...'.

        Returns:
            dict: A dictionary containing the parsed parameters.
        """
        param_list = string_to_parse.split(";")
        param_dict = {}
        for param in param_list:
            key, value = param.split("=")
            handler = ParserFactory.get_handler(key)
            handler.handle(param_dict, value)
        return param_dict


class ParserFactory:
    @staticmethod
    def get_handler(key):
        """
        Get the appropriate handler class based on the provided key.

        Args:
            key (str): The key to identify the handler.

        Returns:
            object: An instance of the handler class corresponding to the key.
                    If the key is not found, an instance of DefaultHandler is returned.
        """
        handlers = {
            "scope": ScopeHandler,
            "value_set": ValueSetHandler,
            "date_format": FormatHandler,
            "link": LinkHandler,
            "regex": RegexHandler,
            "start_date": StartDateHandler,
            "end_date": EndDateHandler,
            "column": ColumnHandler,
            "number": NumberHandler
        }
        return handlers.get(key, DefaultHandler)()


class ScopeHandler:
    def handle(self, param_dict, value):
        """
        Handle the 'scope' parameter by parsing the value and updating the parameter dictionary.

        Args:
            param_dict (dict): The dictionary to update with the parsed values.
            value (str): The value to parse, expected to be in the format 'min_value-max_value'.

        Returns:
            None
        """
        min_value, max_value = value.split("-")
        param_dict["min_value"] = int(min_value) if '.' not in min_value else float(min_value)
        param_dict["max_value"] = int(max_value) if '.' not in max_value else float(max_value)

class NumberHandler:
    def handle(self, param_dict, value):
        """
        Handle the 'number' parameter by converting the value to an integer and updating the parameter dictionary.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to convert to an integer.

        Returns:
            None
        """
        param_dict["number"] = int(value)


class ValueSetHandler:
    def handle(self, param_dict, value):
        """
        Handle the 'value_set' parameter by parsing the value, converting it to a set, and updating the parameter dictionary.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to parse, expected to be in the format '[elem1,elem2,...]'.

        Returns:
            None
        """
        value = value[1:-1]  # Remove the brackets
        value_set = value.split(",")
        param_dict["value_set"] = set([elem.strip() for elem in value_set])


class FormatHandler:
    def handle(self, param_dict, value):
        """
        Handle the 'date_format' parameter by updating the parameter dictionary.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to set as the date format.

        Returns:
            None
        """
        param_dict["date_format"] = value


class LinkHandler:
    def handle(self, param_dict, value):
        """
        Handle the 'link' parameter by checking if the specified file exists and updating the parameter dictionary.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to check, expected to be a filename.

        Raises:
            ValueError: If the specified file does not exist.

        Returns:
            None
        """
        if os.path.exists(f'../resources/value_sets/{value}'):
            param_dict["link"] = value
        else:
            raise ValueError(f"File {value} does not exist in resources/value_sets")


class RegexHandler:
    def handle(self, param_dict, value):
        """
        Handle the 'regex' parameter by updating the parameter dictionary.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to set as the regex pattern.

        Returns:
            None
        """
        param_dict["regex"] = value


class StartDateHandler:
    def handle(self, param_dict, value):
        """
        Handle the 'start_date' parameter by parsing the value into a datetime object and updating the parameter dictionary.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to parse, expected to be in the format 'YYYYMMDD'.

        Returns:
            None
        """
        param_dict["start_date"] = datetime.strptime(value, "%Y%m%d")


class EndDateHandler:
    def handle(self, param_dict, value):
        """
        Handle the 'end_date' parameter by parsing the value into a datetime object and updating the parameter dictionary.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to parse, expected to be in the format 'YYYYMMDD'.

        Returns:
            None
        """
        param_dict["end_date"] = datetime.strptime(value, "%Y%m%d")


class ColumnHandler:
    def handle(self, param_dict, value):
        """
        Handle the 'column' parameter by updating the parameter dictionary.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to set as the column.

        Returns:
            None
        """
        param_dict["column"] = value


class DefaultHandler:
    def handle(self, param_dict, value):
        """
        Raise a ValueError indicating that the input string does not match the expected format.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to handle.

        Raises:
            ValueError: Always raised to indicate an invalid input format.

        Returns:
            None
        """
        raise ValueError("Input string does not match the expected format")
