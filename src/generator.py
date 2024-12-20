import os
import random
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Any, Optional

import exrex
import pandas as pd


class GeneratorType(Enum):
    """
    Enum representing different types of generators.
    """
    INT = 'int'
    FLOAT = 'float'
    STRING = 'string'
    UUID = 'UUID'
    DATE = 'date'
    LOOKUP = 'lookup'


class AbstractGenerator(ABC):
    @abstractmethod
    def generate(self, count: int) -> List[Any]:
        """
        Generate a list of random values.

        Args:
            count (int): The number of values to generate.

        Returns:
            List[Any]: A list of generated values.
        """
        pass


class DateGenerator(AbstractGenerator):
    """
    Generator for random dates within a specified range.
    """

    def __init__(
            self,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            date_format: str = "%Y%m%d%H%M%S"
    ) -> None:
        """
        Initialize the DateGenerator with optional parameters.

        Args:
            start_date (datetime, optional): The start date for the range. Defaults to January 1, 2000.
            end_date (datetime, optional): The end date for the range. Defaults to today.
            date_format (str, optional): The format of the generated date strings. Defaults to "%Y%m%d%H%M%S".
        """
        self.start_date = start_date if start_date else datetime(2000, 1, 1)
        self.end_date = end_date if end_date else datetime.today()
        self.format = date_format

    def _get_random_date(self) -> datetime:
        """
        Get a random date within the specified range.

        Returns:
            datetime: A random date within the specified range.
        """
        return self.start_date + timedelta(
            seconds=random.randint(0, int((self.end_date - self.start_date).total_seconds())))

    def generate(self, count: int) -> List[str]:
        """
        Generate random dates within the specified range and format.

        Args:
            count (int): The number of dates to generate.

        Returns:
            List[str]: A list of randomly generated date strings.
        """
        return [self._get_random_date().strftime(self.format) for _ in range(count)]


class FloatGenerator(AbstractGenerator):
    """
    Generator for random float values within a specified range.
    """

    def __init__(
            self,
            min_value: float = 0.0,
            max_value: float = 0.0,
            precision: int = 2
    ) -> None:
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

    def generate(self, count: int) -> List[float]:
        """
        Generate random float values within the specified range and precision.

        Args:
            count (int): The number of float values to generate.

        Returns:
            List[float]: A list of randomly generated float values.
        """
        return [round(random.uniform(self.min_value, self.max_value), self.precision) for _ in range(count)]


class IntGenerator(AbstractGenerator):
    """
    Generator for random integer values within a specified range.
    """

    def __init__(
            self,
            min_value: int = 0,
            max_value: int = 100
    ) -> None:
        """
        Initialize the IntGenerator with optional parameters.

        Args:
            min_value (int, optional): The minimum value for the range. Defaults to 0.
            max_value (int, optional): The maximum value for the range. Defaults to 100.
        """
        self.min_value = min_value
        self.max_value = max_value

    def generate(self, count: int) -> List[int]:
        """
        Generate random integer values within the specified range.

        Args:
            count (int): The number of integer values to generate.

        Returns:
            List[int]: A list of randomly generated integer values.
        """
        return [random.randint(self.min_value, self.max_value) for _ in range(count)]


class LookupGenerator(AbstractGenerator):
    """
    Generator for random values from a specified column in a CSV file.
    """

    def __init__(
            self,
            link: Optional[str] = None,
            column: Optional[str] = None,
            **kwargs: Dict[str, Any]
    ) -> None:
        """
        Initialize the LookupGenerator with a link to a CSV file and a column name.

        Args:
            link (str, optional): The path to the CSV file. Defaults to None.
            column (str, optional): The column name in the CSV file to use for the value set. Defaults to None.
        """
        self.link = link
        self.column = column
        # TODO Catch other dependent columns
        self.dependent_columns = kwargs.get('dependent_column_1', None)
        self.dependent_concept_id = kwargs.get('dependent_concept_id_1', None)
        self._load_value_set_from_csv()

    def _load_value_set_from_csv(self):
        """
        Load the value set from the specified column in the CSV file.

        Args:
            link (str): The path to the CSV file.
            column (str): The column name in the CSV file to use for the value set.

        Raises:
            ValueError: If the column is not specified or not found in the file.
        """
        if not self.column:
            raise ValueError("Column not specified in parameters")

        if not os.path.isfile(self.link):
            raise ValueError(f"File '{self.link}' does not exist.")

        df = pd.read_csv(self.link, delimiter=";", dtype=str, header=0)
        if self.column not in df.columns:
            raise ValueError(f"Column '{self.column}' not found in file")

        if self.dependent_columns:
            self.value_set = df[[self.column] + [self.dependent_columns]]
        else:
            self.value_set = df[self.column]

    def generate(self, count: int) -> List[str]:
        """
        Generate random values from the loaded value set.

        Args:
            count (int): The number of values to generate.

        Returns:
            List[str]: A list of randomly generated values from the value set.
        """
        return self.value_set.sample(n=count, replace=True).values.tolist()


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

    def generate(self, count: int) -> List[str]:
        """
        Generate random string values based on the value set or regex pattern.

        Args:
            count (int): The number of string values to generate.

        Returns:
            List[str]: A list of randomly generated string values.
        """
        if self.value_set:  # If value set is provided, choose from it
            return [random.choice(tuple(self.value_set)) for _ in range(count)]
        elif self.regex:  # If regex pattern is provided, generate strings based on it
            return [exrex.getone(self.regex) for _ in range(count)]
        else:  # Default to empty strings
            return ['' for _ in range(count)]


class UUIDGenerator(AbstractGenerator):
    """
    Generator for random UUID values.
    """

    def __init__(self, **kwargs: Dict[str, Any]) -> None:
        """
        Initialize the UUIDGenerator with optional parameters.

        Args:
            **kwargs: Additional parameters (not used).
        """
        pass

    def generate(self, count: int) -> List[uuid.UUID]:
        """
        Generate random UUID values.

        Args:
            count (int): The number of UUID values to generate.

        Returns:
            List[uuid.UUID]: A list of randomly generated UUID values.
        """
        return [uuid.uuid4() for _ in range(count)]


class GeneratorFactory:
    """
    Factory class to create generator instances based on the generator type.
    """
    _generator_map: Dict[GeneratorType, AbstractGenerator] = {
        GeneratorType.INT: IntGenerator,
        GeneratorType.FLOAT: FloatGenerator,
        GeneratorType.STRING: StringGenerator,
        GeneratorType.UUID: UUIDGenerator,
        GeneratorType.DATE: DateGenerator,
        GeneratorType.LOOKUP: LookupGenerator,
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
        except KeyError:
            raise KeyError(f"Unknown generator type: {generator_type}")

        return generator_class(**params)
