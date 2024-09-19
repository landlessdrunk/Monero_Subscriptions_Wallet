import json
import os
import threading
import locale
import logging
import logging.config
from src.logging import config as logging_config
from tkinter import PhotoImage

import customtkinter as ctk

import styles
from src.rpc_server import RPCServer
from config import rpc, is_first_launch
from src.views import *
import config as cfg
from src.subscription import Subscription

ctk.set_default_color_theme("monero_theme.json")

# TODO: Get this from the config file first. If not present, use what is currently set below.

class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.config.dictConfig(logging_config)
        self.logger = logging.getLogger(self.__module__)
        self.define_all_views()
        self.spawn_appropriate_initial_window()
        self.start_rpc_server_if_appropriate()
        self.schedule_payments()
        self.scheduler_thread()

    def define_all_views(self):
        self.views = {
            'main': MainView(self),
            'recieve': ReceiveView(self),
            'pay': PayView(self),
            'subscriptions': SubscriptionsView(self),
            'settings': SettingsView(self),
            'set_currency': SetCurrencyView(self),
            'node_selection': NodeSelectionView(self),
            'amount': AmountView(self),
            'review_request': ReviewRequestView(self),
            'review_send': ReviewSendView(self),
            'review_delete': ReviewDeleteRequestView(self),
            'welcome': WelcomeView(self),
            'create_payment_request': CreatePaymentRequestView(self),
            'copy_payment_request': CopyPaymentRequestView(self),
            'history': HistoryView(self)
        }

    def spawn_appropriate_initial_window(self):
        if is_first_launch() == 'True':
            self.current_view = self.views['welcome'].build()
        else:
            self.current_view = self.views['main'].build()

    def start_rpc_server_if_appropriate(self):
        if rpc() == 'True':
            self.rpc_server = RPCServer.get()
            self.rpc_server.start()
            self.rpc_server.check_readiness()

    def switch_view(self, view_name: str):
        self.current_view.destroy()
        self.current_view = self.views[view_name]
        self.current_view.build()

    def schedule_payments(self):
        raw_subs = json.loads(cfg.subscriptions())
        for raw_sub in raw_subs:
            sub = Subscription(**raw_sub)
            sub.queue()

    def scheduler_thread(self):
        sched_thread = threading.Thread(target=self.run_scheduler)
        sched_thread.daemon = True
        sched_thread.start()

    def run_scheduler(self):
        Subscription.schedul.run()

    def shutdown_steps(self):
        self.destroy()
        if rpc() == 'True':
            self.rpc_server.kill()

#Need to make this work with Windows.
#https://stackoverflow.com/questions/3425294/how-to-detect-the-os-default-language-in-python
locale.setlocale(locale.LC_ALL, os.environ['LANG'])

app = App()
app.title("Monero Subscriptions Wallet")
app.iconphoto(True, PhotoImage(file=styles.icon))
app.protocol("WM_DELETE_WINDOW", app.shutdown_steps)
app.resizable(False, False)  # Make the window non-resizable
app.mainloop()
