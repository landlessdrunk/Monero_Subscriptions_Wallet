import customtkinter as ctk
from tkinter import Event
from src.views.mouse_scrollable_frame import MouseScrollableFrame

class SearchableDropdown(ctk.CTkFrame):
    def __init__(self, master, options, width=200, height=30, **kwargs):
        self.command = kwargs.pop("command", None)
        self.variable = kwargs.pop("variable", None)
        super().__init__(master, **kwargs)
        self.options = options
        self.filtered_options = options[:]
        self.dropdown_visible = False
        self.hide_timer = None
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # Entry for input/search
        self.entry = ctk.CTkEntry(
            self,
            width=width,
            height=height,
            placeholder_text="Search options...",
            textvariable=self.variable
        )
        self.entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.entry.bind("<KeyRelease>", self.on_key_release)
        self.entry.bind("<FocusIn>", self.show_dropdown)

        # Scrollable frame for dropdown
        self.dropdown_frame = MouseScrollableFrame(
            self,
            width=width,
            height=150,  # Adjust based on expected results
        )
        # Initially populate (hidden)
        self.update_dropdown()

    def on_key_release(self, event: Event):
        query = self.entry.get().lower()
        if query:
            self.filtered_options = [opt for opt in self.options if query in opt.lower()]
        else:
            self.filtered_options = self.options[:]
        self.update_dropdown()
        self.show_dropdown()

    def update_dropdown(self):
        # Clear existing labels
        for widget in self.dropdown_frame.winfo_children():
            widget.destroy()

        # Add filtered options as clickable labels
        for i, option in enumerate(self.filtered_options[:20]):  # Limit to 20 for performance
            label = ctk.CTkLabel(
                self.dropdown_frame,
                text=option,
                anchor="w",
                width=200
            )
            label.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            label.bind("<Button-1>", lambda e, opt=option: self.select_option(opt))
        self.dropdown_frame._parent_canvas.configure(scrollregion=self.dropdown_frame._parent_canvas.bbox("all"))

    def show_dropdown(self, event=None):
        if self.hide_timer:
            self.after_cancel(self.hide_timer)
        self.dropdown_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.dropdown_visible = True
        self.dropdown_frame.bind_platform()
        self.dropdown_frame._parent_canvas.configure(scrollregion=self.dropdown_frame._parent_canvas.bbox("all"))

    def hide_dropdown(self):
        self.dropdown_frame.grid_forget()
        self.dropdown_visible = False

    def select_option(self, option):
        self.entry.delete(0, "end")
        self.entry.insert(0, option)
        self.hide_dropdown()
        self.command(option)  # Call the command with the selected option
        print(f"Selected: {option}")