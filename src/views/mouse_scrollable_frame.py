import customtkinter as ctk
import platform

class MouseScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind_platform()

    def bind_platform(self):
        system = platform.system().lower()
        if system == "linux":
            self._parent_canvas.bind("<Button-4>", lambda event: self.scroll_frame(-1))
            self._parent_canvas.bind("<Button-5>", lambda event: self.scroll_frame(1))
            self.bind("<Button-4>", lambda event: self.scroll_frame(-1))
            self.bind("<Button-5>", lambda event: self.scroll_frame(1))
        elif system == "windows":
            self._parent_canvas.bind("<MouseWheel>", lambda event: self.scroll_frame(-1 if event.delta > 0 else 1))
            self.bind("<MouseWheel>", lambda event: self.scroll_frame(-1 if event.delta > 0 else 1))
        elif system == "darwin":
            self._parent_canvas.bind("<Button-4>", lambda event: self.scroll_frame(-1))
            self._parent_canvas.bind("<Button-5>", lambda event: self.scroll_frame(1))
            self._parent_canvas.bind("<MouseWheel>", lambda event: self.scroll_frame(-1 if event.delta > 0 else 1))
            self.bind("<Button-4>", lambda event: self.scroll_frame(-1))
            self.bind("<Button-5>", lambda event: self.scroll_frame(1))
            self.bind("<MouseWheel>", lambda event: self.scroll_frame(-1 if event.delta > 0 else 1))

    def scroll_frame(self, direction):
        if hasattr(self, "_parent_canvas"):
            self._parent_canvas.yview_scroll(direction, "units")
            print(f"Scrolling: direction={direction}")

    def unbind_all_events(self):
        self._parent_canvas.unbind("<Button-4>")
        self._parent_canvas.unbind("<Button-5>")
        self._parent_canvas.unbind("<MouseWheel>")
        self.unbind("<Button-4>")
        self.unbind("<Button-5>")
        self.unbind("<MouseWheel>")