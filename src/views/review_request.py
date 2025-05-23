import customtkinter as ctk
from src.interfaces.view import View
from src.subscription import Subscription
import config as cfg
import styles
from monerorequest import decode_monero_payment_request
from datetime import datetime
from cron_descriptor import get_description

class ReviewRequestView(View):
    def build(self):
        self.header('Add Payment Request?')
        self.back_button()

        # TODO: Have window adjust automatically if we even display this.
        '''
        if decoded_request["change_indicator_url"]:
            sellers_wallet_label = self.add(ctk.CTkLabel(self._app, text=f'(Seller may request changes to this. If they do, payments will be paused until you approve them.)', font=styles.BODY_FONT_SIZE))
            sellers_wallet_label.grid(row=5, column=0, columnspan=3, padx=10, pady=0, sticky="ew")
        '''

        # Frame to hold buttons
        self.center_frame = self.add(ctk.CTkFrame(self._app, ))
        self.center_frame.grid(row=6, column=0, columnspan=3, padx=0, pady=10, sticky="nsew")
        self.center_frame.columnconfigure([0, 1], weight=1)  # Frame will span 3 columns but contain two columns (0 and 1)

        # Cancel button
        cancel_button = self.add(ctk.CTkButton(self.center_frame, text="No Thanks", corner_radius=15, command=self.cancel_button))
        cancel_button.grid(row=0, column=0, padx=(10, 5), pady=(0, 10), sticky="ew")

        return self

    def activation(self):
        self._app.geometry(styles.REVIEW_REQUEST_PROMPT_VIEW_GEOMETRY)
        self.decoded_request = decode_monero_payment_request(self._app.views['pay'].payment_input.get())
        # Custom Label
        self.custom_label = self.add(ctk.CTkLabel(self._app, text=self.custom_label_text(), font=styles.SUBHEADING_FONT_SIZE))
        self.custom_label.grid(row=1, column=0, columnspan=3, padx=10, pady=(10, 0), sticky="ew")

        # TODO: show conversion to default currency in ()
        self.amount_label = self.add(ctk.CTkLabel(self._app, text=self.amount_label_text(), font=styles.BODY_FONT_SIZE))
        self.amount_label.grid(row=2, column=0, columnspan=3, padx=10, pady=0, sticky="ew")

        # Start Date  decoded_request["start_date"]
        self.starting_on = self.add(ctk.CTkLabel(self._app, text=self.starting_on_text(), font=styles.BODY_FONT_SIZE))
        self.starting_on.grid(row=3, column=0, columnspan=3, padx=10, pady=0, sticky="ew")

        # Sellers Wallet
        self.sellers_wallet_label = self.add(ctk.CTkLabel(self._app, text=self.sellers_wallet_label_text(), font=styles.BODY_FONT_SIZE))
        self.sellers_wallet_label.grid(row=4, column=0, columnspan=3, padx=10, pady=0, sticky="ew")

        # Confirm button
        self.confirm_button = self.add(ctk.CTkButton(self.center_frame, text=self.confirm_button_text(), corner_radius=15,  command=self.confirm_button))
        self.confirm_button.grid(row=0, column=1, padx=(5, 10), pady=(0, 10), sticky="ew")
        return self

    def reactivation(self):
        super().reactivation()
        self._app.geometry(styles.REVIEW_REQUEST_PROMPT_VIEW_GEOMETRY)
        self.decoded_request = decode_monero_payment_request(self._app.views['pay'].payment_input.get())
        # Custom Label
        self.custom_label.configure(text=self.custom_label_text())
        self.amount_label.configure(text=self.amount_label_text())
        self.starting_on.configure(text=self.starting_on_text())
        self.sellers_wallet_label.configure(text=self.sellers_wallet_label_text())
        self.confirm_button.configure(text=self.confirm_button_text())


    def custom_label_text(self):
        if self.decoded_request:
            label_text = f'{self.decoded_request["custom_label"][:80]}:'
        else:
            label_text = ''
        return label_text

    def amount_label_text(self):
        if self.decoded_request:
            worth_of_xmr_text = ' worth of XMR' if self.decoded_request["currency"].upper() != 'XMR' else ''
            label_text = f'{self.decoded_request["amount"]} {self.decoded_request["currency"]}{worth_of_xmr_text} billed {get_description(self.decoded_request["schedule"]).lower()}'
        else:
            label_text = ''
        return label_text


    def starting_on_text(self):
        if self.decoded_request:
            label_text = f'First payment due: {datetime.strptime(self.decoded_request["start_date"].split("T")[0], "%Y-%m-%d").strftime("%B %-d, %Y")}'
        else:
            label_text = ''
        return label_text

    def sellers_wallet_label_text(self):
        if self.decoded_request:
            label_text = f'Paying To: {self.decoded_request["sellers_wallet"][:5]}...{self.decoded_request["sellers_wallet"][-5:]}'
        else:
            label_text = ''
        return label_text

    def confirm_button_text(self):
        if self.decoded_request:
            label_text = "Pay Now" if self.decoded_request["number_of_payments"] == 1 else "Subscribe"
        else:
            label_text = ''
        return label_text

    def open_main(self):
        self._app.switch_view('main')

    def cancel_button(self):
        self.open_main()

    def confirm_button(self):
        sub = Subscription(**Subscription.decode(self._app.views['pay'].payment_input.get()))
        cfg.config_file.add_subscription(sub)
        sub.queue()
        #TODO: Adding subscription doesn't seem to start the scheduled payments.
        #TODO: Adding subscription doesn't seem to add the subscription to the view.
        self._app.switch_view('subscriptions')
