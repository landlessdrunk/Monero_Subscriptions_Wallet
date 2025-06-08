import customtkinter as ctk
import platform

class MouseScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        getattr(self, f'bind_{platform.system().lower()}')()
        self.bind("<Enter>", lambda event: self.focus_set())

    def bind_linux(self):
        self.bind_all("<Button-4>", lambda event: self.scroll_frame(-1))
        self.bind_all("<Button-5>", lambda event: self.scroll_frame(1))

    def bind_windows(self): #pragma: no cover
        self.bind_all("<MouseWheel>", lambda event: self.scroll_frame(-1 if event.delta > 0 else 1))

    def bind_darwin(self): #pragma: no cover
        self.bind_all("<Button-4>", lambda event: self.scroll_frame(-1))
        self.bind_all("<Button-5>", lambda event: self.scroll_frame(1))
        self.bind_all("<MouseWheel>", lambda event: self.scroll_frame(-1 if event.delta > 0 else 1))

    def scroll_frame(self, direction): #pragma: no cover
        self._parent_canvas.yview_scroll(direction, "units")
