import customtkinter as ctk
import tkinter
from src.interfaces.view import View
from config import stagenet
import config as cfg
import styles
import clipman
from monerorequest import Check, Decode, RequestV2
from src.wallet import Wallet

def input_is_valid(input_string):
    if input_string:
        if input_is_valid_monero_wallet(input_string) or input_is_valid_monero_request(input_string):
            return True

    return False

def input_is_valid_monero_wallet(input_string):
    return Check.wallet(wallet_address=input_string, allow_standard=True, allow_integrated_address=True, allow_subaddress=True, allow_stagenet=stagenet())

def input_is_valid_monero_request(input_string):
    if 'monero-request:' in input_string:
        # Decode it
        request_attrs = Decode.monero_payment_request_from_code(monero_payment_request=input_string)
        del request_attrs['version']
        decoded_request = RequestV2(**request_attrs)
        decoded_request.allow_standard = True
        decoded_request.allow_integrated_address = True
        decoded_request.allow_subaddress = True
        decoded_request.allow_stagenet = stagenet()

        return decoded_request.valid()

    else:
        return False

class PayView(View):
    def build(self):
        self.header('Pay To:')
        self.back_button()

        # Next button
        self.next_button = self.add(ctk.CTkButton(self._app, text="Continue", corner_radius=15, command=self.next_button_action))
        self.next_button.grid(row=2, column=0, columnspan=3, padx=120, pady=15, sticky="ew")

        self._app.update_idletasks()
        return self

    def activation(self):
        self._app.geometry(styles.PAY_VIEW_GEOMETRY)
        return self

    def reactivate(self):
        super().reactivate()
        # TODO: Can we set the border color through the theme file instead?
        # Input box
        self.payment_input = tkinter.StringVar(self._app, name='payment_input')
        clipman.init()
        clipman_contents = clipman.paste()
        if input_is_valid(input_string=clipman_contents) and clipman_contents != Wallet().address:
            self.payment_input.set(clipman_contents)

            # TODO: refactor this to be better?
            self.input_box_for_wallet_or_request = self.add(ctk.CTkEntry(self._app, textvariable=self.payment_input, font=(styles.font, 12), corner_radius=15, border_color=styles.monero_orange))
        else:
            self.input_box_for_wallet_or_request = self.add(ctk.CTkEntry(self._app, placeholder_text="Enter a monero payment request or wallet address...", font=(styles.font, 12), corner_radius=15, border_color=styles.monero_orange))

        self.input_box_for_wallet_or_request.grid(row=1, column=0, columnspan=3, padx=70, pady=(27.5, 0), sticky="ew")

    def wallet_or_request_logic(self, input_string):
        if 'monero-request:' in input_string:
            self._app.switch_view('review_request')
        else:
            cfg.SEND_TO_WALLET = input_string
            # Move to "how much" view
            self._app.switch_view('amount')

    def next_button_action(self):
        input_string = self.input_box_for_wallet_or_request.get().strip()
        if input_is_valid(input_string=input_string):
            self.wallet_or_request_logic(input_string=input_string)
        else: # pragma: no cover
            #TODO: Add error message
            print('Not a Monero Payment Request or wallet address')
