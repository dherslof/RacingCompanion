# This file is part of the Racing-Companion project.
#
# Description: Main application for the Racing Companion. 
# License: TBD

import customtkinter as ctk
from rcfunc.data_utils import load_vehicles, load_data, load_maintenance_entries
from rctabs.welcome_tab import WelcomePage
from rctabs.track_sessions_tab import TrackSessionsPage
from rctabs.maintenance_tab import MaintenancePage
from rctabs.notebook_tab import NotebookPage

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class RacingDiaryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Racing Companion")
        self.geometry("850x750")

        self.app_version = "1.0.0"
        self.footer_template_text = f"dherslof | Racing Companion | version: {self.app_version} | Active Vehicle: None"

        # Load data
        self.vehicles, self.vehicle_data = load_vehicles()
        self.track_days = load_data()
        self.maintenance_entries = load_maintenance_entries()

        self.active_vehicle = None
        self.weather_options = ["Sunny", "Cloudy", "Overcast", "Light Rain", "Heavy Rain", "Wet Track", "Mixed Conditions", "drying-up"]

        # Tab view
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabs
        self.tab_welcome = self.tab_view.add("Welcome")
        self.tab_sessions = self.tab_view.add("Track Sessions")
        self.tab_maintenance = self.tab_view.add("Maintenance Log")
        self.tab_part_inventory = self.tab_view.add("Notebook")

        # Footer frame
        self.footer_frame = ctk.CTkFrame(self, fg_color="#D0D3D4", height=40)
        self.footer_frame.pack(side="bottom", fill="x")
        self.footer_label = ctk.CTkLabel(self.footer_frame, text=f"{self.footer_template_text}", font=("Arial", 14, "bold"))
        self.footer_label.pack(pady=5)

        # Add page frames to tabs
        self.welcome_page = WelcomePage(self.tab_welcome, self)
        self.welcome_page.pack(fill="both", expand=True)

        self.sessions_page = TrackSessionsPage(self.tab_sessions, self)
        self.sessions_page.pack(fill="both", expand=True)

        self.maintenance_page = MaintenancePage(self.tab_maintenance, self)
        self.maintenance_page.pack(fill="both", expand=True)

        self.notebook_page = NotebookPage(self.tab_part_inventory, self)
        self.notebook_page.pack(fill="both", expand=True)

    # Global methods
    def update_footer(self):
        """Update the footer to display the active vehicle."""
        if self.active_vehicle:
            self.footer_label.configure(text=f"dherslof | Racing Companion | version: {self.app_version} | Active Vehicle: {self.active_vehicle}")
        else:
            self.footer_label.configure(text=f"{self.footer_template_text}")

if __name__ == "__main__":
    app = RacingDiaryApp()
    app.mainloop()