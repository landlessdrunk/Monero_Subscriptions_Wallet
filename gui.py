import json
from os import environ, path
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
import pystray
from PIL import Image, ImageDraw

ctk.set_default_color_theme(path.abspath(path.join(path.dirname(__file__), "monero_theme.json")))

# TODO: Get this from the config file first. If not present, use what is currently set below.

class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_view = None
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
        for view in self.views.values():
            view.build()
            view.deactivate()

    def spawn_appropriate_initial_window(self):
        if is_first_launch() == 'True':
            self.switch_view('welcome')
        else:
            self.switch_view('main')

    def start_rpc_server_if_appropriate(self):
        if rpc() == 'True':
            self.rpc_server = RPCServer.get()
            self.rpc_server.start()
            self.rpc_server.check_readiness()

    def switch_view(self, view_name: str):
        if self.current_view:
            self.current_view.deactivate()
        self.views[view_name].reactivate()
        self.views[view_name].activate()
        self.current_view = self.views[view_name]

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
        # self.icon.stop()
        if rpc() == 'True':
            self.rpc_server.kill()

    def tray_icon(self):
        # img = Image.open('assets/icon_black.png')
        # sized_img = img.resize(size=[64,64])
        """
        Looking through the [_draw](https://github.com/moses-palmer/pystray/blob/master/lib/pystray/_xorg.py#L354)
        function the `dim.width` and `dim.height` values I'm getting are just 1, and 1.
        This makes some amount of sense since I suppose there isn't anything in `self._window` yet,
        but what confuses me is that [_assert_icon_data](https://github.com/moses-palmer/pystray/blob/master/lib/pystray/_xorg.py#L366)
        function then uses these dimensions to resize the `_icon` and [paste](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.paste)
        it into the `_icon_data` `PIL.Image` that was created. All that said, trying to change these dimensions doesn't help.
        """
        sized_img = Image.open('assets/app.ico')
        self.icon = pystray.Icon('Monero Subscriptions Wallet', icon=self.create_image(64,64,'black','white'))
        self.icon.run_detached()

    def create_image(self, width, height, color1, color2):
        # Generate an image and draw a pattern
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            (width // 2, 0, width, height // 2),
            fill=color2)
        dc.rectangle(
            (0, height // 2, width // 2, height),
            fill=color2)

        return image

#Need to make this work with Windows.
#https://stackoverflow.com/questions/3425294/how-to-detect-the-os-default-language-in-python
locale.setlocale(locale.LC_ALL, environ['LANG'])

app = App()
app.title("Monero Subscriptions Wallet")
app.iconphoto(True, PhotoImage(file=styles.icon))
app.protocol("WM_DELETE_WINDOW", app.shutdown_steps)
app.resizable(False, False)  # Make the window non-resizable
# app.tray_icon()
app.mainloop()
