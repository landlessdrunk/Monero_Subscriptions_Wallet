from abc import ABC, abstractmethod

class View(ABC):
    def __init__(self, app):
        self._app = app
        self._elements = []
        self._activated = False

    def add(self, element):
        self._elements.append(element)
        return element

    def destroy(self):
        for element in reversed(self._elements):
            element.destroy()
        self._elements = []

    @abstractmethod
    def build(self):
        pass

    def activate(self):
        self.activation()
        self._activated = True

    @abstractmethod
    def activation(self):
        pass

    def deactivate(self):
        for element in self._elements:
            element.grid_remove()

    def reactivate(self):
        for element in self._elements:
            element.grid()

    @property
    def activated(self):
        return self._activated
