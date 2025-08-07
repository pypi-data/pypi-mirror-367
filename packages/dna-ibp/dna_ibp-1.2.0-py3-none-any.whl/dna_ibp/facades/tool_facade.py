# tool_facade.py
# facade parent class for minor DNA analyser tools (G4Killer & P53 predictor)
from abc import ABCMeta, abstractmethod

class Tool(metaclass=ABCMeta):

    def __init__(self, api):
        self.api = api

    @abstractmethod
    def run(self, *args) -> None:
        raise NotImplementedError("Not implemented.")