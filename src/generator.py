import random
import exrex
import uuid
import pandas as pd

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict


class GeneratorType(Enum):
    """
    Enum representing different types of generators.
    """
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
    """
    Generator for random dates within a specified range.
    """
    def __init__(self, start_date=None, end_date=None, date_format="yyyymmddhhmmss"):
        """
        Initialize the DateGenerator with optional parameters.

        Args:
            start_date (datetime, optional): The start date for the range. Defaults to January 1, 2000.
            end_date (datetime, optional): The end date for the range. Defaults to today.
            date_format (str, optional): The format of the generated date strings. Defaults to "yyyymmddhhmmss".
        """
        self.start_date = start_date if start_date else datetime(2000, 1, 1)
        self.end_date = end_date if end_date else datetime.today()
        self.format = date_format

    def generate(self):
        """
        Generate random dates within the specified range and format.

        Yields:
            str: A randomly generated date string.
        """
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
    """
    Generator for random float values within a specified range.
    """

    def __init__(self, min_value=0.0, max_value=0.0, precision=2):
        """
        Initialize the FloatGenerator with optional parameters.

        Args:
            min_value (float, optional): The minimum value for the range. Defaults to 0.0.
            max_value (float, optional): The maximum value for the range. Defaults to 0.0.
            precision (int, optional): The number of decimal places for the generated values. Defaults to 2.
        """
        self.min_value = min_value
        self.max_value = max_value
        self.precision = precision

    def generate(self):
        """
        Generate random float values within the specified range and precision.

        Yields:
            float: A randomly generated float value.
        """
        while True:
            yield round(random.uniform(self.min_value, self.max_value), self.precision)


class IntGenerator(AbstractGenerator):
    """
    Generator for random integer values within a specified range.
    """

    def __init__(self, min_value=0, max_value=100):
        """
        Initialize the IntGenerator with optional parameters.

        Args:
            min_value (int, optional): The minimum value for the range. Defaults to 0.
            max_value (int, optional): The maximum value for the range. Defaults to 100.
        """
        self.min_value = min_value
        self.max_value = max_value

    def generate(self):
        """
        Generate random integer values within the specified range.

        Yields:
            int: A randomly generated integer value.
        """
        while True:
            yield random.randint(self.min_value, self.max_value)


class StringGenerator(AbstractGenerator):
    """
    Generator for random string values based on a value set or regex pattern.
    """

    def __init__(self, value_set=None, regex=None, link=None, column=None):
        """
        Initialize the StringGenerator with optional parameters.

        Args:
            value_set (set, optional): A set of predefined string values to choose from.
            regex (str, optional): A regex pattern to generate random strings.
            link (str, optional): A path to a CSV file containing a column of string values.
            column (str, optional): The column name in the CSV file to use for the value set.
        """
        self.value_set = value_set
        self.regex = regex
        if link is not None:
            self._load_value_set_from_csv(link, column)

    def _load_value_set_from_csv(self, link, column):
        if not column:
            raise ValueError("Column not specified in parameters")
        df = pd.read_csv(f"../resources/value_sets/{link}", delimiter=";", dtype=str, header=0)
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in file")

        self.value_set = set(df[column])

    def generate(self):
        """
        Generate random string values based on the value set or regex pattern.

        Yields:
            str: A randomly generated string value.
        """
        if self.value_set:  # If value set is provided, choose from it
            while True:
                yield random.choice(tuple(self.value_set))
        elif self.regex:  # If regex pattern is provided, generate strings based on it
            while True:
                yield exrex.getone(self.regex)
        else:  # Default to random alphanumeric strings
            while True:
                yield ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(10))


class UUIDGenerator(AbstractGenerator):

    def __init__(self, **kwargs):
        pass

    def generate(self):
        """
        Generate random UUID values.

        Yields:
            UUID: A randomly generated UUID.
        """
        while True:
            yield uuid.uuid4()


class GeneratorFactory:
    """
    Factory class to create generator instances based on the generator type.
    """
    _generator_map: Dict[GeneratorType, AbstractGenerator] = {
        GeneratorType.INT: IntGenerator,
        GeneratorType.FLOAT: FloatGenerator,
        GeneratorType.STRING: StringGenerator,
        GeneratorType.UUID: UUIDGenerator,
        GeneratorType.DATE: DateGenerator
    }

    @classmethod
    def create_generator(cls, generator_type: GeneratorType, params: dict) -> AbstractGenerator:
        """
        Create a generator instance based on the provided generator type and parameters.

        Args:
            generator_type (GeneratorType): The type of generator to create.
            params (dict): A dictionary of parameters to initialize the generator.

        Returns:
            AbstractGenerator: An instance of a generator corresponding to the specified type.

        Raises:
            KeyError: If the provided generator type is unknown.
        """
        try:
            generator_class = cls._generator_map[generator_type]
        except:
            raise KeyError(f"Unknown generator type: {generator_type}")

        return generator_class(**params)
