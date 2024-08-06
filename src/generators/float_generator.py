import random
from .generator import AbstractGenerator


class FloatGenerator(AbstractGenerator):
    def __init__(self, min_value: float, max_value: float, precision: int = 2):
        self.min_value = min_value
        self.max_value = max_value
        self.precision = precision

    def generate(self):
        while True:
            yield round(random.uniform(self.min_value, self.max_value), self.precision)
