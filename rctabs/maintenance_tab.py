import customtkinter as ctk
from tkinter import StringVar
from rcutils.data_utils import save_maintenance_entries, load_maintenance_entries
import matplotlib.pyplot as plt
import numpy as np
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MaintenancePage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.vehicles = self.app.vehicles
        self.active_vehicle = self.app.active_vehicle
        self.maintenance_entries = self.app.maintenance_entries

        self.setup_maintenance_page()

    def setup_maintenance_page(self):
        """Maintenance log page"""
        # Data storage
        self.maintenance_entries = self.app.maintenance_entries

        # Create header with tab selector
        self.maintenance_header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.maintenance_header_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.maintenance_title_label = ctk.CTkLabel(
            self.maintenance_header_frame,
            text="Maintenance Log",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.maintenance_title_label.pack(side="left")

        # View toggle
        self.maintenance_view_selector = ctk.CTkSegmentedButton(
            self.maintenance_header_frame,
            values=["List View", "Statistics"],
            command=self.switch_maintenance_view
        )
        self.maintenance_view_selector.pack(side="left", padx=(20, 0))
        self.maintenance_view_selector.set("List View")

        self.maintenance_add_button = ctk.CTkButton(
            self.maintenance_header_frame,
            text="+ Add Entry",
            command=self.add_new_maintenance_entry,
        )
        self.maintenance_add_button.pack(side="right")

        # Search and filter
        self.maintenance_search_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.maintenance_search_frame.pack(fill="x", padx=20, pady=10)

        self.maintenance_search_entry = ctk.CTkEntry(
            self.maintenance_search_frame,
            placeholder_text="Search entries..."
        )
        self.maintenance_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.maintenance_search_entry.bind("<KeyRelease>", self.search_maintenance_entries)

        self.maintenance_filter_button = ctk.CTkButton(
            self.maintenance_search_frame,
            text="Filter",
            width=80,
            fg_color="#6C7A89",
            command=self.show_maintenance_filter_options
        )
        self.maintenance_filter_button.pack(side="right")

        # Advanced search frame (hidden by default)
        self.advanced_maintenance_search_frame = ctk.CTkFrame(self, fg_color="#F5F7FA")

        # Vehicle filter
        vehicle_frame = ctk.CTkFrame(self.advanced_maintenance_search_frame, fg_color="transparent")
        vehicle_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(vehicle_frame, text="Vehicle:").pack(side="left", padx=(0, 10))

        filter_vehicle_options = ["All"] + self.vehicles
        self.maintenance_vehicle_filter = ctk.CTkComboBox(vehicle_frame, values=filter_vehicle_options)
        self.maintenance_vehicle_filter.pack(side="left", fill="x", expand=True)
        if self.active_vehicle:
            self.maintenance_vehicle_filter.set(self.active_vehicle)
        else:
            self.maintenance_vehicle_filter.set("All")

        # Date range filter
        date_frame = ctk.CTkFrame(self.advanced_maintenance_search_frame, fg_color="transparent")
        date_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(date_frame, text="Date range:").pack(side="left", padx=(0, 10))
        self.maintenance_entry_start_date = ctk.CTkEntry(date_frame, placeholder_text="YYYY-MM-DD")
        self.maintenance_entry_start_date.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(date_frame, text="to").pack(side="left", padx=5)
        self.maintenance_entry_end_date = ctk.CTkEntry(date_frame, placeholder_text="YYYY-MM-DD")
        self.maintenance_entry_end_date.pack(side="left", padx=(5, 0))

        # Maintenance type filter
        type_frame = ctk.CTkFrame(self.advanced_maintenance_search_frame, fg_color="transparent")
        type_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(type_frame, text="Type:").pack(side="left", padx=(0, 10))
        self.maintenance_type_var = ctk.StringVar(value="All")
        types = ["All", "Routine", "Repair", "Major", "Preventive"]
        for i, t in enumerate(types):
            ctk.CTkRadioButton(type_frame, text=t, variable=self.maintenance_type_var, value=t).pack(side="left", padx=10)

        # Apply filter button
        filter_button_frame = ctk.CTkFrame(self.advanced_maintenance_search_frame, fg_color="transparent")
        filter_button_frame.pack(fill="x", pady=10)
        ctk.CTkButton(filter_button_frame, text="Apply Filters", command=self.apply_maintenance_filters).pack(side="right")
        ctk.CTkButton(filter_button_frame, text="Clear", command=self.clear_maintenance_filters,
                    fg_color="#6C7A89").pack(side="right", padx=10)

        # Create frame for list view
        self.maintenance_list_view_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.maintenance_list_view_frame.pack(fill="both", expand=True)

        # Create scrollable container for entries
        self.maintenance_entries_container = ctk.CTkScrollableFrame(
            self.maintenance_list_view_frame,
            fg_color="transparent"
        )
        self.maintenance_entries_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Create statistics view (hidden by default)
        self.maintenance_stats_view_frame = ctk.CTkFrame(self, fg_color="transparent")

        self.refresh_maintenance_entries()

        # Initialize matplotlib figure
        self.setup_maintenance_statistics_view()

    def search_maintenance_entries(self, event=None):
        """Search entries based on the search text"""
        user_search = True
        self.refresh_maintenance_entries(user_search)

    def switch_maintenance_view(self, view):
        """Switch between list view and statistics view"""
        if view == "List View":
            self.maintenance_stats_view_frame.pack_forget()
            self.maintenance_list_view_frame.pack(fill="both", expand=True)
        else:
            self.maintenance_list_view_frame.pack_forget()
            self.maintenance_stats_view_frame.pack(fill="both", expand=True)
            self.update_maintenance_statistics()

    def add_new_maintenance_entry(self):
        """Opens dialog to add a new maintenance entry"""
        dialog = ctk.CTkToplevel(self.app)
        dialog.title("Add Maintenance Entry")
        dialog.geometry("500x600")
        dialog.transient(self.app)
        self.after(100, lambda: self._setup_entry_dialog(dialog))

    def _setup_entry_dialog(self, dialog):
        try:
            dialog.grab_set()
            dialog.focus_set()
        except:
            pass

        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(title_frame, text="Title:").pack(side="left", padx=(0, 10))
        title_entry = ctk.CTkEntry(title_frame, placeholder_text="Maintenance title...")
        title_entry.pack(side="left", fill="x", expand=True)

        vehicle_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        vehicle_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(vehicle_frame, text="Vehicle:").pack(side="left", padx=(0, 10))
        vehicle_combo = ctk.CTkComboBox(vehicle_frame, values=self.vehicles)
        vehicle_combo.pack(side="left", fill="x", expand=True)

        date_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        date_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(date_frame, text="Date:").pack(side="left", padx=(0, 10))
        date_entry = ctk.CTkEntry(date_frame, placeholder_text="YYYY-MM-DD")
        date_entry.pack(side="left", fill="x", expand=True)

        duration_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        duration_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(duration_frame, text="Duration:").pack(side="left", padx=(0, 10))
        duration_entry = ctk.CTkEntry(duration_frame, placeholder_text="e.g. 1 hour 30 minutes")
        duration_entry.pack(side="left", fill="x", expand=True)

        hb_ref_label = ctk.CTkFrame(form_frame, fg_color="transparent")
        hb_ref_label.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(hb_ref_label, text="Handbook/Manual Ref:").pack(side="left", padx=(0, 10))
        hb_ref_entry = ctk.CTkEntry(hb_ref_label, placeholder_text="Haynes manual 6.7")
        hb_ref_entry.pack(side="left", fill="x", expand=True)

        tags_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        tags_frame.pack(fill="x", pady=(5, 5))
        ctk.CTkLabel(tags_frame, text="Tags:").pack(side="left", padx=(0, 10))
        tags_subframe = ctk.CTkFrame(tags_frame, fg_color="transparent")
        tags_subframe.pack(side="left", fill="x", expand=True)

        tag_vars = {}
        tags = ["Routine", "Repair", "Major", "Minor", "Preventive", "Oil", "Tires", "Engine", "Chassis", "Brakes", "Update", "Electronics"]
        columns = 4
        for i, tag in enumerate(tags):
            var = ctk.BooleanVar(value=False)
            tag_vars[tag] = var
            row = i // columns
            col = i % columns
            ctk.CTkCheckBox(tags_subframe, text=tag, variable=var).grid(row=row, column=col, padx=5, pady=5, sticky="w")

        desc_label = ctk.CTkLabel(form_frame, text="Description:")
        desc_label.pack(anchor="w", pady=(5, 5))
        desc_text = ctk.CTkTextbox(form_frame, height=150)
        desc_text.pack(fill="x", expand=True)

        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        def save_entry():
            new_entry = {
                "title": title_entry.get(),
                "vehicle": vehicle_combo.get(),
                "date": date_entry.get(),
                "duration": duration_entry.get(),
                "handbook_ref": hb_ref_entry.get(),
                "description": desc_text.get("1.0", "end-1c"),
                "tags": [tag for tag, var in tag_vars.items() if var.get()]
            }
            self.maintenance_entries.append(new_entry)
            save_maintenance_entries(self.maintenance_entries)
            self.refresh_maintenance_entries()
            dialog.destroy()

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            fg_color="#6C7A89",
            width=100
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            button_frame,
            text="Save",
            command=save_entry,
            fg_color="#2ECC71",
            hover_color="#27AE60",
            width=100
        ).pack(side="right")

    def edit_maintenance_entry(self, entry):
        print("'edit_maintenance_entry'- Not yet implemented")
        pass

    def delete_maintenance_entry(self, entry):
        if entry in self.maintenance_entries:
            self.maintenance_entries.remove(entry)
            self.refresh_maintenance_entries()
            save_maintenance_entries(self.maintenance_entries)

    def refresh_maintenance_entries(self, user_search=False):
        for widget in self.maintenance_entries_container.winfo_children():
            widget.destroy()

        search_text = self.maintenance_search_entry.get().lower()
        vehicle_filter = self.maintenance_vehicle_filter.get()
        maintenance_type = self.maintenance_type_var.get()
        start_date = self.maintenance_entry_start_date.get()
        end_date = self.maintenance_entry_end_date.get()

        filtered_entries = self.maintenance_entries.copy()

        if search_text:
            filtered_entries = [
                e for e in filtered_entries if
                search_text in e["title"].lower() or
                search_text in e["description"].lower() or
                search_text in e["vehicle"].lower()
            ]

        if user_search is False and self.active_vehicle is not None:
            vehicle_filter = self.active_vehicle

        if vehicle_filter != "All":
            filtered_entries = [e for e in filtered_entries if vehicle_filter in e["vehicle"]]

        if maintenance_type != "All":
            filtered_entries = [e for e in filtered_entries if maintenance_type in e.get("tags", [])]

        if start_date:
            filtered_entries = [e for e in filtered_entries if e["date"] >= start_date]
        if end_date:
            filtered_entries = [e for e in filtered_entries if e["date"] <= end_date]

        for entry in filtered_entries:
            self.create_maintenance_entry_card(
                entry["title"],
                entry["description"],
                entry["vehicle"],
                entry["date"],
                entry["duration"],
                entry.get("tags"),
                entry["handbook_ref"]
            )

        if self.maintenance_view_selector.get() == "Statistics":
            self.update_maintenance_statistics()

    def create_maintenance_entry_card(self, title, description, vehicle, date, duration, tags=None, handbook_ref=""):
        entry = {
            "title": title,
            "description": description,
            "vehicle": vehicle,
            "date": date,
            "duration": duration,
            "tags": tags or [],
            "handbook_ref": handbook_ref,
        }

        card = ctk.CTkFrame(
            self.maintenance_entries_container,
            corner_radius=10,
            fg_color="white",
            border_width=1,
            border_color="#E0E0E0"
        )
        card.pack(fill="x", pady=8, ipady=5)

        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=15, pady=(10, 5))

        title_label = ctk.CTkLabel(
            top_row,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        title_label.pack(side="left")

        date_label = ctk.CTkLabel(
            top_row,
            text=date,
            font=ctk.CTkFont(size=14),
            text_color="#6C7A89"
        )
        date_label.pack(side="right")

        info_row = ctk.CTkFrame(card, fg_color="transparent")
        info_row.pack(fill="x", padx=15, pady=5)

        vehicle_label = ctk.CTkLabel(
            info_row,
            text=f"Vehicle: {vehicle}",
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        vehicle_label.pack(side="left")

        duration_label = ctk.CTkLabel(
            info_row,
            text=f"Duration: {duration}",
            font=ctk.CTkFont(size=14),
            text_color="#6C7A89"
        )
        duration_label.pack(side="right")

        desc_frame = ctk.CTkFrame(card, fg_color="transparent")
        desc_frame.pack(fill="x", padx=15, pady=(5, 10))

        desc_label = ctk.CTkLabel(
            desc_frame,
            text=description,
            font=ctk.CTkFont(size=14),
            anchor="w",
            justify="left",
            wraplength=500
        )
        desc_label.pack(side="left", fill="x")

        if tags:
            tags_frame = ctk.CTkFrame(card, fg_color="transparent")
            tags_frame.pack(fill="x", padx=15, pady=(0, 10))
            for tag in tags:
                tag_label = ctk.CTkLabel(
                    tags_frame,
                    text=tag,
                    fg_color="#E5F2FF",
                    corner_radius=5,
                    padx=8,
                    pady=2,
                    font=ctk.CTkFont(size=12)
                )
                tag_label.pack(side="left", padx=(0, 5))

        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(0, 10))

        edit_button = ctk.CTkButton(
            button_frame,
            text="Edit",
            width=80,
            height=28,
            fg_color="#6C7A89",
            command=lambda e=entry: self.edit_maintenance_entry(e)
        )
        edit_button.pack(side="right", padx=5)

        delete_button = ctk.CTkButton(
            button_frame,
            text="Delete",
            width=80,
            height=28,
            fg_color="#E74C3C",
            command=lambda e=entry: self.delete_maintenance_entry(e)
        )
        delete_button.pack(side="right", padx=5)

        return card

    def show_maintenance_filter_options(self):
        if self.advanced_maintenance_search_frame.winfo_ismapped():
            self.advanced_maintenance_search_frame.pack_forget()
            self.maintenance_filter_button.configure(text="Filter", fg_color="#6C7A89", hover_color="#34495E")
        else:
            self.advanced_maintenance_search_frame.pack(fill="x", padx=20, pady=(0, 10))
            self.maintenance_filter_button.configure(text="Hide Filter", fg_color="#E67E22", hover_color="#D35400")

    def clear_maintenance_filters(self):
        self.maintenance_vehicle_filter.set("All")
        self.maintenance_entry_start_date.delete(0, 'end')
        self.maintenance_entry_end_date.delete(0, 'end')
        self.maintenance_type_var.set("All")
        self.maintenance_search_entry.delete(0, 'end')
        self.refresh_maintenance_entries()

    def apply_maintenance_filters(self):
        user_search = True
        self.refresh_maintenance_entries(user_search)

    def setup_maintenance_statistics_view(self):
        self.stats_tabs = ctk.CTkTabview(self.maintenance_stats_view_frame)
        self.stats_tabs.pack(fill="both", expand=True, padx=20, pady=20)

        self.stats_tabs.add("Maintenance Frequency")
        self.stats_tabs.add("Time Spent")
        self.stats_tabs.add("Vehicle Comparison")

        freq_frame = ctk.CTkFrame(self.stats_tabs.tab("Maintenance Frequency"), fg_color="transparent")
        freq_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.freq_fig, self.freq_ax = plt.subplots(figsize=(10, 6))
        self.freq_canvas = FigureCanvasTkAgg(self.freq_fig, master=freq_frame)
        self.freq_canvas.get_tk_widget().pack(fill="both", expand=True)

        time_frame = ctk.CTkFrame(self.stats_tabs.tab("Time Spent"), fg_color="transparent")
        time_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.time_fig, self.time_ax = plt.subplots(figsize=(10, 6))
        self.time_canvas = FigureCanvasTkAgg(self.time_fig, master=time_frame)
        self.time_canvas.get_tk_widget().pack(fill="both", expand=True)

        vehicle_frame = ctk.CTkFrame(self.stats_tabs.tab("Vehicle Comparison"), fg_color="transparent")
        vehicle_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.vehicle_fig, self.vehicle_ax = plt.subplots(figsize=(10, 6))
        self.vehicle_canvas = FigureCanvasTkAgg(self.vehicle_fig, master=vehicle_frame)
        self.vehicle_canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_maintenance_statistics(self):
        self.freq_ax.clear()
        self.time_ax.clear()
        self.vehicle_ax.clear()

        if not self.maintenance_entries:
            return

        vehicles = {}
        months = {}
        maintenance_types = {}

        for entry in self.maintenance_entries:
            vehicle = entry.get("vehicle", "Unknown")
            if vehicle not in vehicles:
                vehicles[vehicle] = {"count": 0, "time": 0}
            vehicles[vehicle]["count"] += 1

            duration_str = entry.get("duration", "0 minutes")
            duration_match = re.search(r'(\d+)\s*(?:hour|hr)s?', duration_str, re.IGNORECASE)
            hours = int(duration_match.group(1)) if duration_match else 0

            duration_match = re.search(r'(\d+)\s*(?:minute|min)s?', duration_str, re.IGNORECASE)
            minutes = int(duration_match.group(1)) if duration_match else 0

            total_minutes = hours * 60 + minutes
            vehicles[vehicle]["time"] += total_minutes

            date_str = entry.get("date", "2025-01-01")
            month = date_str[:7]
            if month not in months:
                months[month] = 0
            months[month] += 1

            for tag in entry.get("tags", []):
                if tag not in maintenance_types:
                    maintenance_types[tag] = 0
                maintenance_types[tag] += 1

        sorted_months = sorted(months.keys())
        month_counts = [months[m] for m in sorted_months]
        month_labels = [m[5:7] + "/" + m[0:4] for m in sorted_months]

        self.freq_ax.bar(month_labels, month_counts)
        self.freq_ax.set_title('Maintenance Frequency by Month')
        self.freq_ax.set_xlabel('Month')
        self.freq_ax.set_ylabel('Number of Maintenance Tasks')
        self.freq_fig.tight_layout()
        self.freq_canvas.draw()

        if maintenance_types:
            types = list(maintenance_types.keys())
            counts = list(maintenance_types.values())
            self.time_ax.pie(counts, labels=types, autopct='%1.1f%%', startangle=90,
                       colors=plt.cm.tab10.colors[:len(types)])
            self.time_ax.set_title('Maintenance Tasks by Type')
            self.time_fig.tight_layout()
            self.time_canvas.draw()

        if vehicles:
            vehicle_names = list(vehicles.keys())
            counts = [vehicles[v]["count"] for v in vehicle_names]
            times = [vehicles[v]["time"]/60 for v in vehicle_names]

            x = np.arange(len(vehicle_names))
            width = 0.35

            self.vehicle_ax.bar(x - width/2, counts, width, label='# of Tasks')
            self.vehicle_ax.bar(x + width/2, times, width, label='Hours Spent')

            self.vehicle_ax.set_title('Maintenance Comparison by Vehicle')
            self.vehicle_ax.set_xticks(x)
            self.vehicle_ax.set_xticklabels([v.split(" (")[0] for v in vehicle_names])
            self.vehicle_ax.legend()
            self.vehicle_ax.set_ylabel('Count / Hours', loc='center')
            self.vehicle_fig.tight_layout()
            self.vehicle_fig.subplots_adjust(left=0.10)
            self.vehicle_canvas.draw()