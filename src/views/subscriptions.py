import customtkinter as ctk
from src.interfaces.view import View
import config as cfg
import styles
import json
from PIL import Image
from src.subscription import Subscription
from src.views.mouse_scrollable_frame import MouseScrollableFrame

class SubscriptionsView(View):
    @property
    def geometry(self):
        if not self._geometry:
            self._geometry = styles.SUBSCRIPTIONS_LARGE_VIEW_GEOMETRY
        return self._geometry

    def build(self):
        self.header('Manage Subscriptions:')
        self.back_button()

        # Plus Button
        add_image = ctk.CTkImage(Image.open(styles.plus_icon), size=(24, 24))
        self.add_button = self.add(ctk.CTkButton(self._app, image=add_image, text='', fg_color='transparent', width=35, height=30, command=self.add_subscription))
        self.add_button.grid(row=0, column=2, padx=10, pady=(10, 20), sticky="e")
        self.sub_frame = self.add(SubscriptionsScrollableFrame(master=self._app, corner_radius=0, fg_color="transparent"))

        # TODO: Would be cool to have a little section for "Assuming no price fluctuations, your wallet has enough funds to cover your subscription costs until X date."
        # TODO: There is probably a better way to word this, and we may want to assume a 20% price drop or something to be safe.

        self._app.grid_rowconfigure(1, weight=1)  # Changes this globally. Set back when closing view.

        return self

    def activation(self):
        self._app.subscriptions_queue.put(self.update_subscriptions)
        return self

    def reactivate(self):
        super().reactivate()
        self._app.subscriptions_queue.put(self.update_subscriptions)

    def update_subscriptions(self):
        self.sub_frame.update_subscriptions()

    def add_subscription(self):
        self._app.switch_view('pay')
        # self.master.master.master.switch_view('pay')

    def destroy(self):
        self._app.grid_rowconfigure(1, weight=0)
        super().destroy()


class SubscriptionsScrollableFrame(MouseScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.grid(row=1, column=0, columnspan=3, sticky='nsew')
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.subscriptions = json.loads(cfg.subscriptions())
        self.sub_frames = []
        if self.subscriptions:
            for i, sub in enumerate(self.subscriptions):
                self.sub_frames.append(self._create_subscription(Subscription(**sub), i))
            print('test')
        else:
            no_subs_text = ctk.CTkLabel(self, text="     You haven't added any subscriptions yet.", )
            # no_subs_text.pack(padx=10, pady=(50, 0))
            #TODO: Switch to grid

    def _create_subscription(self, sub, row):
        return SubscriptionFrame(self, sub, row)

    def update_subscriptions(self):
        sub_diff = [Subscription(**sub) for sub in self.subscriptions_diff()]
        self.subscriptions = json.loads(cfg.subscriptions())
        for sub in sub_diff:
            self.sub_frames.append(self._create_subscription(sub, len(self.sub_frames) + 1))
        
        for sub_frame in self.sub_frames:
            if sub_frame.subscription.json_friendly() not in self.subscriptions:
                sub_frame.destroy()
                self.sub_frames.remove(sub_frame)

    def subscriptions_diff(self):
        new_subs = json.loads(cfg.subscriptions())
        current_subs = [sub_frame.subscription.json_friendly() for sub_frame in self.sub_frames]
        diff_subs = []
        for sub in new_subs:
            if not any(sub == cur_sub for cur_sub in current_subs):
                diff_subs.append(sub)
        return diff_subs

class SubscriptionFrame(ctk.CTkFrame):
    def __init__(self, master, sub, row, **kwargs):
        super().__init__(master, **kwargs)
        self.subscription = sub
        # Padding and stuff for each SubscriptionFrame
        self.grid(row=row, column=1, columnspan=3, sticky="nsew", padx=10, pady=(0, 10))

       # Truncated to 50 characters
        self.subscription_name = ctk.CTkLabel(self, text=f'{sub.custom_label[:50]}:', font=styles.SUBHEADING_FONT_SIZE)
        self.subscription_name.grid(row=0, column=1, pady=0, sticky="ns")

        self.subscription_price = ctk.CTkLabel(self, text=f'{sub.amount} {sub.currency}', font=styles.SUBHEADING_FONT_SIZE)
        self.subscription_price.grid(row=1, column=1, pady=0,  sticky="ns")

        # TODO: Make this accurate. Right now it just shows billing cycle
        self.subscription_renews_in = ctk.CTkLabel(self, text=f'Renews At {sub.next_payment_time().strftime('%c')}', font=styles.BODY_FONT_SIZE)
        self.subscription_renews_in.grid(row=2, column=1, pady=0, sticky="ns")

        self.subscription_cancel_button = ctk.CTkButton(self, text="Cancel", corner_radius=15, command=lambda: self.cancel_subscription(sub))
        self.subscription_cancel_button.grid(row=3, column=1, pady=(10, 20))

        # Center the widgets within each column
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)  # Higher weight for the middle column
        self.columnconfigure(2, weight=1)

    def cancel_subscription(self, subscription):
        # cfg.config_file.remove_subscription(subscription)
        # self.destroy()
        cfg.SELECTED_SUBSCRIPTION = subscription
        self.master.master.master.master.switch_view('review_delete')
