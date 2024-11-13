import os
from datetime import datetime
from typing import Dict, Any

from config import config

class ConfigParserFactory:
    @staticmethod
    def get_handler(key: str) -> object:
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
            "dependent_concept_id_1": DefaultHandler,
            "dependent_column_1": DefaultHandler
        }
        return handlers.get(key, ErrorHandler)(key)

class ConfigParser:
    @staticmethod
    def parse(config_string: str) -> dict:
        """
        Parse a semicolon-separated string into a dictionary of parameters.

        Args:
            config_string (str): The string to parse, formatted as 'key1=value1;key2=value2;...'.

        Returns:
            dict: A dictionary containing the parsed parameters.

        Raises:
            ValueError: If the input string is malformed or contains invalid key-value pairs.
        """
        if not config_string or not isinstance(config_string, str):
            return dict()

        param_dict = dict()
        try:
            param_list = [param.strip() for param in config_string.split(";") if param.strip()]

            for param in param_list:
                if "=" not in param:
                    raise ValueError(f"Invalid parameter format: '{param}'. Expected format: 'key=value'")

                parts = param.split("=", 1)  # Split on first '=' only
                if len(parts) != 2:
                    raise ValueError(f"Invalid parameter format: '{param}'. Expected format: 'key=value'")

                key, value = parts
                key = key.strip()
                value = value.strip()

                if not key or not value:
                    raise ValueError(f"Empty key or value in parameter: '{param}'")

                handler = ConfigParserFactory.get_handler(key)
                handler.handle(param_dict, value)

        except Exception as e:
            raise ValueError(f"Failed to parse config string: {str(e)}")

        return param_dict


class AbstractHandler:
    """
    Abstract base class for handling different types of parameters.

    Attributes:
        key (str): The key associated with the handler.
    """

    def __init__(self, key: str) -> None:
        self.key = key

    def handle(self, param_dict: Dict[str, Any], value: str) -> None:
        raise NotImplementedError


class DefaultHandler(AbstractHandler):
    def handle(self, param_dict: Dict[str, Any], value: str) -> None:
        """
        Handle the default case by updating the parameter dictionary with the value.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to set as the default.

        Raises:
            ValueError: If the value is empty or None.
        """
        if not value:
            raise ValueError(f"Empty value provided for key '{self.key}'")
        param_dict[self.key] = value


class RangeHandler(AbstractHandler):
    def handle(self, param_dict: Dict[str, Any], value: str) -> None:
        """
        Handle the 'range' parameter by parsing the value and updating the parameter dictionary.

        Args:
            param_dict (dict): The dictionary to update with the parsed values.
            value (str): The value to parse, expected to be in the format 'min_value-max_value'.

        Raises:
            ValueError: If the value format is invalid or values are not numeric.
        """
        if not value or "-" not in value:
            raise ValueError(f"Invalid range format: '{value}'. Expected format: 'min_value-max_value'")

        try:
            min_value, max_value = value.split("-", 1)
            min_value = min_value.strip()
            max_value = max_value.strip()

            if not min_value or not max_value:
                raise ValueError(f"Empty value in range: '{value}'")

            # Convert to appropriate numeric type
            min_val = float(min_value) if '.' in min_value else int(min_value)
            max_val = float(max_value) if '.' in max_value else int(max_value)

            if min_val > max_val:
                raise ValueError(f"Min value ({min_val}) is greater than max value ({max_val})")

            param_dict["min_value"] = min_val
            param_dict["max_value"] = max_val

        except ValueError as e:
            raise ValueError(f"Invalid range format: {str(e)}")


class ValueSetHandler(AbstractHandler):
    def handle(self, param_dict: Dict[str, Any], value: str) -> None:
        """
        Handle the 'value_set' parameter by parsing the value and updating the parameter dictionary.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to parse, expected to be in the format '[elem1,elem2,...]'.

        Raises:
            ValueError: If the value format is invalid or missing brackets.
        """
        if not value or len(value) < 2:
            raise ValueError(f"Invalid value set format: '{value}'. Expected format: '[elem1,elem2,...]'")

        if not (value.startswith('[') and value.endswith(']')):
            raise ValueError(f"Value set must be enclosed in square brackets: '{value}'")

        try:
            value = value[1:-1]  # Remove brackets
            if not value.strip():
                raise ValueError("Empty value set")

            value_set = [elem.strip() for elem in value.split(",")]
            if not all(value_set):
                raise ValueError("Value set contains empty elements")

            param_dict["value_set"] = set(value_set)

        except Exception as e:
            raise ValueError(f"Invalid value set format: {str(e)}")


class LinkHandler(AbstractHandler):
    def handle(self, param_dict: Dict[str, Any], value: str) -> None:
        """
        Handle the 'link' parameter by checking if the specified file exists.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to check, expected to be a filename.

        Raises:
            ValueError: If the value is empty or file doesn't exist.
        """
        if not value:
            raise ValueError("Empty file path provided")

        try:
            full_path = os.path.join(os.path.dirname(config.xlsx), value)
            if not os.path.isfile(full_path):
                raise ValueError(f"File '{value}' does not exist in resources/value_sets")
            param_dict["link"] = full_path

        except Exception as e:
            raise ValueError(f"Invalid file link: {str(e)}")


class DateHandler(AbstractHandler):
    def handle(self, param_dict: Dict[str, Any], value: str) -> None:
        """
        Handle date parameters by parsing the value into a datetime object.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to parse, expected to be in the format 'YYYYMMDD'.

        Raises:
            ValueError: If the date format is invalid or the date is invalid.
        """
        if not value or len(value) != 8:
            raise ValueError(f"Invalid date format for '{self.key}'. Expected format: YYYYMMDD, got: '{value}'")

        try:
            date_obj = datetime.strptime(value, "%Y%m%d")
            param_dict[self.key] = date_obj

        except ValueError:
            raise ValueError(f"Invalid date value for '{self.key}'. Expected format: YYYYMMDD, got: '{value}'")


class ErrorHandler(AbstractHandler):
    def handle(self, param_dict: Dict[str, Any], value: str) -> None:
        """
        Handle unknown parameter keys.

        Args:
            param_dict (dict): The dictionary to update with the parsed value.
            value (str): The value to handle.

        Raises:
            ValueError: Always raised with information about the invalid key.
        """
        raise ValueError(f"Unknown parameter key: '{self.key}'")