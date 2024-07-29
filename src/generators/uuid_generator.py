import uuid
from generator import AbstractGenerator

class UUIDGenerator(AbstractGenerator):
    def generate(self):
        while True:
            yield uuid.uuid4()