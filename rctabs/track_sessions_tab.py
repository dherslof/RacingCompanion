import os
import customtkinter as ctk
import tkinter.filedialog as fd
import matplotlib.pyplot as plt
import numpy as np
import rcfunc.gui_utils as gui_utils

from tkinter import StringVar
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from rcfunc.data_utils import save_data
from rcfunc.track_session_mngr import TrackSessionMngr
from rcfunc.track_day_report_mngr import TrackDayReportMngr
from rcfunc.track_day_stats_mngr import TrackDayStatsMngr

# TODO: List of todos:
# - Use GUI utils for scrolling instead

class TrackSessionsPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.session_content_frames = {}

        # TrackSessionMngr for all track day/session logic
        self.track_session_mngr = TrackSessionMngr(
            track_days=self.app.track_days,
            vehicles=self.app.vehicles,
            active_vehicle=self.app.active_vehicle,
            weather_options=self.app.weather_options,
            save_callback=save_data
        )

        # TrackDayReportMngr for all track day report logic
        self.track_day_report_mngr = TrackDayReportMngr(self.app.track_days, self.app.vehicles)

        # TrackDayStatsMngr for all track day statistics and analytics
        self.track_day_stats_mngr = TrackDayStatsMngr(
            track_days=self.app.track_days,
            vehicles=self.app.vehicles,
            active_vehicle=self.app.active_vehicle
        )

        self.current_view = "list"
        self.setup_track_sessions_page()

    def setup_track_sessions_page(self):
        """Track session logging with card-style design."""

        # Header frame
        self.track_sessions_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.track_sessions_header_frame.pack(fill="x", padx=20, pady=(20, 10))

        # Title label (optional, similar to maintenance tab)
        self.track_sessions_title_label = ctk.CTkLabel(
           self.track_sessions_header_frame,
           text="Track Days",
           font=ctk.CTkFont(size=24, weight="bold")
        )
        self.track_sessions_title_label.pack(side="left")

        # View selector: List View / Statistics
        self.track_view_selector = ctk.CTkSegmentedButton(
           self.track_sessions_header_frame,
           values=["List View", "Statistics"],
           command=self.switch_track_view
        )
        self.track_view_selector.pack(side="left", padx=(20, 0))
        self.track_view_selector.set("List View")

        # New session button
        self.new_session_button = ctk.CTkButton(
           self.track_sessions_header_frame,
           text="+ Create New Track Day",
           command=self.create_new_track_day,
           text_color="white"
        )
        self.new_session_button.pack(side="right", padx=(10, 0))

        self.report_button = ctk.CTkButton(
           self.track_sessions_header_frame,
           text="Report",
           fg_color="#6C7A89",
           hover_color="#34495E",
           text_color="white",
           command=self.open_track_day_report_dialog
        )
        self.report_button.pack(side="right", padx=(10, 0))

        # List view frame
        self.session_frame = ctk.CTkScrollableFrame(self)
        self.session_frame.pack(fill="both", expand=True, padx=10, pady=10)
        gui_utils.enable_mousewheel_scrolling(self.session_frame)

        # Statistics view frame
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._create_stats_view()

        self.display_track_days()

    def _create_stats_view(self):
        """Create the statistics view with tabs and charts."""
        self.stats_tabs = ctk.CTkTabview(self.stats_frame)
        self.stats_tabs.pack(fill="both", expand=True, padx=20, pady=20)
        self.stats_tabs.add("Track Frequency")
        self.stats_tabs.add("Performance Metrics")
        self.stats_tabs.add("Vehicle Activity")
        self.stats_tabs.add("Weather Distribution")

        # Track Frequency chart
        freq_frame = ctk.CTkFrame(self.stats_tabs.tab("Track Frequency"), fg_color="transparent")
        freq_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.freq_fig, self.freq_ax = plt.subplots(figsize=(10, 6))
        self.freq_canvas = FigureCanvasTkAgg(self.freq_fig, master=freq_frame)
        self.freq_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Performance Metrics chart
        perf_frame = ctk.CTkFrame(self.stats_tabs.tab("Performance Metrics"), fg_color="transparent")
        perf_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.perf_fig, self.perf_ax = plt.subplots(figsize=(10, 6))
        self.perf_canvas = FigureCanvasTkAgg(self.perf_fig, master=perf_frame)
        self.perf_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Vehicle Activity chart
        veh_frame = ctk.CTkFrame(self.stats_tabs.tab("Vehicle Activity"), fg_color="transparent")
        veh_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.veh_fig, self.veh_ax = plt.subplots(figsize=(10, 6))
        self.veh_canvas = FigureCanvasTkAgg(self.veh_fig, master=veh_frame)
        self.veh_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Weather Distribution chart
        weather_frame = ctk.CTkFrame(self.stats_tabs.tab("Weather Distribution"), fg_color="transparent")
        weather_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.weather_fig, self.weather_ax = plt.subplots(figsize=(10, 6))
        self.weather_canvas = FigureCanvasTkAgg(self.weather_fig, master=weather_frame)
        self.weather_canvas.get_tk_widget().pack(fill="both", expand=True)

    def switch_track_view(self, view):
        """Switch between list view and statistics view."""
        self.current_view = view.lower().replace(" ", "_")
        if self.current_view == "list_view":
            self.stats_frame.pack_forget()
            self.session_frame.pack(fill="both", expand=True, padx=10, pady=10)
            self.display_track_days()
        else:
            self.session_frame.pack_forget()
            self.stats_frame.pack(fill="both", expand=True)
            self.update_track_statistics()

    def update_track_statistics(self):
        """Update all track statistics charts."""
        self._update_track_frequency_chart()
        self._update_performance_metrics_chart()
        self._update_vehicle_activity_chart()
        self._update_weather_distribution_chart()

    def _update_track_frequency_chart(self):
        """Update the track frequency chart."""
        self.freq_ax.clear()
        chart_data = self.track_day_stats_mngr.get_chart_data(
            "track_frequency",
            vehicle=self.app.active_vehicle
        )
        if chart_data.get("labels"):
            self.freq_ax.bar(chart_data["labels"], chart_data["values"], color="#3498DB")
            self.freq_ax.set_title(chart_data["title"], fontsize=14, fontweight="bold")
            self.freq_ax.set_xlabel(chart_data["xlabel"])
            self.freq_ax.set_ylabel(chart_data["ylabel"])
            self.freq_ax.tick_params(axis="x", rotation=45)
        self.freq_fig.tight_layout()
        self.freq_canvas.draw()

    def _update_performance_metrics_chart(self):
        """Update the performance metrics chart."""
        self.perf_ax.clear()
        chart_data = self.track_day_stats_mngr.get_chart_data(
            "performance_metrics",
            vehicle=self.app.active_vehicle
        )
        if chart_data.get("labels"):
            x = np.arange(len(chart_data["labels"]))
            width = 0.35
            self.perf_ax.bar(
                x - width / 2,
                chart_data["avg_laps"],
                width,
                label="Avg Laps",
                color="#2ECC71"
            )
            self.perf_ax.bar(
                x + width / 2,
                chart_data["avg_sessions"],
                width,
                label="Avg Sessions",
                color="#E74C3C"
            )
            self.perf_ax.set_title(chart_data["title"], fontsize=14, fontweight="bold")
            self.perf_ax.set_xticks(x)
            self.perf_ax.set_xticklabels(chart_data["labels"])
            self.perf_ax.set_ylabel(chart_data["ylabel"])
            self.perf_ax.legend()
        self.perf_fig.tight_layout()
        self.perf_canvas.draw()

    def _update_vehicle_activity_chart(self):
        """Update the vehicle activity chart."""
        self.veh_ax.clear()
        chart_data = self.track_day_stats_mngr.get_chart_data(
            "vehicle_activity",
            vehicle=self.app.active_vehicle
        )
        if chart_data.get("vehicle_names"):
            x = np.arange(len(chart_data["vehicle_names"]))
            width = 0.35
            self.veh_ax.bar(
                x - width / 2,
                chart_data["days_count"],
                width,
                label="Track Days",
                color="#9B59B6"
            )
            self.veh_ax.bar(
                x + width / 2,
                chart_data["sessions_count"],
                width,
                label="Sessions",
                color="#F39C12"
            )
            self.veh_ax.set_title(chart_data["title"], fontsize=14, fontweight="bold")
            self.veh_ax.set_xticks(x)
            self.veh_ax.set_xticklabels(chart_data["vehicle_names"])
            self.veh_ax.set_ylabel("Count")
            self.veh_ax.legend()
        self.veh_fig.tight_layout()
        self.veh_canvas.draw()

    def _update_weather_distribution_chart(self):
        """Update the weather distribution pie chart."""
        self.weather_ax.clear()
        chart_data = self.track_day_stats_mngr.get_chart_data(
            "weather_distribution",
            vehicle=self.app.active_vehicle
        )
        if chart_data.get("labels"):
            self.weather_ax.pie(
                chart_data["values"],
                labels=chart_data["labels"],
                autopct="%1.1f%%",
                startangle=90,
                colors=plt.cm.Set3.colors
            )
            self.weather_ax.set_title(chart_data["title"], fontsize=14, fontweight="bold")
        self.weather_fig.tight_layout()
        self.weather_canvas.draw()

    def display_track_days(self):
        """Display stored track days as expandable cards."""
        for widget in self.session_frame.winfo_children():
            widget.destroy()

        # Always use up-to-date data from app and update managers
        self.track_session_mngr.update_data_references(
            self.app.track_days, self.app.vehicles, self.app.active_vehicle
        )
        self.track_day_stats_mngr.update_data_references(
            self.app.track_days, self.app.vehicles, self.app.active_vehicle
        )

        filtered_track_days = self.track_session_mngr.get_filtered_track_days()

        if not filtered_track_days:
            no_track_days_label = ctk.CTkLabel(
                self.session_frame,
                text="No track days available for the selected vehicle.",
                font=("Arial", 14),
                text_color="gray"
            )
            no_track_days_label.pack(pady=20)
            return

        # Reverse the order of track days to show the most recent first. New variable to not break original index.
        reversed_track_day_list = list(reversed(filtered_track_days))
        for idx, track_day in enumerate(reversed_track_day_list):
            orig_idx = len(filtered_track_days) - 1 - idx  # Original index in the unfiltered list
            card = ctk.CTkFrame(self.session_frame, corner_radius=10, border_width=1)
            card.pack(fill="x", pady=5, padx=10)

            header_frame = ctk.CTkFrame(card, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=5)

            title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            title_frame.pack(side="left", fill="x", expand=True)

            title = ctk.CTkLabel(title_frame, text=f"{track_day['track']} - {track_day['date']}",
                               font=("Arial", 16, "bold"))
            title.pack(side="top", anchor="w")

            organizer = ctk.CTkLabel(title_frame, text=f"Organizer: {track_day['organizer']}")
            organizer.pack(side="top", anchor="w")

            vehicle_label = ctk.CTkLabel(title_frame, text=f"Vehicle: {track_day.get('vehicle', 'N/A')}")
            vehicle_label.pack(side="top", anchor="w")

            buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            buttons_frame.pack(side="right", padx=10)

            delete_button = ctk.CTkButton(buttons_frame, text="Delete",
                                       width=80, height=32,
                                       command=lambda i=orig_idx: self.delete_track_day(i),
                                       fg_color="#E74C3C",
                                       hover_color="#C0392B")
            delete_button.pack(side="left", padx=5)

            toggle_button = ctk.CTkButton(buttons_frame, text="View Sessions",
                                        width=120, height=32,
                                        command=lambda i=orig_idx, c=card: self.toggle_sessions_inline(i, c))
            toggle_button.pack(side="left", padx=5)

            content_frame = ctk.CTkFrame(card, fg_color="transparent")
            content_frame.pack(fill="x", padx=10, pady=(0, 10), expand=False)

            self.session_content_frames[orig_idx] = {
                "frame": content_frame,
                "button": toggle_button,
                "visible": False
            }
            content_frame.pack_forget()

    def delete_track_day(self, filtered_idx):
        """Delete a track day with confirmation."""
        filtered_track_days = self.track_session_mngr.get_filtered_track_days()
        if not (0 <= filtered_idx < len(filtered_track_days)):
            return
        track_day = filtered_track_days[filtered_idx]

        dialog = ctk.CTkToplevel(self.app)
        dialog.title("Confirm Delete")
        dialog.geometry("450x200")
        dialog.transient(self.app)
        dialog.update_idletasks()
        dialog.grab_set()

        container = ctk.CTkFrame(dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        msg = ctk.CTkLabel(container,
                            text=f"Are you sure you want to delete the track day at {track_day['track']} on {track_day['date']}?\n\nThis will delete ALL sessions from this track day.",
                            wraplength=400,
                            font=("Arial", 14))
        msg.pack(pady=20)

        buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)

        cancel_btn = ctk.CTkButton(buttons_frame,
                                    text="Cancel",
                                    command=dialog.destroy,
                                    fg_color="#7F8C8D",
                                    hover_color="#5D6D7E",
                                    width=100)
        cancel_btn.pack(side="left", padx=5)

        def confirm_delete():
            self.track_session_mngr.delete_track_day(filtered_idx)
            # Rebuild content frames since indices may have changed
            self.session_content_frames = {}
            self.display_track_days()
            dialog.destroy()

        delete_btn = ctk.CTkButton(buttons_frame,
                                    text="Delete",
                                    command=confirm_delete,
                                    fg_color="#E74C3C",
                                    hover_color="#C0392B",
                                    width=100)
        delete_btn.pack(side="right", padx=5)

        dialog.grab_set()
        dialog.wait_window()

    def toggle_sessions_inline(self, idx, card):
        content_data = self.session_content_frames[idx]
        content_frame = content_data["frame"]
        toggle_button = content_data["button"]

        is_visible = content_data["visible"]
        content_data["visible"] = not is_visible

        if is_visible:
            content_frame.pack_forget()
            toggle_button.configure(text="View Sessions", fg_color="#1F6AA5", hover_color="#144870")
        else:
            for widget in content_frame.winfo_children():
                widget.destroy()
            divider = ctk.CTkFrame(content_frame, height=1, fg_color="#D0D3D4")
            divider.pack(fill="x", pady=5)
            # Use manager to get sessions for the filtered track day
            filtered_track_days = self.track_session_mngr.get_filtered_track_days()
            if 0 <= idx < len(filtered_track_days):
                self.display_sessions_inline(filtered_track_days[idx], content_frame, idx)
            content_frame.pack(fill="x", padx=10, pady=(0, 10), expand=True)
            toggle_button.configure(text="Hide Sessions", fg_color="#E67E22", hover_color="#D35400")

    def display_sessions_inline(self, track_day, parent_frame, track_day_idx):
        if not track_day['sessions']:
            empty_label = ctk.CTkLabel(parent_frame, text="No sessions recorded yet",
                                    text_color="gray")
            empty_label.pack(pady=10)
        else:
            table_container = ctk.CTkFrame(parent_frame, fg_color="transparent", corner_radius=0)
            table_container.pack(fill="x", pady=5)

            table_container.columnconfigure(0, weight=1)
            table_container.columnconfigure(1, weight=1)
            table_container.columnconfigure(2, weight=2)
            table_container.columnconfigure(3, weight=2)
            table_container.columnconfigure(4, weight=2)
            table_container.columnconfigure(5, weight=2)

            header_frame = ctk.CTkFrame(table_container, fg_color="#B8C9D6", corner_radius=0)
            header_frame.grid(row=0, column=0, columnspan=6, sticky="ew")

            header_frame.columnconfigure(0, weight=1)
            header_frame.columnconfigure(1, weight=1)
            header_frame.columnconfigure(2, weight=2)
            header_frame.columnconfigure(3, weight=2)
            header_frame.columnconfigure(4, weight=2)
            header_frame.columnconfigure(5, weight=2)

            ctk.CTkLabel(header_frame, text="Session #", font=("Arial", 11, "bold"),
                    text_color="#2C3E50", fg_color="transparent").grid(row=0, column=0, padx=10, pady=3, sticky="w")
            ctk.CTkLabel(header_frame, text="Laps", font=("Arial", 11, "bold"),
                    text_color="#2C3E50", fg_color="transparent").grid(row=0, column=1, padx=10, pady=3, sticky="w")
            ctk.CTkLabel(header_frame, text="Vehicle", font=("Arial", 11, "bold"),
                    text_color="#2C3E50", fg_color="transparent").grid(row=0, column=2, padx=10, pady=3, sticky="w")
            ctk.CTkLabel(header_frame, text="Weather", font=("Arial", 11, "bold"),
                    text_color="#2C3E50", fg_color="transparent").grid(row=0, column=3, padx=10, pady=3, sticky="w")
            ctk.CTkLabel(header_frame, text="Tire Info", font=("Arial", 11, "bold"),
                    text_color="#2C3E50", fg_color="transparent").grid(row=0, column=4, padx=10, pady=3, sticky="w")
            ctk.CTkLabel(header_frame, text="Best Lap", font=("Arial", 11, "bold"),
                    text_color="#2C3E50", fg_color="transparent").grid(row=0, column=5, padx=10, pady=3, sticky="w")

            for i, session in enumerate(track_day['sessions']):
                row_index = i + 1
                row_color = "#F5F7FA" if i % 2 == 0 else "#EBEEF2"
                row_frame = ctk.CTkFrame(table_container, fg_color=row_color, corner_radius=0)
                row_frame.grid(row=row_index, column=0, columnspan=6, sticky="ew")

                row_frame.columnconfigure(0, weight=1)
                row_frame.columnconfigure(1, weight=1)
                row_frame.columnconfigure(2, weight=2)
                row_frame.columnconfigure(3, weight=2)
                row_frame.columnconfigure(4, weight=2)
                row_frame.columnconfigure(5, weight=2)

                session_num = ctk.CTkLabel(row_frame, text=f"#{session.get('session_number', 'N/A')}",
                                        font=("Arial", 11), fg_color="transparent")
                session_num.grid(row=0, column=0, padx=20, pady=3, sticky="w")

                laps_label = ctk.CTkLabel(row_frame, text=f"{session.get('laps', 'N/A')}",
                                        font=("Arial", 11), fg_color="transparent")
                laps_label.grid(row=0, column=1, padx=10, pady=3, sticky="w")

                vehicle_label = ctk.CTkLabel(row_frame, text=f"{session.get('vehicle', 'N/A')}",
                                        font=("Arial", 11), fg_color="transparent")
                vehicle_label.grid(row=0, column=2, padx=10, pady=3, sticky="w")

                weather_label = ctk.CTkLabel(row_frame, text=f"{session.get('weather', 'N/A')}",
                                        font=("Arial", 11), fg_color="transparent")
                weather_label.grid(row=0, column=3, padx=10, pady=3, sticky="w")

                tire_type = session.get('tire_type', 'N/A')
                tire_status = session.get('tire_status', 'N/A')
                tire_label = ctk.CTkLabel(row_frame, text=f"{tire_type} | {tire_status}",
                                        font=("Arial", 11), fg_color="transparent")
                tire_label.grid(row=0, column=4, padx=10, pady=3, sticky="w")

                best_lap = ctk.CTkLabel(row_frame, text=session.get('best_lap_time', 'N/A'),
                                    font=("Arial", 11, "bold"), fg_color="transparent")
                best_lap.grid(row=0, column=5, padx=10, pady=3, sticky="w")

                def on_enter(event, w=row_frame):
                    w.configure(fg_color="#FAE7A5")
                def on_leave(event, w=row_frame, c=row_color):
                    w.configure(fg_color=c)
                row_frame.bind("<Enter>", on_enter)
                row_frame.bind("<Leave>", on_leave)
                row_frame.bind("<Button-3>", lambda event, s=session, idx=track_day_idx: self.show_session_context_menu(event, s, idx))

        add_button_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        add_button_frame.pack(fill="x", pady=5)

        session_numbers = [session.get("session_number", f"Session {i+1}") for i, session in enumerate(track_day['sessions'])]
        self.modify_session_var = StringVar(value=session_numbers[0] if session_numbers else "No Sessions")
        modify_session_dropdown = ctk.CTkOptionMenu(
            add_button_frame,
            values=session_numbers,
            variable=self.modify_session_var,
            width=150,
            fg_color="#F5F7FA",
            button_color="#D0D3D4",
            button_hover_color="#B3B6B7",
            dropdown_fg_color="#F5F7FA",
            text_color="#2C3E50"
        )
        modify_session_dropdown.pack(side="left", padx=5)

        modify_button = ctk.CTkButton(
            add_button_frame,
            text="Modify Session",
            command=lambda: self.modify_session_form(track_day_idx, self.modify_session_var.get()),
            fg_color="#6C7A89",
            width=150,
            height=32
        )
        modify_button.pack(side="left", padx=5)

        export_button = ctk.CTkButton(
            add_button_frame,
            text="Export",
            fg_color="#6C7A89",
            width=170,
            height=32,
            command=lambda: self.open_export_track_day_form(track_day_idx)
        )
        export_button.pack(side="left", padx=5)

        add_session_button = ctk.CTkButton(add_button_frame, text="+ Add Session",
                                        width=150, height=32,
                                        command=lambda: self.add_session_form(track_day_idx),
                                        fg_color="#2ECC71",
                                        hover_color="#27AE60",
                                        text_color="white",)
        add_session_button.pack(side="right", padx=5, pady=5)

    def modify_session_form(self, track_day_idx, session_number):
        filtered_track_days = self.track_session_mngr.get_filtered_track_days()
        if not (0 <= track_day_idx < len(filtered_track_days)):
            return
        track_day = filtered_track_days[track_day_idx]
        session = next((s for s in track_day["sessions"] if s.get("session_number") == session_number), None)
        if not session:
            return

        self.session_form_window = ctk.CTkToplevel(self)
        self.session_form_window.title("Modify Session")
        self.session_form_window.geometry("550x950")
        self.session_form_window.transient(self)
        self.session_form_window.update_idletasks()

        form_frame = ctk.CTkFrame(self.session_form_window)
        form_frame.pack(fill="both", expand=True, padx=30, pady=30)

        field_pady = 10

        ctk.CTkLabel(form_frame, text="Number of Laps:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
        self.laps_entry = ctk.CTkEntry(form_frame, width=450, height=35)
        self.laps_entry.insert(0, session.get("laps", ""))
        self.laps_entry.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(form_frame, text="Weather:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
        self.weather_var = StringVar(value=session.get("weather", self.track_session_mngr.weather_options[0]))
        self.weather_dropdown = ctk.CTkOptionMenu(
            form_frame,
            values=self.track_session_mngr.weather_options,
            variable=self.weather_var,
            width=450,
            height=35,
            dynamic_resizing=True,
            fg_color="#F5F7FA",
            button_color="#D0D3D4",
            button_hover_color="#B3B6B7",
            dropdown_fg_color="#F5F7FA",
            text_color="#2C3E50"
        )
        self.weather_dropdown.pack(fill="x", pady=(0, field_pady))

        ctk.CTkLabel(form_frame, text="Tire Type:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
        self.tire_type_entry = ctk.CTkEntry(
            form_frame,
            width=450,
            height=35,
            fg_color="#F5F7FA",
            border_color="#D0D3D4",
            text_color="#2C3E50")
        self.tire_type_entry.insert(0, session.get("tire_type", ""))
        self.tire_type_entry.pack(fill="x", pady=(0, field_pady))

        ctk.CTkLabel(form_frame, text="Tire Status:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
        self.tire_status_entry = ctk.CTkEntry(
            form_frame,
            width=450,
            height=35,
            fg_color="#F5F7FA",
            border_color="#D0D3D4",
            text_color="#2C3E50")
        self.tire_status_entry.insert(0, session.get("tire_status", ""))
        self.tire_status_entry.pack(fill="x", pady=(0, field_pady))

        ctk.CTkLabel(form_frame, text="Best Lap Time:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
        self.best_lap_time_entry = ctk.CTkEntry(
            form_frame,
            width=450,
            height=35,
            fg_color="#F5F7FA",
            border_color="#D0D3D4",
            text_color="#2C3E50")
        self.best_lap_time_entry.insert(0, session.get("best_lap_time", ""))
        self.best_lap_time_entry.pack(fill="x", pady=(0, field_pady))

        ctk.CTkLabel(form_frame, text="Comments:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
        self.comments_entry = ctk.CTkEntry(
            form_frame,
            width=450,
            height=120,
            fg_color="#F5F7FA",
            border_color="#D0D3D4",
            text_color="#2C3E50")
        self.comments_entry.insert(0, session.get("comments", ""))
        self.comments_entry.pack(fill="x", pady=(0, field_pady))

        save_button = ctk.CTkButton(
            form_frame,
            text="Save Changes",
            command=lambda: self.save_modified_session(track_day_idx, session),
            fg_color="#2ECC71",
            hover_color="#27AE60",
            width=150,
            height=40
        )
        save_button.pack(pady=20)

        self.session_form_window.grab_set()
        self.session_form_window.focus_set()

    def save_modified_session(self, track_day_idx, session):
        session["laps"] = self.laps_entry.get()
        session["weather"] = self.weather_var.get()
        session["tire_type"] = self.tire_type_entry.get()
        session["tire_status"] = self.tire_status_entry.get()
        session["best_lap_time"] = self.best_lap_time_entry.get()
        session["comments"] = self.comments_entry.get()
        self.track_session_mngr.save_callback(self.track_session_mngr.track_days)
        self.session_form_window.destroy()
        content_data = self.session_content_frames.get(track_day_idx)
        if content_data and content_data["visible"]:
            self.toggle_sessions_inline(track_day_idx, None)
            self.toggle_sessions_inline(track_day_idx, None)

    def show_session_context_menu(self, event, session, track_day_idx):
        pass  # Placeholder for future context menu

    def add_session_form(self, track_day_idx):
        self.session_form_window = ctk.CTkToplevel(self)
        self.session_form_window.title("Add New Session")
        self.session_form_window.geometry("550x650")

        filtered_track_days = self.track_session_mngr.get_filtered_track_days()
        if not (0 <= track_day_idx < len(filtered_track_days)):
            return
        track_day = filtered_track_days[track_day_idx]
        track_day_vehicle = track_day.get("vehicle", "N/A")

        self.session_form_window.transient(self)
        self.session_form_window.update_idletasks()

        scrollable_frame = ctk.CTkScrollableFrame(self.session_form_window)
        scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
       # TODO: Use GUI utils for scrolling instead
        def _on_mousewheel(event):
            if event.num == 4 or event.delta > 0:
                scrollable_frame._parent_canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                scrollable_frame._parent_canvas.yview_scroll(1, "units")

        scrollable_frame._parent_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        scrollable_frame._parent_canvas.bind_all("<Button-4>", _on_mousewheel)
        scrollable_frame._parent_canvas.bind_all("<Button-5>", _on_mousewheel)

        def cleanup_mousewheel_bindings():
            scrollable_frame._parent_canvas.unbind_all("<MouseWheel>")
            scrollable_frame._parent_canvas.unbind_all("<Button-4>")
            scrollable_frame._parent_canvas.unbind_all("<Button-5>")

        self.session_form_window.protocol(
            "WM_DELETE_WINDOW",
            lambda: [cleanup_mousewheel_bindings(), self.session_form_window.destroy()]
        )

        field_pady = 10

        ctk.CTkLabel(scrollable_frame, text="Session Number:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
        session_number_entry = ctk.CTkEntry(scrollable_frame, width=450, height=35)
        session_number_entry.insert(0, str(len(track_day["sessions"]) + 1))
        session_number_entry.pack(fill="x", pady=(0, field_pady))

        ctk.CTkLabel(scrollable_frame, text="Number of Laps:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
        laps_entry = ctk.CTkEntry(scrollable_frame, width=450, height=35)
        laps_entry.pack(fill="x", pady=(0, field_pady))

        if track_day_vehicle != "N/A":
            ctk.CTkLabel(scrollable_frame, text="Vehicle:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
            vehicle_label = ctk.CTkLabel(
                scrollable_frame,
                text=track_day_vehicle,
                font=("Arial", 12, "bold"),
                fg_color="#F5F7FA",
                text_color="#2C3E50"
            )
            vehicle_label.pack(fill="x", pady=(0, field_pady))

        else:
            ctk.CTkLabel(scrollable_frame, text="Vehicle:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
            vehicle_var = StringVar(value=self.track_session_mngr.vehicles[0])
            vehicle_dropdown = ctk.CTkOptionMenu(
                scrollable_frame,
                values=self.track_session_mngr.vehicles,
                variable=vehicle_var,
                width=450,
                height=35,
                dynamic_resizing=True,
                fg_color="#F5F7FA",
                button_color="#D0D3D4",
                button_hover_color="#B3B6B7",
                dropdown_fg_color="#F5F7FA",
                text_color="#2C3E50"
            )
            vehicle_dropdown.pack(fill="x", pady=(0, field_pady))

        ctk.CTkLabel(scrollable_frame, text="Weather:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
        weather_var = StringVar(value=self.track_session_mngr.weather_options[0])
        weather_dropdown = ctk.CTkOptionMenu(
            scrollable_frame,
            values=self.track_session_mngr.weather_options,
            variable=weather_var,
            width=450,
            height=35,
            dynamic_resizing=True,
            fg_color="#F5F7FA",
            button_color="#D0D3D4",
            button_hover_color="#B3B6B7",
            dropdown_fg_color="#F5F7FA",
            text_color="#2C3E50"
        )
        weather_dropdown.pack(fill="x", pady=(0, field_pady))

        ctk.CTkLabel(scrollable_frame, text="Tire Type:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
        tire_type_entry = ctk.CTkEntry(scrollable_frame, width=450, height=35)
        tire_type_entry.pack(fill="x", pady=(0, field_pady))

        ctk.CTkLabel(scrollable_frame, text="Tire Status:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
        tire_status_entry = ctk.CTkEntry(scrollable_frame, width=450, height=35)
        tire_status_entry.pack(fill="x", pady=(0, field_pady))

        ctk.CTkLabel(scrollable_frame, text="Best Lap Time:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
        best_lap_time_entry = ctk.CTkEntry(scrollable_frame, width=450, height=35)
        best_lap_time_entry.pack(fill="x", pady=(0, field_pady))

        ctk.CTkLabel(scrollable_frame, text="Comments:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
        comments_entry = ctk.CTkEntry(scrollable_frame, width=450, height=120)
        comments_entry.pack(fill="x", pady=(0, field_pady))

        button_frame = ctk.CTkFrame(self.session_form_window, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 10), side="bottom")

        def save_session():
            session_number = session_number_entry.get()
            laps = laps_entry.get()
            if track_day_vehicle != "N/A":
                vehicle = track_day_vehicle
            else:
                vehicle = vehicle_var.get()
            weather = weather_var.get()
            tire_type = tire_type_entry.get()
            tire_status = tire_status_entry.get()
            best_lap_time = best_lap_time_entry.get()
            comments = comments_entry.get()

            new_session = {
                "session_number": session_number,
                "laps": laps,
                "vehicle": vehicle,
                "weather": weather,
                "tire_type": tire_type,
                "tire_status": tire_status,
                "best_lap_time": best_lap_time,
                "comments": comments
            }

            # Use manager to add session
            self.track_session_mngr.add_session(track_day_idx, new_session)
            self.session_form_window.destroy()
            self.display_track_days()
            self.toggle_sessions_inline(track_day_idx, None)
            cleanup_mousewheel_bindings()

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=lambda: [cleanup_mousewheel_bindings(), self.session_form_window.destroy()],
            fg_color="#E74C3C",
            hover_color="#C0392B",
            text_color="white",
            width=150,
            height=40
        )
        cancel_button.pack(side="left", padx=10)

        save_button = ctk.CTkButton(
            button_frame,
            text="Save Session",
            command=save_session,
            fg_color="#2ECC71",
            hover_color="#27AE60",
            text_color="white",
            width=150,
            height=40
        )
        save_button.pack(side="right", padx=10)

        self.session_form_window.grab_set()
        self.session_form_window.focus_set()

    def create_new_track_day(self):
        self.new_window = ctk.CTkToplevel(self)
        self.new_window.title("New Track Day")
        self.new_window.geometry("400x300")

        ctk.CTkLabel(self.new_window, text="Track Name:").pack()
        self.track_entry = ctk.CTkEntry(self.new_window)
        self.track_entry.pack()

        ctk.CTkLabel(self.new_window, text="Date (YYYY-MM-DD):").pack()
        self.date_entry = ctk.CTkEntry(self.new_window)
        self.date_entry.pack()

        ctk.CTkLabel(self.new_window, text="Organizer:").pack()
        self.organizer_entry = ctk.CTkEntry(self.new_window)
        self.organizer_entry.pack()

        ctk.CTkLabel(self.new_window, text="Vehicle Used:").pack()
        self.vehicle_var = StringVar(value=self.track_session_mngr.vehicles[0] if self.track_session_mngr.vehicles else "No Vehicles Available")
        self.vehicle_dropdown = ctk.CTkOptionMenu(
            self.new_window,
            values=self.track_session_mngr.vehicles if self.track_session_mngr.vehicles else ["No Vehicles Available"],
            variable=self.vehicle_var
        )
        self.vehicle_dropdown.pack()

        save_button = ctk.CTkButton(self.new_window, text="Save", command=self.save_track_day)
        save_button.pack(pady=10)

    def save_track_day(self):
        selected_vehicle = self.vehicle_var.get()
        try:
            self.track_session_mngr.create_track_day(
                track_name=self.track_entry.get(),
                date=self.date_entry.get(),
                organizer=self.organizer_entry.get(),
                vehicle=selected_vehicle
            )
            self.new_window.destroy()
            self.display_track_days()
        except ValueError:
            ctk.CTkLabel(self.new_window, text="Please add a vehicle before creating a track day.", text_color="red").pack()
   
    def open_export_track_day_form(self, track_day_idx):

        # Set default export directory and filename
        default_dir = os.path.join(os.path.expanduser("~"), ".local/racing-companion/exports")
        track_day = self.track_session_mngr.get_track_day(track_day_idx)
        default_filename = f"{track_day.get('track', 'track_day')}_{track_day.get('date', 'unknown_date')}.csv"

        # Create file in order to pre-fill it in user dialog, otherwise it will not show up
        os.makedirs(default_dir, exist_ok=True)

        # Ask user for file path (pre-filled)
        file_path = fd.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_filename,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            # Check if directory is empty, if empty remove it. Don't remove if it contains files.
            if os.path.exists(default_dir) and not os.listdir(default_dir):
                os.rmdir(default_dir)
            return  # User cancelled

        # Export using the manager
        success = self.track_session_mngr.export_track_day_to_csv(track_day_idx, file_path)
        if success:
            messagebox.showinfo("Export Successful", f"Track day exported to:\n{file_path}")
        else:
            messagebox.showerror("Export Failed", "Failed to export track day to CSV.")

    def open_track_day_report_dialog(self):
      dialog = ctk.CTkToplevel(self)
      dialog.title("Track Day Report")
      dialog.geometry("400x420")
      dialog.transient(self)
      dialog.update_idletasks()
      dialog.grab_set()

      field_pady = 10

      # Report Type
      report_types = ["summary", "extensive", "specific"]
      report_type_var = StringVar(value="")
      ctk.CTkLabel(
         dialog,
         text="Report Type:",
         anchor="w",
         font=("Arial", 12, "bold")
      ).pack(fill="x", padx=20, pady=(10, 2))

      report_type_menu = ctk.CTkOptionMenu(
         dialog,
         values=report_types,
         variable=report_type_var,
         width=350,
         fg_color="#F5F7FA",
         button_color="#D0D3D4",
         button_hover_color="#B3B6B7",
         dropdown_fg_color="#F5F7FA",
         text_color="#2C3E50"
      )
      report_type_menu.pack(fill="x", padx=20, pady=(field_pady, field_pady))

      # Container for dynamic form (change form design between specific and the rest)
      form_frame = ctk.CTkFrame(dialog, fg_color="transparent", corner_radius=10)
      form_frame.pack(fill="both", expand=True, padx=20, pady=0)

      # Variables for other fields
      vehicle_var = StringVar(value="")
      year_var = StringVar(value="")
      track_var = StringVar(value="")
      specific_track_day_var = StringVar(value="")

      def build_report_form(*_):
         # Remove old traces
         if hasattr(form_frame, "trace_ids"):
            for var, trace_id in form_frame.trace_ids:
                  var.trace_remove("write", trace_id)
            form_frame.trace_ids = []
         
         # Clear previous widgets
         for widget in form_frame.winfo_children():
               widget.destroy()

         if report_type_var.get() == "specific":
               # Show only track day dropdown
               ctk.CTkLabel(form_frame, text="Select Track Day:", anchor="w", font=("Arial", 12, "bold")).pack(fill="x", pady=(field_pady, 2))
               # Build list of all track days (Same list as displayed)
               track_days = self.app.track_days
               track_day_options = [f"{td.get('track', 'N/A')} - {td.get('date', 'N/A')}" for td in track_days]
               specific_track_day_var.set("")
               specific_track_day_menu = ctk.CTkOptionMenu(
                  form_frame,
                  values=[""] + track_day_options,
                  variable=specific_track_day_var,
                  width=350,
                  fg_color="#F5F7FA",
                  button_color="#D0D3D4",
                  button_hover_color="#B3B6B7",
                  dropdown_fg_color="#F5F7FA",
                  text_color="#2C3E50"
               )
               specific_track_day_menu.pack(fill="x", pady=(0, field_pady))
         else:
               # Regular fields (vehicle, year, track, etc.)
               # ... your previous code for vehicle, year, track dropdowns ...
               # Use the same logic as before, but pack into form_frame

               # Vehicle
               ctk.CTkLabel(form_frame, text="Vehicle:", anchor="w", font=("Arial", 12, "bold")).pack(fill="x", pady=(field_pady, 2))
               vehicle_list = self.app.vehicles if self.app.vehicles else ["No Vehicles Available"]
               active_vehicle = self.app.active_vehicle if self.app.active_vehicle in vehicle_list else ""
               # Only prefill if not already set (so user selection is preserved on rebuild)
               if not vehicle_var.get():
                  vehicle_var.set(active_vehicle)
               vehicle_menu = ctk.CTkOptionMenu(
                  form_frame,
                  values=[""] + vehicle_list,
                  variable=vehicle_var,
                  width=350,
                  fg_color="#F5F7FA",
                  button_color="#D0D3D4",
                  button_hover_color="#B3B6B7",
                  dropdown_fg_color="#F5F7FA",
                  text_color="#2C3E50"
               )
               vehicle_menu.pack(fill="x", pady=(0, field_pady))

               ctk.CTkLabel(form_frame, text="Year:", anchor="w", font=("Arial", 12, "bold")).pack(fill="x", pady=(field_pady, 2))
               years = self.track_day_report_mngr.get_available_years(vehicle=vehicle_var.get())
               year_menu = ctk.CTkOptionMenu(
                  form_frame,
                  values=[""] + years if years else [""],
                  variable=year_var,
                  width=350,
                  fg_color="#F5F7FA",
                  button_color="#D0D3D4",
                  button_hover_color="#B3B6B7",
                  dropdown_fg_color="#F5F7FA",
                  text_color="#2C3E50"
               )
               year_menu.pack(fill="x", pady=(0, field_pady))

               if report_type_var.get() != "summary":
                  year_menu.configure(state="disabled")
               else:
                  year_menu.configure(state="normal")

               ctk.CTkLabel(form_frame, text="Track:", anchor="w", font=("Arial", 12, "bold")).pack(fill="x", pady=(field_pady, 2))
               tracks = self.track_day_report_mngr.get_available_tracks(vehicle=vehicle_var.get(), year=year_var.get())
               track_menu = ctk.CTkOptionMenu(
                  form_frame,
                  values=[""] + tracks if tracks else [""],
                  variable=track_var,
                  width=350,
                  fg_color="#F5F7FA",
                  button_color="#D0D3D4",
                  button_hover_color="#B3B6B7",
                  dropdown_fg_color="#F5F7FA",
                  text_color="#2C3E50"
               )
               track_menu.pack(fill="x", pady=(0, field_pady))

               if report_type_var.get() == "summary":
                  track_menu.configure(state="normal")
               else:
                  track_menu.configure(state="disabled")

               def update_year_menu(*_):
                  years = self.track_day_report_mngr.get_available_years(vehicle=vehicle_var.get())
                  year_menu.configure(values=[""] + years if years else [""])
                  # Only clear if current selection is not valid
                  if year_var.get() not in years:
                     year_var.set("")
                  # Enable only for summary
                  if report_type_var.get() == "summary":
                     year_menu.configure(state="normal")
                  else:
                     year_menu.configure(state="disabled")

               def update_track_menu(*_):
                  tracks = self.track_day_report_mngr.get_available_tracks(vehicle=vehicle_var.get(), year=year_var.get())
                  track_menu.configure(values=[""] + tracks if tracks else [""])
                  if track_var.get() not in tracks:
                     track_var.set("")
                  # Enable only for summary
                  if report_type_var.get() == "summary":
                     track_menu.configure(state="normal")
                  else:
                     track_menu.configure(state="disabled")

               trace_ids = []

               trace_ids.append(vehicle_var.trace_add("write", update_year_menu))
               trace_ids.append(vehicle_var.trace_add("write", update_track_menu))
               trace_ids.append(year_var.trace_add("write", update_track_menu))
               trace_ids.append(report_type_var.trace_add("write", update_year_menu))

               form_frame.trace_ids = [
                     (vehicle_var, trace_ids[0]),
                  (vehicle_var, trace_ids[1]),
                  (year_var, trace_ids[2]),
                  (report_type_var, trace_ids[3])
               ]

               # Initial update
               update_year_menu()
               update_track_menu()

         # Generate report
         def run_report():
               if report_type_var.get() == "specific":
                  selected = specific_track_day_var.get()
                  # Find the track day object
                  track_days = self.app.track_days
                  td = next((td for td in track_days if f"{td.get('track', 'N/A')} - {td.get('date', 'N/A')}" == selected), None)
                  result = self.track_day_report_mngr.generate_report("specific", track_day=td)
               else:
                  report_type = report_type_var.get()
                  if not report_type:
                      # Make sure the error dialog appears above the dialog window
                      messagebox.showerror(
                        "Failure",
                        "No 'Report Type' selected. Please select a report type before generating a report.",
                        parent=dialog
                      )
                      return

                  vehicle = vehicle_var.get()
                  year = year_var.get() if report_type == "summary" else None
                  track = track_var.get()
                  result = self.track_day_report_mngr.generate_report(report_type, vehicle, year, track=track)

               self.show_report_window(result)

         run_btn = ctk.CTkButton(
               form_frame,
               text="Generate Report",
               command=run_report,
               fg_color="#2ECC71",
               hover_color="#27AE60",
               text_color="white",
               width=150,
               height=40
         )
         run_btn.pack(side="top", pady=10, anchor="center")

      # Rebuild form when report type changes
      report_type_var.trace_add("write", build_report_form)
      build_report_form()

    def show_report_window(self, report_text, title="Track Day Report Result"):
      report_win = ctk.CTkToplevel(self)
      report_win.title(title)
      report_win.geometry("700x600")  # Bigger window

      report_win.transient(self)
      report_win.lift()
      report_win.update_idletasks()
      report_win.grab_set()

      # Header
      header_frame = ctk.CTkFrame(report_win, fg_color="transparent")
      header_frame.pack(fill="x", pady=(10, 0))

      export_btn = ctk.CTkButton(header_frame, text="Export", fg_color="#6C7A89", width=100, height=28, command=lambda: self.export_report(report_text, parent=report_win))
      export_btn.pack(side="right", padx=20, pady=4)

      # Scrollable report area
      scroll_frame = ctk.CTkScrollableFrame(report_win, fg_color="#F5F7FA")
      scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)
      def _on_mousewheel(event):
         if event.num == 4 or event.delta > 0:
            scroll_frame._parent_canvas.yview_scroll(-1, "units")
         elif event.num == 5 or event.delta < 0:
            scroll_frame._parent_canvas.yview_scroll(1, "units")

      scroll_frame._parent_canvas.bind_all("<MouseWheel>", _on_mousewheel)
      scroll_frame._parent_canvas.bind_all("<Button-4>", _on_mousewheel)
      scroll_frame._parent_canvas.bind_all("<Button-5>", _on_mousewheel)

      # Display report text with some formatting
      for line in report_text.split("\n"):
    # Detect track day header (e.g., lines starting with "- TrackName on Date")
         if line.startswith("- "):
            # Track day header: bold, colored, extra top margin
            ctk.CTkLabel(
                  scroll_frame,
                  text=line,
                  font=("Arial", 13, "bold"),
                  text_color="#1F6AA5",
                  fg_color="#EBEEF2"
            ).pack(anchor="w", pady=(18, 4), fill="x")
         elif line.strip() == "":
            ctk.CTkLabel(scroll_frame, text="", fg_color="#F5F7FA").pack()
         elif line.startswith("Vehicle:") or line.startswith("Summary") or line.startswith("Extensive") or line.startswith("Specific"):
            ctk.CTkLabel(scroll_frame, text=line, font=("Arial", 14, "bold"), text_color="#34495E", fg_color="#F5F7FA").pack(anchor="w", pady=(8,2))
         elif ":" in line:
            field, value = line.split(":", 1)
            field_frame = ctk.CTkFrame(scroll_frame, fg_color="#F5F7FA")
            field_frame.pack(anchor="w", padx=20, pady=2, fill="x")
            ctk.CTkLabel(field_frame, text=f"{field}: ", font=("Arial", 12, "bold"), text_color="#070707", fg_color="#F5F7FA").pack(side="left")
            ctk.CTkLabel(field_frame, text=value.strip(), font=("Arial", 12), text_color="#070707", fg_color="#F5F7FA").pack(side="left")
         else:
            ctk.CTkLabel(scroll_frame, text=line, font=("Arial", 12), text_color="#070707", fg_color="#F5F7FA").pack(anchor="w", padx=40)

    def export_report(self, report_text, parent=None):
      # TODO: Update this to a csv file and text
      file_path = fd.asksaveasfilename(
         defaultextension=".txt",
         filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
         parent=parent
      )
      if file_path:
         with open(file_path, "w") as f:
               f.write(report_text)
         messagebox.showinfo("Export Successful", f"Report exported to:\n{file_path}")