import customtkinter as ctk

import styles
from src.interfaces.view import View
from src.exchange import Exchange
import config as cfg
from config import default_currency, secondary_currency

class SetCurrencyView(View):
    @property
    def geometry(self):
        if not self._geometry:
            self._geometry = styles.SET_CURRENCY_VIEW_GEOMETRY
        return self._geometry

    def build(self):
        def default_currency_selector_callback(choice):
            cfg.config_file.set(section='subscriptions', option='default_currency', value=choice)
            cfg.config_file.write()

        def secondary_currency_selector_callback(choice):
            cfg.config_file.set(section='subscriptions', option='secondary_currency', value=choice)
            cfg.config_file.write()

        self.header('Set Currency:')
        self.back_button()

        self.currency_frame = self.add(ctk.CTkFrame(self._app))
        self.currency_frame.grid_columnconfigure(0, weight=1)
        self.currency_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="new")

        # Labels
        label1 = self.add(ctk.CTkLabel(self.currency_frame, text='Default:'))
        label1.grid(row=2, column=0, columnspan=2, padx=(120, 10), pady=(20, 5), sticky="new")

        label2 = self.add(ctk.CTkLabel(self.currency_frame, text='Secondary:'))
        label2.grid(row=2, column=2, columnspan=2, padx=(10, 120), pady=(20, 5), sticky="new")

        # TODO: Without selected_currency commented out, the buttons don't work on subsequest frames.
        # Default Currency
        self.default_currency_var = ctk.StringVar(value=default_currency())
        self.default_currency = self.add(ctk.CTkOptionMenu(self.currency_frame, values=Exchange.options(), corner_radius=15, command=default_currency_selector_callback, variable=self.default_currency_var))
        self.default_currency.grid(row=3, column=0, columnspan=2, padx=(120, 20), pady=(5, 35))

        # Secondary Currency
        self.secondary_currency_var = ctk.StringVar(value=secondary_currency())
        self.secondary_currency = self.add(ctk.CTkOptionMenu(self.currency_frame, values=Exchange.options(), corner_radius=15, command=secondary_currency_selector_callback, variable=self.secondary_currency_var))
        self.secondary_currency.grid(row=3, column=2, columnspan=2, padx=(20, 120), pady=(5, 35))

        return self

    def activation(self):
        return self
