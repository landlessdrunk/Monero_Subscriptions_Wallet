from abc import ABC, abstractmethod
import logging
import logging.config
from src.logging import config as logging_config
import customtkinter as ctk
import styles
from PIL import Image

class View(ABC):
    def __init__(self, app):
        self._app = app
        self._elements = []
        self._activated = False
        self._header = None
        self._back_button = None
        logging.config.dictConfig(logging_config)
        self.logger = logging.getLogger(self.__module__)

    def add(self, element):
        self._elements.append(element)
        return element

    def destroy(self):
        for element in reversed(self._elements):
            element.destroy()
        self._elements = []

    @abstractmethod
    def build(self): # pragma: no cover
        pass

    def activate(self):
        self.activation()
        self._activated = True

    @abstractmethod
    def activation(self): # pragma: no cover
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

    def header(self, text):
        if not self._header:
            self._header = self.add(ctk.CTkLabel(self._app, text=text, font=styles.HEADINGS_FONT_SIZE))
            self._header.grid(row=0, column=1, padx=0, pady=10, sticky="nsew")
            center_helper = self.add(ctk.CTkLabel(self._app, text='', font=styles.HEADINGS_FONT_SIZE))
            center_helper.grid(row=0, column=2, padx=30, pady=0, sticky="e")
        return self._header

    def back_button(self):
        # Back Button
        if not self._back_button:
            back_image = ctk.CTkImage(Image.open(styles.back_icon), size=(24, 24))
            self._back_button = self.add(ctk.CTkButton(self._app, image=back_image, text='', fg_color='transparent', width=35, height=30, corner_radius=7, command=self.last_page))
            self._back_button.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        return self._back_button

    def last_page(self):
        self._app.switch_view_last()
