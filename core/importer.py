from abc import ABC, abstractmethod

class Importer(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> list:
        pass