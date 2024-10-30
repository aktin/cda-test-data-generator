import os
from datetime import datetime

from config import config


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
            "range": RangeHandler,
            "value_set": ValueSetHandler,
            "date_format": DefaultHandler,
            "link": LinkHandler,
            "regex": DefaultHandler,
            "start_date": DateHandler,
            "end_date": DateHandler,
            "column": DefaultHandler,
        }
        return handlers.get(key, ErrorHandler)(key)


class AbstractHandler:
    # TODO Docstring
    def __init__(self, key):
        self.key = key

    def handle(self, param_dict, value):
        """
        Handle the parameter by updating the parameter dictionary.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to parse.

        Returns:
            None
        """
        raise NotImplementedError


class DefaultHandler(AbstractHandler):
    def handle(self, param_dict, value):
        """
        Handle the default case by updating the parameter dictionary with the value.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to set as the default.

        Returns:
            None
        """
        param_dict[self.key] = value


class RangeHandler(AbstractHandler):
    def handle(self, param_dict, value):
        """
        Handle the 'range' parameter by parsing the value and updating the parameter dictionary.

        Args:
            param_dict (dict): The dictionary to update with the parsed values.
            value (str): The value to parse, expected to be in the format 'min_value-max_value'.

        Returns:
            None
        """
        min_value, max_value = value.split("-")
        param_dict["min_value"] = int(min_value) if '.' not in min_value else float(min_value)
        param_dict["max_value"] = int(max_value) if '.' not in max_value else float(max_value)


class ValueSetHandler(AbstractHandler):
    def handle(self, param_dict, value):
        """
        Handle the 'value_set' parameter by parsing the value, converting it to a set, and updating the parameter dictionary.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to parse, expected to be in the format '[elem1,elem2,...]'.

        Returns:
            None
        """
        value = value[1:-1]  # Remove brackets
        value_set = value.split(",")
        param_dict["value_set"] = set([elem.strip() for elem in value_set])


class LinkHandler(AbstractHandler):
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
        full_path = os.path.join(os.path.dirname(config.xlsx), value)
        if os.path.isfile(full_path):
            param_dict["link"] = full_path
        else:
            raise ValueError(f"File {value} does not exist in resources/value_sets")


class DateHandler(AbstractHandler):
    def handle(self, param_dict, value):
        """
        Handle the 'start_date' parameter by parsing the value into a datetime object and updating the parameter dictionary.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to parse, expected to be in the format 'YYYYMMDD'.

        Returns:
            None
        """
        param_dict[self.key] = datetime.strptime(value, "%Y%m%d")


class ErrorHandler(AbstractHandler):
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
