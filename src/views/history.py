import logging
import customtkinter as ctk
from src.interfaces.view import View
import styles
from src.logging import config as logging_config
from src.clients.rpc import RPCClient
from src.transaction import Transaction
from src.exchange import Exchange
from src.wallet import Wallet
from src.rpc_server import RPCServer
from src.observers.rpc_readiness_observer import RPCReadinessObserver
from src.views.mouse_scrollable_frame import MouseScrollableFrame
from monero_usd_price import calculate_monero_from_atomic_units

class HistoryView(View):
    def __init__(self, app):
        super().__init__(app)
        self._tx_thread = None

    @property
    def geometry(self):
        if not self._geometry:
            self._geometry = styles.HISTORY_LARGE_VIEW_GEOMETRY
        return self._geometry

    def build(self):
        # Back button and title
        # styles.back_and_title(self, ctk, cfg, title='Transaction History:', pad_bottom=10)

        self.header('Transaction History:')
        self.back_button()

        # Plus Button
        #add_image = ctk.CTkImage(Image.open(styles.plus_icon), size=(24, 24))
        #add_button = self.add(ctk.CTkButton(self._app, image=add_image, text='', fg_color='transparent', width=35, height=30, corner_radius=7, command=self.add_subscription))
        #add_button.grid(row=0, column=2, padx=10, pady=(10, 20), sticky="e")

        #TODO: This doesn't work as intended because the RPC Wallet server has yet to properly be started.
        self.transactions_frame = self.add(TransactionsScrollableFrame(master=self._app, corner_radius=0, fg_color="transparent"))
        rpc_server = RPCServer.get(Wallet())
        rpc_server.attach(RPCReadinessObserver(self.transactions_frame))
        self._app.grid_rowconfigure(1, weight=1)  # Changes this globally. Set back when closing view.
        return self

    def activation(self):
        #TODO: Update this to update transactions periodically like the scrollable frame does.
        # if len(self.TRANSACTIONS) > 4:
        #     self._app.geometry(styles.center_window_x(self._app, styles.HISTORY_LARGE_VIEW_GEOMETRY))
        #     #self._app.geometry(styles.HISTORY_LARGE_VIEW_GEOMETRY)
        # else:
        #     self._app.geometry(styles.HISTORY_SMALL_VIEW_GEOMETRY)
        return self

    def destroy(self):
        self._app.grid_rowconfigure(1, weight=0)
        self._tx_thread = None
        super().destroy()

class TransactionsScrollableFrame(MouseScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self._app = master
        logging.config.dictConfig(logging_config)
        self.logger = logging.getLogger(self.__module__)
        self.grid(row=1, column=0, columnspan=3, sticky='nsew')
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.schedule_tx_update()
        self.transactions = None
        self.transaction_frames = []
        self._observers = []

    def _add_tx(self, tx, row):
        self.transaction_frames.append(TransactionFrame(self, tx, row))

    def schedule_tx_update(self):
        self._app.transactions_queue.put(self.update_txs)

    def render_txs(self):
        if self.transactions:
            for direction, txs in self.transactions.items():
                txs.sort(reverse=True, key=lambda t: t['timestamp'])
                for i, tx in enumerate(txs):
                    try:
                        transaction = Transaction(**tx, direction=direction)
                        self._add_tx(transaction, i)
                    except (TypeError, UnboundLocalError, RuntimeError) as e: # pragma: no cover
                        self.logger.debug(str(e))
        else:
            self.no_tx_text = ctk.CTkLabel(self, text="No transactions yet.")
            self.no_tx_text.grid(row=1, column=1, padx=10, pady=(50, 0))


    def update_txs(self):
        self.logger.debug('Updating Transactions')
        new_transactions = RPCClient.get().get_transfers()
        #TODO: How to handle pending transactions? Pending transfers aren't included
        diff_transactions = {
            'in': [],
            'out': [],
            'pending': []
        }
        old_tx_ids = {'in': [], 'out': [], 'pending': []}
        if self.transactions:
            for new_dir, new_txs in new_transactions.items():
                for new_tx in new_txs:
                    for old_dir, old_txs in self.transactions.items():
                        for old_tx in old_txs:
                            if not old_tx_ids.get(old_dir):
                                old_tx_ids[old_dir] = []
                            old_tx_ids[old_dir].append(old_tx['txid'])
                    if new_tx['txid'] not in old_tx_ids[new_dir]:
                        diff_transactions[new_dir].append(new_tx)
        elif new_transactions:
            diff_transactions = new_transactions

        if getattr(self, 'no_tx_text', None) and any([diff for diffs in diff_transactions.values() for diff in diffs]):
            self.no_tx_text.destroy()
            self.no_tx_text = None

        for direction, txs in diff_transactions.items():
            txs.sort(reverse=True, key=lambda t: t['timestamp'])
            for i, tx in enumerate(txs):
                try:
                    transaction = Transaction(**tx, direction=direction)
                    self._add_tx(transaction, i+len(old_tx_ids[direction]))
                except (TypeError, UnboundLocalError, RuntimeError) as e: # pragma: no cover
                    self.logger.debug(str(e))
        self.transactions = new_transactions
        self.schedule_tx_update()

class TransactionFrame(ctk.CTkFrame):
    def __init__(self, master, tx, row, **kwargs):
        super().__init__(master, **kwargs)

        # Padding and stuff for each TransactionFrame
        self.grid(row=row, column=1, columnspan=3, sticky="nsew", padx=(10, 0), pady=(0, 10))

        # Configure the main window grid for spacing and alignment
        self.columnconfigure(1, weight=1)

        symbol = "+" if tx.direction == "in" else "-"
        sub_text = Exchange.convert(tx.subscription()['currency'], calculate_monero_from_atomic_units(tx.amt())) if tx.subscription() else None
        no_sub_text = calculate_monero_from_atomic_units(tx.amt())
        currency_text = tx.subscription()['currency'] if tx.subscription() else 'XMR'
        amount_text = f"{symbol} {sub_text if tx.subscription() else no_sub_text} {currency_text}"
        payment_name_text = tx.notes() or (tx.payment_id[:49] + "…" if len(tx.payment_id) >= 50 else tx.payment_id)

        date_text = f"On {tx.time()}"

        text_color = styles.green if tx.direction == "in" else styles.red  # TODO: update colors

        self.payment_name = ctk.CTkLabel(self, text=payment_name_text, font=styles.TX_NAME_FONT_SIZE, text_color=styles.monero_orange)  # TODO: UPDATE THIS
        self.payment_name.grid(row=0, column=0, padx=10, pady=0, sticky="w")

        self.date = ctk.CTkLabel(self, text=date_text, font=styles.TX_DATE_FONT_SIZE, text_color='grey')
        self.date.grid(row=1, column=0, padx=(10, 0), pady=(0, 20), sticky="w")

        self.amount = ctk.CTkLabel(self, text=amount_text, font=styles.TX_AMOUNT_FONT_SIZE, text_color=text_color)
        self.amount.grid(row=0, column=2, padx=(0, 10), pady=0, sticky="e")

        # Center the widgets within each column
        #self.columnconfigure(0, weight=1)
