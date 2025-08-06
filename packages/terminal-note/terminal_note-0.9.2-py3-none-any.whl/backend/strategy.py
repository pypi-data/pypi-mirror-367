from abc import ABC, abstractmethod


class HandlerStrategy(ABC):
    @abstractmethod
    def create(self, file_name):
        pass

    @abstractmethod
    def inline_note(self, text):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def read(self):
        pass


class HandlerService:
    def __init__(self, strategy: HandlerStrategy):
        self._strategy = strategy

    def create(self, file_name):
        return self._strategy.create(file_name)

    def inline_note(self, text):
        return self._strategy.inline_note(text)

    def update(self):
        return self._strategy.update()

    def delete(self):
        return self._strategy.delete()

    def read(self):
        return self._strategy.read()
