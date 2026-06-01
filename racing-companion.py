#!/usr/bin/python3
# This file is part of the Racing-Companion project.
#
# Description: Main application for the Racing Companion. 
# License: TBD

import customtkinter as ctk
import tkinter as tk
import signal
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
        self.is_closing = False

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
        self.tab_sessions = self.tab_view.add("Track Days")
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

        # Ensure callbacks are stopped before the root is destroyed.
        self.protocol("WM_DELETE_WINDOW", self.on_app_close)
        self.report_callback_exception = self._report_callback_exception

    # Global methods
    def update_footer(self):
        """Update the footer to display the active vehicle."""
        if self.active_vehicle:
            self.footer_label.configure(text=f"dherslof | Racing Companion | version: {self.app_version} | Active Vehicle: {self.active_vehicle}")
        else:
            self.footer_label.configure(text=f"{self.footer_template_text}")

    def on_app_close(self):
        """Perform deterministic app shutdown to avoid callback races on destroy."""
        if self.is_closing:
            return

        self.is_closing = True

        try:
            # Drain pending idle callbacks before tear-down.
            self.update_idletasks()
        except Exception:
            pass

        try:
            # Release any active modal grab so shutdown cannot be blocked.
            grab_widget = self.grab_current()
            if grab_widget is not None:
                grab_widget.grab_release()
        except Exception:
            pass

        try:
            # Cancel all outstanding Tk 'after' callbacks to prevent them from
            # firing against a destroyed interpreter during shutdown.
            after_ids = self.tk.call("after", "info")
            if isinstance(after_ids, str):
                after_ids = (after_ids,) if after_ids else ()
            for after_id in after_ids:
                try:
                    self.after_cancel(after_id)
                except Exception:
                    pass
        except Exception:
            pass

        try:
            # Destroy outstanding toplevel windows first.
            for child in self.winfo_children():
                if isinstance(child, tk.Toplevel):
                    try:
                        child.destroy()
                    except Exception:
                        pass
        except Exception:
            pass

        try:
            self.quit()
        except Exception:
            pass

        self.destroy()

    def _report_callback_exception(self, exc, val, tb):
        """Ignore known Tk/CTk teardown callback races while closing."""
        if self.is_closing and exc is tk.TclError:
            msg = str(val)
            if "invalid command name" in msg and ("check_dpi_scaling" in msg or "update" in msg):
                return
        super().report_callback_exception(exc, val, tb)

if __name__ == "__main__":
    app = RacingDiaryApp()
    signal.signal(signal.SIGINT, lambda *_: app.on_app_close())
    app.mainloop()