import customtkinter as ctk
from src.interfaces.view import View
import config as cfg
import styles
from monerorequest import Check
from src.clients.rpc import RPCClient
from src.exchange import Exchange

def clear_temp_payment_info():
    cfg.CURRENT_PAYMENT_REQUEST = ''
    cfg.CURRENT_SEND_CURRENCY = ''
    cfg.CURRENT_SEND_AMOUNT = ''
    cfg.SEND_TO_WALLET = ''


class ReviewSendView(View):
    @property
    def geometry(self):
        if not self._geometry:
            self._geometry = styles.REVIEW_PROMPT_GEOMETRY
        return self._geometry

    def build(self):
        # Title
        self.header('Send Payment?')
        self._header.grid(row=0, column=0, columnspan=3, padx=10, pady=(45, 5), sticky="ew")

        # Frame to hold buttons
        center_frame = self.add(ctk.CTkFrame(self._app, ))
        center_frame.grid(row=3, column=0, columnspan=3, padx=0, pady=15, sticky="nsew")
        center_frame.columnconfigure([0, 1, 2, 3, 4, 5], weight=1)

        # Cancel button
        self.cancel_button = self.add(ctk.CTkButton(center_frame, text="Cancel", corner_radius=15, command=self.cancel_button))
        self.cancel_button.grid(row=0, column=2, padx=(10, 5), pady=0, sticky="e")

        # Confirm button
        self.confirm_button = self.add(ctk.CTkButton(center_frame, text="Send", corner_radius=15, command=self.confirm_button))
        self.confirm_button.grid(row=0, column=3, padx=(5, 10), pady=0, sticky="w")

        return self

    def activation(self):
        return self

    def reactivate(self):
        super().reactivate()
        # TODO: show conversion to default currency in ()
        worth_of_xmr_text = ' worth of XMR' if cfg.CURRENT_SEND_CURRENCY.upper() != 'XMR' else ''
        self.sending_to = self.add(ctk.CTkLabel(self._app, text=f'{cfg.CURRENT_SEND_AMOUNT} {cfg.CURRENT_SEND_CURRENCY}{worth_of_xmr_text} to: {cfg.SEND_TO_WALLET[:5]}...{cfg.SEND_TO_WALLET[-5:]}', font=styles.SUBHEADING_FONT_SIZE))
        self.sending_to.grid(row=1, column=0, columnspan=3, padx=10, pady=0, sticky="ew")

    def cancel_button(self):
        clear_temp_payment_info()
        self.open_main()

    def confirm_button(self):
        # TODO: Make send payment work
        # Send the payment

        # Confirm if it worked or not (if not, let them retry)
        if RPCClient.get().transfer(cfg.SEND_TO_WALLET, Exchange.to_atomic_units(cfg.CURRENT_SEND_CURRENCY, cfg.CURRENT_SEND_AMOUNT)):
            clear_temp_payment_info()
            self.open_main()
        else:
            self.open_amount()

    def open_amount(self):
        self._app.switch_view('amount')

    def open_main(self):
        self._app.switch_view('main')
