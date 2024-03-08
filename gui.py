import customtkinter as ctk

from src.rpc_server import RPCServer
from src.views import MainView, ReceiveView, PayView, SubscriptionsView, SettingsView

ctk.set_default_color_theme("monero_theme.json")

# VARIABLES TO MOVE TO CONFIG
CURRENCY_OPTIONS = ["USD", "XMR", "BTC", "EUR", "GBP"]  # Is there a library for pulling these in automatically?'

# TODO: Get this from the config file first. If not present, use what is currently set below.
DEFAULT_CURRENCY = CURRENCY_OPTIONS[0]
SECONDARY_CURRENCY = CURRENCY_OPTIONS[1]

class App(ctk.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("500x195")
        # 3 columns 2 rows

        # Configure the main window grid for spacing and alignment
        self.columnconfigure([0, 1, 2], weight=1)

        # Define what the views are
        self.views = {
            'main': MainView(self),
            'recieve': ReceiveView(self),
            'pay': PayView(self),
            'subscriptions': SubscriptionsView(self),
            'settings': SettingsView(self)
        }

        self.current_view = self.views['main'].build()
        self.rpc_server = RPCServer.get()
        self.rpc_server.start()
        self.rpc_server.check_readiness()

    def switch_view(self, view_name: str):
        self.current_view.destroy()
        self.current_view = self.views[view_name]
        self.current_view.build()

    def shutdown_steps(self):
        self.destroy()
        self.rpc_server.kill()

app = App()
app.protocol("WM_DELETE_WINDOW", app.shutdown_steps)
app.mainloop()