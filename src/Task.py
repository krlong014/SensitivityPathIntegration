from abc import ABC, abstractmethod

class Function(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def run(self, arg):
        pass

    def cleanup(self):
        pass

class ResultAnalyzer(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def acceptResult(self, result):
        pass

    def postprocess(self, arg):
        pass

    def cleanup(self):
        pass
