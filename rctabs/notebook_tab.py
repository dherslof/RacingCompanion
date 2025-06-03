import customtkinter as ctk

class NotebookPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        label = ctk.CTkLabel(self, text="Part inventory list - Coming Soon", font=("Arial", 16))
        label.pack(pady=20)