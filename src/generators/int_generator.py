import random
from generator import AbstractGenerator

class IntGenerator(AbstractGenerator):
    def __init__(self, min_value: int, max_value: int):
        self.min_value = min_value
        self.max_value = max_value

    def generate(self):
        while True:
            yield random.randint(self.min_value, self.max_value)