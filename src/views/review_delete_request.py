import customtkinter as ctk
from src.interfaces.view import View
import config as cfg
import styles


class ReviewDeleteRequestView(View):
    def build(self):
        # Title
        self.header('Cancel Subscription?')
        self.back_button()
        # Frame to hold buttons
        center_frame = self.add(ctk.CTkFrame(self._app, ))
        center_frame.grid(row=1, column=0, columnspan=3, padx=0, pady=15, sticky="nsew")
        center_frame.columnconfigure([0, 1, 2, 3, 4, 5], weight=1)

        # No Button
        no_button = self.add(ctk.CTkButton(center_frame, text="No", corner_radius=15, command=self.open_main))
        no_button.grid(row=0, column=2, padx=(10, 5), pady=0, sticky="ew")

        # Yes Button
        yes_button = self.add(ctk.CTkButton(center_frame, text="Yes", corner_radius=15, command=self.cancel_action))
        yes_button.grid(row=0, column=3, padx=(5, 10), pady=0, sticky="ew")

        return self

    def activation(self):
        self._app.geometry(styles.REVIEW_PROMPT_GEOMETRY)
        return self

    def open_main(self):
        self._app.switch_view('subscriptions')

    def cancel_action(self):
        cfg.config_file.remove_subscription(cfg.SELECTED_SUBSCRIPTION)
        cfg.SELECTED_SUBSCRIPTION.deschedule()
        cfg.SELECTED_SUBSCRIPTION = ''
        self._app.switch_view('subscriptions')
