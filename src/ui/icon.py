import pystray
from PIL import Image, ImageDraw

class Icon():
    def __init__(self, hide_callback, show_callback):
        self.name = 'Monero Subscription Wallet'
        self.width = 64
        self.height = 64
        self.color1 = 'black'
        self.color2 = 'white'
        self._menu = None
        self.hide_callback = hide_callback
        self.show_callback = show_callback
        self._icon = self.create()

    def image(self):
        # Generate an image and draw a pattern
        image = Image.new('RGB', (self.width, self.height), self.color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            (self.width // 2, 0, self.width, self.height // 2),
            fill=self.color2)
        dc.rectangle(
            (0, self.height // 2, self.width // 2, self.height),
            fill=self.color2)

        return image

    def create(self):
        return pystray.Icon(self.name, icon=self.image(), menu=self.menu())

    def menu(self):
        if not self._menu:
            self._menu = pystray.Menu(
                pystray.MenuItem('Hide', self.hide_callback),
                pystray.MenuItem('Show', self.show_callback)
            )
        return self._menu

    def stop(self):
        self._icon.stop()

    def thread_run(self):
        self._icon.run()