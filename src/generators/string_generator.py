import random
import exrex
import pandas as pd
from typing import List, Optional
from .generator import AbstractGenerator

class StringGenerator(AbstractGenerator):
    def __init__(self, value_set: Optional[set[str]] = None, regex: Optional[str] = None, link: Optional[str] = None):
        self.value_set = value_set
        self.regex = regex
        if link:
            df = pd.read_csv(f"../res/value_sets/{link}", delimiter=";",  dtype=str)
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