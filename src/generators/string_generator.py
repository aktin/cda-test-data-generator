import random
from typing import List, Optional
from .generator import AbstractGenerator

class StringGenerator(AbstractGenerator):
    def __init__(self, value_set: Optional[List[str]] = None, format: Optional[str] = None, link: Optional[str] = None):
        self.value_set = value_set
        self.format = format
        self.link = link

        if self.link:
            # In a real scenario, you'd read from the file here
            # For this example, we'll just use a dummy set
            self.value_set = ["file1", "file2", "file3"]

    def generate(self):
        if self.value_set:
            while True:
                for value in self.value_set:
                    yield value
        elif self.format:
            while True:
                yield ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(len(self.format)))
        else:
            while True:
                yield ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(10))