
from .generator import AbstractGenerator


class EmptyGenerator(AbstractGenerator):

    def generate(self):
        while True:
            yield ""
