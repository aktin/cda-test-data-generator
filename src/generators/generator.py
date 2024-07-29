from abc import ABC, abstractmethod

class AbstractGenerator(ABC):
    @abstractmethod
    def generate(self):
        pass