from datetime import datetime
from typing import List, Optional, Any
from .generator_types import GeneratorType
from .int_generator import IntGenerator
from .float_generator import FloatGenerator
from .string_generator import StringGenerator
from .uuid_generator import UUIDGenerator
from .date_generator import DateGenerator


class GeneratorFactory:
    @staticmethod
    def create_generator(generator_type: GeneratorType, value_set: str) -> Any:

        if generator_type == GeneratorType.INT:
            return IntGenerator(min_value, max_value).generate()

        elif generator_type == GeneratorType.FLOAT:
            min_value = kwargs.get('min_value', 0.0)
            max_value = kwargs.get('max_value', 1.0)
            precision = kwargs.get('precision', 2)
            return FloatGenerator(min_value, max_value, precision).generate()

        elif generator_type == GeneratorType.STRING:
            value_set = kwargs.get('value_set')
            format = kwargs.get('format')
            link = kwargs.get('link')
            return StringGenerator(value_set, format, link).generate()

        elif generator_type == GeneratorType.UUID:
            return UUIDGenerator().generate()

        elif generator_type == GeneratorType.DATE:
            start_date = kwargs.get('start_date', datetime(2000, 1, 1))
            end_date = kwargs.get('end_date', datetime(2030, 12, 31))
            format = kwargs.get('format', 'yyyymmddhhmmss')
            return DateGenerator(start_date, end_date, format).generate()

        else:
            raise ValueError(f"Unknown generator type: {generator_type}")
