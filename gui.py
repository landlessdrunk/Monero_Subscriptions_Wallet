import json
from os import environ, path
import threading
import locale
import logging
import logging.config
import signal
from src.logging import config as logging_config
from tkinter import PhotoImage
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon, QPixmap, QColor
import customtkinter as ctk

import styles
from src.rpc_server import RPCServer
from config import rpc, is_first_launch
from src.views import *
import config as cfg
from src.subscription import Subscription
from PIL import Image, ImageDraw
import sys
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
        self.process_qt_events()

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
        if not self.views[view_name].activated:
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

    # PyQt5 System Tray Setup
    def create_tray_icon(self, app):
        # Create a 32x32 red square pixmap
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(255, 0, 0))  # Red
        icon = QIcon('assets/icon.ico')

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(icon, app)

        # Create context menu
        menu = QMenu()
        restore_action = menu.addAction("Restore")
        quit_action = menu.addAction("Quit")

        # Connect actions
        restore_action.triggered.connect(lambda: self.show_window())
        quit_action.triggered.connect(sys.exit)

        self.tray_icon.setContextMenu(menu)

        self.tray_icon.activated.connect(lambda reason: self.handle_tray_click(reason))

        self.tray_icon.show()
        return self.tray_icon

    def hide_to_tray(self):
        # Minimize to tray instead of closing
        self.withdraw()  # Hide the window
        self.tray_icon.show()

    def handle_tray_click(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.toggle_window()

    def toggle_window(self):
        if self.winfo_viewable():
            self.hide_to_tray()
        else:
            self.show_window()

    def show_window(self):
        # Restore the window
        self.deiconify()
        self.lift()
        self.focus_force()

    def process_qt_events(self):
        # Process Qt events to keep tray icon responsive
        qt_app.processEvents()
        self.after(50, self.process_qt_events)  # Call again after 50ms

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

def signal_handler(sig, frame):
    app.shutdown_steps()
    qt_app.quit()
    sys.exit(0)

#Need to make this work with Windows.
#https://stackoverflow.com/questions/3425294/how-to-detect-the-os-default-language-in-python
locale.setlocale(locale.LC_ALL, environ['LANG'])
qt_app = QApplication(sys.argv)

app = App()
app.title("Monero Subscriptions Wallet")
app.iconphoto(True, PhotoImage(file=styles.icon))
app.protocol("WM_DELETE_WINDOW", app.hide_to_tray)
app.resizable(False, False)  # Make the window non-resizable
app.create_tray_icon(qt_app)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

app.mainloop()
