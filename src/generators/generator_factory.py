import math
from datetime import datetime
from typing import List, Optional, Any

from .empty_generator import EmptyGenerator
from .generator_types import GeneratorType
from .int_generator import IntGenerator
from .float_generator import FloatGenerator
from .string_generator import StringGenerator
from .uuid_generator import UUIDGenerator
from .date_generator import DateGenerator
from parser import Parser

class GeneratorFactory:

    @staticmethod
    def create_generator(generator_type: GeneratorType, value_set: str) -> Any:

        params = {}
        if type(value_set) == str:
            params = Parser.parse(value_set)

        if generator_type == GeneratorType.INT:
            return IntGenerator(**params).generate()

        elif generator_type == GeneratorType.FLOAT:
            min_value = params.get('min_value', 0.0)
            max_value = params.get('max_value', 1.0)
            precision = params.get('precision', 2)
            return FloatGenerator(min_value, max_value, precision).generate()

        elif generator_type == GeneratorType.STRING:
            value_set = params.get('value_set')
            regex = params.get('regex')
            link = params.get('link')
            return StringGenerator(value_set, regex, link).generate()

        elif generator_type == GeneratorType.UUID:
            return UUIDGenerator().generate()

        elif generator_type == GeneratorType.DATE:
            start_date = params.get('start_date', datetime(2000, 1, 1))
            end_date = params.get('end_date', datetime(2030, 12, 31))
            format = params.get('format', 'yyyymmddhhmmss')
            return DateGenerator(start_date, end_date, format).generate()

        elif generator_type == GeneratorType.EMPTY:
            return EmptyGenerator().generate()

        else:
            raise ValueError(f"Unknown generator type: {generator_type}")
