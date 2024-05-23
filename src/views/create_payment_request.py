import customtkinter as ctk
import tkinter

from src.exchange import Exchange
from src.interfaces.view import View
from config import default_currency
import config as cfg
import styles
import clipboard
import monerorequest
from src.wallet import Wallet


class CreatePaymentRequestView(View):
    def build(self):
        def selected_currency_callback(choice):
            cfg.CURRENT_CREATE_PAYMENT_REQUEST_CURRENCY = choice

        self._app.geometry(styles.CREATE_PAYMENT_REQUEST_VIEW_GEOMETRY)

        # TODO: Can we set the border color through the theme file instead?
        # Border Color
        bc = styles.monero_orange
        x = 10  # 70
        y = 5  # (27.5, 20)

        heading_frame = ctk.CTkFrame(self._app)
        heading_frame.columnconfigure([0, 1, 2], weight=1)
        heading_frame.pack(fill='x', padx=0, pady=0)

        # Back Button
        back_image = ctk.CTkImage(styles.Image.open("back_icon.png"), size=(24, 24))
        back_button = self.add(ctk.CTkButton(heading_frame, image=back_image, text='', fg_color='transparent', width=35, height=30, corner_radius=7, command=self.open_main))
        back_button.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        # Title
        label = self.add(ctk.CTkLabel(heading_frame, text='Create Payment Request:', font=styles.HEADINGS_FONT_SIZE))
        label.grid(row=0, column=1, padx=10, pady=(10, 0), sticky="ew")

        # TODO: Doing this to get it to display properly. There is probably a better way to do this.
        spacer = self.add(ctk.CTkLabel(heading_frame, text=''))
        spacer.grid(row=0, column=3, padx=10, pady=(10, 0), sticky="e")



        content_frame = ctk.CTkFrame(self._app)
        content_frame.pack(fill='both', expand=True, padx=0, pady=0)
        # Configure the grid layout to have 100 columns with equal size
        for i in range(10):
            content_frame.grid_columnconfigure(i, weight=1)

        # Input Title
        self.custom_label_input = self.add(ctk.CTkEntry(content_frame, placeholder_text="Title", corner_radius=15, border_color=bc))  # font=(styles.font, 12),
        self.custom_label_input.grid(row=0, column=0, columnspan=10, padx=x, pady=(10 + y, y), sticky="ew")

        # Pricing & Payments
        self.number_of_payments_input = self.add(ctk.CTkEntry(content_frame, placeholder_text="# Payments", corner_radius=15, border_color=bc))  # font=(styles.font, 12),
        payment_count_options = ["Subscription", "1 payment"]
        for i in range(366):
            if i > 1:
                payment_count_options.append(f"{i} payments")
        selected_number_of_payments = ctk.StringVar(value=payment_count_options[2])
        self.number_of_payments_input = self.add(ctk.CTkOptionMenu(content_frame, values=payment_count_options, corner_radius=15,command=selected_currency_callback, variable=selected_number_of_payments))
        self.number_of_payments_input.grid(row=1, column=0, columnspan=4, padx=x, pady=y, sticky="ew")

        payments_of = self.add(ctk.CTkLabel(content_frame, text="of", font=styles.BODY_FONT_SIZE))
        payments_of.grid(row=1, column=4, columnspan=2, padx=x, pady=y, sticky="ew")

        self.amount_input = self.add(ctk.CTkEntry(content_frame, placeholder_text="Price", corner_radius=15, border_color=bc))  # font=(styles.font, 12),
        self.amount_input.grid(row=1, column=6, columnspan=2, padx=x, pady=y, sticky="ew")

        selected_currency = ctk.StringVar(value=default_currency())
        currency_input = self.add(ctk.CTkOptionMenu(content_frame, values=Exchange.options(), corner_radius=15, command=selected_currency_callback, variable=selected_currency))
        currency_input.grid(row=1, column=8, columnspan=2, padx=x, pady=y, sticky="ew")



        billing_every = self.add(ctk.CTkLabel(content_frame, text="Bills every", font=styles.BODY_FONT_SIZE))
        billing_every.grid(row=2, column=0, columnspan=3, padx=x, pady=y, sticky="ew")

        self.days_per_billing_cycle_input = self.add(ctk.CTkEntry(content_frame, placeholder_text="30 days", corner_radius=15, border_color=bc))  # font=(styles.font, 12),
        self.days_per_billing_cycle_input.grid(row=2, column=3, columnspan=4, padx=x, pady=y, sticky="ew")

        starting_on = self.add(ctk.CTkLabel(content_frame, text="starting:", font=styles.BODY_FONT_SIZE))
        starting_on.grid(row=2, column=7, columnspan=1, padx=x, pady=y, sticky="ew")

        self.start_date_input = self.add(ctk.CTkEntry(content_frame, placeholder_text="mm/dd/yyyy", corner_radius=15, border_color=bc))  #font=(styles.font, 12),
        self.start_date_input.grid(row=2, column=8, columnspan=2, padx=x, pady=y, sticky="ew")




        # Consider having these as ADVANCED settings that you have to expand to see
        self.sellers_wallet_input = self.add(ctk.CTkEntry(content_frame, placeholder_text="Sellers Wallet", corner_radius=15, border_color=bc))  # font=(styles.font, 12),
        self.sellers_wallet_input.grid(row=3, column=0, columnspan=6, padx=x, pady=y, sticky="ew")



        self.change_indicator_url_input = self.add(ctk.CTkEntry(content_frame, placeholder_text="Change Indicator URL (Optional)", corner_radius=15, border_color=bc))  #font=(styles.font, 12),
        self.change_indicator_url_input.grid(row=4, column=0, columnspan=4, padx=(x, 5), pady=(y, 5 + y), sticky="ew")

        self.payment_id_input = self.add(ctk.CTkEntry(content_frame, placeholder_text="Payment ID (Optional)", corner_radius=15, border_color=bc))  # font=(styles.font, 12),
        self.payment_id_input.grid(row=4, column=4, columnspan=2, padx=(5, x), pady=(y, 5 + y), sticky="ew")



        # Create button
        create_button = self.add(ctk.CTkButton(content_frame, text="Create Payment Request", corner_radius=15, command=self.create_button))
        create_button.grid(row=5, column=0, columnspan=10, padx=120, pady=10, sticky="ew")

        return self

    def open_main(self):
        self._app.switch_view('main')

    def create_button(self):
        self._app.switch_view('main')
