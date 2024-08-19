import os
from datetime import datetime


class Parser:
    @staticmethod
    def parse(string_to_parse):
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
        handlers = {
            "scope": ScopeHandler,
            "value_set": ValueSetHandler,
            "format": FormatHandler,
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
        min_value, max_value = value.split("-")
        param_dict["min_value"] = int(min_value) if '.' not in min_value else float(min_value)
        param_dict["max_value"] = int(max_value) if '.' not in max_value else float(max_value)

class NumberHandler:
    def handle(self, param_dict, value):
        param_dict["number"] = int(value)


class ValueSetHandler:
    def handle(self, param_dict, value):
        value = value[1:-1]  # Remove the brackets
        value_set = value.split(",")
        param_dict["value_set"] = set([elem.strip() for elem in value_set])


class FormatHandler:
    def handle(self, param_dict, value):
        param_dict["format"] = value


class LinkHandler:
    def handle(self, param_dict, value):
        if os.path.exists(f'../resources/value_sets/{value}'):
            param_dict["link"] = value
        else:
            raise ValueError(f"File {value} does not exist in resources/value_sets")


class RegexHandler:
    def handle(self, param_dict, value):
        param_dict["regex"] = value


class StartDateHandler:
    def handle(self, param_dict, value):
        param_dict["start_date"] = datetime.strptime(value, "%Y%m%d")


class EndDateHandler:
    def handle(self, param_dict, value):
        param_dict["end_date"] = datetime.strptime(value, "%Y%m%d")


class ColumnHandler:
    def handle(self, param_dict, value):
        param_dict["column"] = value


class DefaultHandler:
    def handle(self, param_dict, value):
        raise ValueError("Input string does not match the expected format")
