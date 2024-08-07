import random
from abc import ABC, abstractmethod
import exrex
import uuid
import pandas as pd

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Any, Dict

from src.parser import Parser


class GeneratorType(Enum):
    INT = 'int'
    FLOAT = 'float'
    STRING = 'String'
    UUID = 'UUID'
    DATE = 'date'


class AbstractGenerator(ABC):
    @abstractmethod
    def generate(self):
        pass


class DateGenerator(AbstractGenerator):
    def __init__(self, start_date: datetime, end_date: datetime, date_format="yyyymmdd"):
        self.start_date = start_date
        self.end_date = end_date
        self.format = date_format

    def generate(self):
        while True:
            random_date = self.start_date + timedelta(
                seconds=random.randint(0, int((self.end_date - self.start_date).total_seconds()))
            )
            if self.format == 'yyyymmdd':
                yield random_date.strftime('%Y%m%d')
            elif self.format == 'yyyymmddhhmm':
                yield random_date.strftime('%Y%m%d%H%M')
            elif self.format == 'yyyymmddhhmmss':
                yield random_date.strftime('%Y%m%d%H%M%S')
            else:
                yield random_date.strftime('%Y%m%d%H%M%S')  # Default to full format


class FloatGenerator(AbstractGenerator):
    def __init__(self, min_value: float, max_value: float, precision: int = 2):
        self.min_value = min_value
        self.max_value = max_value
        self.precision = precision

    def generate(self):
        while True:
            yield round(random.uniform(self.min_value, self.max_value), self.precision)


class IntGenerator(AbstractGenerator):
    def __init__(self, min_value, max_value):
        self.min_value = min_value
        self.max_value = max_value

    def generate(self):
        while True:
            yield random.randint(self.min_value, self.max_value)


class StringGenerator(AbstractGenerator):
    def __init__(self, value_set: Optional[set[str]] = None, regex: Optional[str] = None, link: Optional[str] = None):
        self.value_set = value_set
        self.regex = regex
        if link:
            df = pd.read_csv(f"../resources/value_sets/{link}", delimiter=";", dtype=str)
            self.value_set = set(df.iloc[:, 0])

    def generate(self):
        if self.value_set:
            while True:
                yield random.choice(tuple(self.value_set))
        elif self.regex:
            while True:
                yield exrex.getone(self.regex)
        else:
            while True:
                yield ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(10))


class UUIDGenerator(AbstractGenerator):
    def generate(self):
        while True:
            yield uuid.uuid4()


class GeneratorFactory:
    @staticmethod
    def _create_int_generator(params: Dict[str, Any]) -> IntGenerator:
        min_value = params.get('min_value', 0)
        max_value = params.get('max_value', 100)
        return IntGenerator(min_value, max_value)

    @staticmethod
    def _create_float_generator(params: Dict[str, Any]) -> FloatGenerator:
        min_value = params.get('min_value', 0.0)
        max_value = params.get('max_value', 1.0)
        precision = params.get('precision', 2)
        return FloatGenerator(min_value, max_value, precision)

    @staticmethod
    def _create_string_generator(params: Dict[str, Any]) -> StringGenerator:
        value_set = params.get('value_set')
        regex = params.get('regex')
        link = params.get('link')
        return StringGenerator(value_set, regex, link)

    @staticmethod
    def _create_uuid_generator() -> UUIDGenerator:
        return UUIDGenerator()

    @staticmethod
    def _create_date_generator(params: Dict[str, Any]) -> DateGenerator:
        start_date = params.get('start_date', datetime(2000, 1, 1))
        end_date = params.get('end_date', datetime(2030, 12, 31))
        date_format = params.get('format', 'yyyymmddhhmmss')
        return DateGenerator(start_date, end_date, date_format)

    @staticmethod
    def create_generator(generator_type: GeneratorType, value_set: str) -> AbstractGenerator:
        params = {}
        if value_set is str:
            params = Parser.parse(value_set)

        if generator_type == GeneratorType.INT:
            return GeneratorFactory._create_int_generator(params)
        elif generator_type == GeneratorType.FLOAT:
            return GeneratorFactory._create_float_generator(params)
        elif generator_type == GeneratorType.STRING:
            return GeneratorFactory._create_string_generator(params)
        elif generator_type == GeneratorType.UUID:
            return GeneratorFactory._create_uuid_generator()
        elif generator_type == GeneratorType.DATE:
            return GeneratorFactory._create_date_generator(params)
        else:
            raise ValueError(f"Unknown generator type: {generator_type}")
