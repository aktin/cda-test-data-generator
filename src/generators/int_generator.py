import random
from .generator import AbstractGenerator


class IntGenerator(AbstractGenerator):
    def __init__(self, **kwargs):
        self.min_value = kwargs['min_value']
        self.max_value = kwargs['max_value']

    def generate(self):
        while True:
            yield random.randint(self.min_value, self.max_value)
