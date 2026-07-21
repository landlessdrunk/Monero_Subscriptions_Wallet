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
from src.monerod import Monerod
from config import rpc, is_first_launch, daemon_executable
from src.views import MainView, ReceiveView, PayView, SubscriptionsView, SettingsView, SetCurrencyView,\
                      NodeSelectionView, AmountView, ReviewRequestView, ReviewSendView,\
                      ReviewDeleteRequestView, WelcomeView, CreatePaymentRequestView, CopyPaymentRequestView,\
                      HistoryView
import config as cfg
from src.subscription import Subscription
from PIL import Image, ImageDraw
import sys
import queue
import time

ctk.set_default_color_theme(path.abspath(path.join(path.dirname(__file__), "monero_theme.json")))

# TODO: Get this from the config file first. If not present, use what is currently set below.

class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_view = None
        self.stop_subscriptions = False
        self.rpc_server = None
        logging.config.dictConfig(logging_config)
        self.logger = logging.getLogger(self.__module__)
        self._qt_app = QApplication(sys.argv)
        self.transactions_queue = queue.Queue()
        self.subscriptions_queue = queue.Queue()
        self.define_all_views()
        self.last_views = []
        self.spawn_appropriate_initial_window()
        self.start_rpc_server_if_appropriate()
        self.start_monerod_if_appropriate()
        self.schedule_payments()
        self.scheduler_thread()
        self.process_qt_events()
        self.process_tx_queue()
        self.process_sub_queue()

    def process_tx_queue(self):
        try:
            task = self.transactions_queue.get_nowait()
            task()
            self.transactions_queue.task_done()
        except queue.Empty: # pragma: no cover
            pass
        self.after(5000, self.process_tx_queue)

    def process_sub_queue(self):
        try:
            task = self.subscriptions_queue.get_nowait()
            task()
            self.subscriptions_queue.task_done()
        except queue.Empty:
            pass
        self.after(50, self.process_sub_queue)

    def define_all_views(self):
        self.views = {
            'main': MainView(self),
            'receive': ReceiveView(self),
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

    def view_name(self, check_view):
        for name, view in self.views.items():
            if view == check_view:
                return name

    def switch_view_last(self):
        last_view = self.last_views.pop()
        self.switch_view(self.view_name(last_view), True)

    def spawn_appropriate_initial_window(self):
        if is_first_launch() == 'True':
            self.switch_view('welcome')
        else:
            self.switch_view('main')

    def start_rpc_server_if_appropriate(self):
        if rpc() == 'True': # pragma: no cover
            self.rpc_server = RPCServer.get()
            self.rpc_server.start()
            self.rpc_server.check_readiness()

    def start_monerod_if_appropriate(self):
        if daemon_executable():
            self.monerod = Monerod.get()
            self.monerod.start()
            self.monerod.check_readiness()

    def switch_view(self, view_name: str, back=False):
        if self.current_view:
            self.current_view.set_geometry()
            self.current_view.deactivate()
            if not back:
                self.last_views.append(self.current_view)
        
        if not self.views[view_name].activated:
            self.views[view_name].activate()

        self.views[view_name].reactivate()
        self.geometry(self.views[view_name].geometry)

        self.current_view = self.views[view_name]        

    def schedule_payments(self):
        raw_subs = json.loads(cfg.subscriptions())
        for raw_sub in raw_subs:
            sub = Subscription(**raw_sub)
            sub.queue()

    def scheduler_thread(self):
        self.sched_thread = threading.Thread(target=self.run_scheduler)
        self.sched_thread.daemon = True
        self.sched_thread.start()

    def run_scheduler(self):
        while not self.stop_subscriptions:
            Subscription.schedul.run(blocking=False)
            time.sleep(1)

    def destroy(self):
        for key, view in self.views.items():
            view.destroy()
        super().destroy()

    def shutdown_steps(self):
        self.after_cancel(self.process_tx_queue)
        self.after_cancel(self.process_sub_queue)
        self.after_cancel(self.process_qt_events)

        self.empty_tk_queue(self.transactions_queue)
        self.empty_tk_queue(self.subscriptions_queue)

        for event in Subscription.schedul.queue:
            Subscription.schedul.cancel(event)

        self.stop_subscriptions = True
        self.sched_thread.join(timeout=2)

        if rpc() == 'True' and self.rpc_server: # pragma: no cover
            self.rpc_server.kill()

        if hasattr(self, 'tray_icon') and self.tray_icon: # pragma: no cover
            self.tray_icon.hide()
            self.tray_icon.deleteLater()
        self.qt_app.processEvents()
        self.qt_app.quit()
        del self._qt_app

        self.destroy()


    def empty_tk_queue(self, queue):
        while not queue.empty():
            try:
                queue.get_nowait()
                queue.task_done()
            except queue.Empty: # pragma: no cover
                break

    # PyQt5 System Tray Setup
    def create_tray_icon(self): # pragma: no cover
        # Create a 32x32 red square pixmap
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(255, 0, 0))  # Red
        icon = QIcon('assets/icon.ico')

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon(icon, self.qt_app)

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

    def hide_to_tray(self): # pragma: no cover
        # Minimize to tray instead of closing
        self.withdraw()  # Hide the window
        self.tray_icon.show()

    def handle_tray_click(self, reason): # pragma: no cover
        if reason == QSystemTrayIcon.Trigger:
            self.toggle_window()

    def toggle_window(self): # pragma: no cover
        if self.winfo_viewable():
            self.hide_to_tray()
        else:
            self.show_window()

    def show_window(self): # pragma: no cover
        # Restore the window
        self.deiconify()
        self.lift()
        self.focus_force()

    def process_qt_events(self):
        # Process Qt events to keep tray icon responsive
        self.qt_app.processEvents()
        self.after(50, self.process_qt_events)  # Call again after 50ms

    def create_image(self, width, height, color1, color2): # pragma: no cover
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

    def signal_handler(self, sig, frame): # pragma: no cover
        self.shutdown_steps()
        sys.exit(0)

    @property
    def qt_app(self):
        return self._qt_app

#Need to make this work with Windows.
#https://stackoverflow.com/questions/3425294/how-to-detect-the-os-default-language-in-python
if __name__ == "__main__": # pragma: no cover
    locale.setlocale(locale.LC_ALL, environ['LANG'])

    app = App()
    app.title("Monero Subscriptions Wallet")
    app.iconphoto(True, PhotoImage(file=styles.icon))
    app.protocol("WM_DELETE_WINDOW", app.hide_to_tray)
    app.resizable(True, True)  # Make the window resizable
    app.create_tray_icon()

    signal.signal(signal.SIGINT, app.signal_handler)
    signal.signal(signal.SIGTERM, app.signal_handler)

    app.mainloop()
