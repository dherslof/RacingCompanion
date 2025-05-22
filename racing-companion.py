#Todo: Add file header + description

import customtkinter as ctk
import json
import os
import matplotlib.pyplot as plt
import numpy as np
import re
from datetime import datetime
from tkinter import StringVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Initialize app
ctk.set_appearance_mode("light")  # Light mode
ctk.set_default_color_theme("blue")  # Blue-themed UI

data_file = "track_sessions.json"
vehicles_file = "vehicles.json"

app_version = "1.0.0"

footer_template_text = f"dherslof | Racing Companion | version: {app_version} | Active Vehicle: None"

def load_data():
    if os.path.exists(data_file):
        with open(data_file, "r") as file:
            return json.load(file)
    return []

def save_data(data):
    with open(data_file, "w") as file:
        json.dump(data, file, indent=4)

def save_vehicles(self, vehicles, vehicle_data=None):
    data_to_save = {
        "vehicles": vehicles,
        "vehicle_data": vehicle_data or {}
    }
    with open(self.vehicles_file, 'w') as f:
        json.dump(data_to_save, f, indent=2)

def load_vehicles():
    """Load vehicles and vehicle data from JSON file or return default if file doesn't exist."""
    if os.path.exists(vehicles_file):
        with open(vehicles_file, "r") as file:
            data = json.load(file)
            return data.get("vehicles", []), data.get("vehicle_data", {})
    # Default vehicles list and empty vehicle data
    return [], {}

def save_vehicles(vehicles, vehicle_data):
    """Save vehicles and vehicle data to JSON file."""
    data_to_save = {
        "vehicles": vehicles,
        "vehicle_data": vehicle_data
    }
    with open(vehicles_file, "w") as file:
        json.dump(data_to_save, file, indent=4)

def save_maintenance_entries(maintenance_entries):
    """Save maintenance entries to a JSON file."""
    maintenance_file = "maintenance_entries.json"
    with open(maintenance_file, "w") as file:
        json.dump(maintenance_entries, file, indent=4)

def load_maintenance_entries():
    """Load maintenance entries from a JSON file."""
    maintenance_file = "maintenance_entries.json"
    if os.path.exists(maintenance_file):
        with open(maintenance_file, "r") as file:
            return json.load(file)
    else:
        return []


class RacingDiaryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Racing Companion")
        self.geometry("850x750")

        # Tab view
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabs
        self.tab_welcome = self.tab_view.add("Welcome")
        self.tab_sessions = self.tab_view.add("Track Sessions")
        self.tab_maintenance = self.tab_view.add("Maintenance Log")
        self.tab_part_inventory = self.tab_view.add("Parts Inventory")

        # Store session frames in a dictionary - rename to avoid collision
        self.session_content_frames = {}

        # Define weather options
        self.weather_options = ["Sunny", "Cloudy", "Overcast", "Light Rain", "Heavy Rain", "Wet Track", "Mixed Conditions", "drying-up"]

        # Sample vehicles list (to be replaced with actual data later)
        #self.vehicles = load_vehicles()
        self.vehicles, self.vehicle_data = load_vehicles()
        # Ensure vehicles and vehicle_data are valid
        if not isinstance(self.vehicles, list):
            self.vehicles = []
        if not isinstance(self.vehicle_data, dict):
            self.vehicle_data = {}

        # Track the currently selected vehicle
        self.active_vehicle = None

        # Footer frame
        self.footer_frame = ctk.CTkFrame(self, fg_color="#D0D3D4", height=40)
        self.footer_frame.pack(side="bottom", fill="x")

        self.footer_label = ctk.CTkLabel(self.footer_frame, text=f"{footer_template_text}", font=("Arial", 14, "bold"))
        self.footer_label.pack(pady=5)

        # Setup pages
        self.setup_welcome_page()
        self.setup_track_sessions_page()
        self.setup_maintenance_page()
        self.setup_part_inventory_page()

    def setup_welcome_page(self):
        # Main container
        welcome_container = ctk.CTkFrame(self.tab_welcome, fg_color="transparent")
        welcome_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Welcome section
        welcome_section = ctk.CTkFrame(welcome_container, fg_color="transparent")
        welcome_section.pack(fill="x", pady=10)

        label = ctk.CTkLabel(welcome_section, text="Welcome to your Racing Companion!", font=("Arial", 24, "bold"))
        label.pack(pady=10)

        description = ctk.CTkLabel(welcome_section,
                                text="Keep track of your track days, vehicle maintenance and garage inventory with ease!",
                                font=("Arial", 14),
                                wraplength=600)
        description.pack(pady=5)

        # Divider
        divider = ctk.CTkFrame(welcome_container, height=2, fg_color="#D0D3D4")
        divider.pack(fill="x", pady=20)

        # Vehicles section
        vehicles_section = ctk.CTkFrame(welcome_container, fg_color="transparent")
        vehicles_section.pack(fill="both", expand=True, pady=10)

        # Vehicles header with title and add button side by side
        vehicles_header = ctk.CTkFrame(vehicles_section, fg_color="transparent")
        vehicles_header.pack(fill="x", pady=10)

        vehicles_title = ctk.CTkLabel(vehicles_header, text="Your Vehicles", font=("Arial", 18, "bold"))
        vehicles_title.pack(side="left")

        add_vehicle_btn = ctk.CTkButton(vehicles_header,
                                    text="+ Add Vehicle",
                                    command=self.show_add_vehicle_dialog,
                                    fg_color="#2ECC71",
                                    hover_color="#27AE60",
                                    width=120)
        add_vehicle_btn.pack(side="right")

        # Create scrollable frame for vehicles
        self.vehicles_container = ctk.CTkScrollableFrame(vehicles_section, fg_color="transparent")
        self.vehicles_container.pack(fill="both", expand=True, pady=10)

        self.display_vehicles()

    def display_vehicles(self):
        """Display vehicles as cards in the welcome page."""
        # Clear existing vehicles
        for widget in self.vehicles_container.winfo_children():
            widget.destroy()

        if not self.vehicles:
        # Show a message if no vehicles are available
            empty_label = ctk.CTkLabel(self.vehicles_container, text="No vehicles added yet. Click '+ Add Vehicle' to add one.",
                                    font=("Arial", 14), text_color="gray")
            empty_label.pack(pady=20)
            return

        # Create a frame to hold vehicles in a grid (3 columns)
        grid_frame = ctk.CTkFrame(self.vehicles_container, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)

        # Configure grid columns (3 equal columns)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.columnconfigure(2, weight=1)

        # Add vehicle cards
        for i, vehicle in enumerate(self.vehicles):
            # Calculate grid position (row, column)
            row = i // 3
            col = i % 3

            # Determine card color based on whether it's the active vehicle
            card_color = "#D4EFDF" if vehicle == self.active_vehicle else "#eeeeee"

            # Create card frame
            card = ctk.CTkFrame(grid_frame, corner_radius=10, border_width=1, fg_color=card_color)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")

            # Content frame
            content_frame = ctk.CTkFrame(card, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=15, pady=15)

            vehicle_type = self.vehicle_data.get(vehicle, {}).get('type', 'Car')  # Default to 'Car' if not found


            # Define abbreviations for vehicle types
            abbreviations = {
                "Car": "CAR",
                "Motorcycle": "MC",
                "Quad": "QUAD",
                "Snowmobile": "SLED"
            }
            vehicle_type_abbr = abbreviations.get(vehicle_type, vehicle_type[:4].upper())  # Default to first 4 letters

            # Car icon
            icon_frame = ctk.CTkFrame(content_frame, width=40, height=40,
                                    corner_radius=20, fg_color="#3498DB")
            icon_frame.pack(pady=5)
            icon_frame.pack_propagate(False)  # Force the frame to keep its size

            icon_label = ctk.CTkLabel(icon_frame, text=vehicle_type_abbr,
                                    font=("Arial", 10, "bold"),
                                    text_color="white", anchor="center")
            icon_label.pack(expand=True, padx=5, pady=5)

            # Vehicle name
            name_label = ctk.CTkLabel(content_frame, text=vehicle, font=("Arial", 14, "bold"))
            name_label.pack(pady=5)

            # Button frame
            button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            button_frame.pack(fill="x", pady=10)

            # Edit button
            edit_btn = ctk.CTkButton(button_frame,
                                    text="Edit",
                                    command=lambda v=vehicle: self.edit_vehicle(v),
                                    fg_color="#6C7A89",  # Yellow color
                                    #hover_color="#D4AC0D",  # Darker yellow on hover
                                    width=40,
                                    height=28)
            edit_btn.pack(side="left", padx=5)

            # Delete button
            delete_btn = ctk.CTkButton(button_frame,
                                    text="Delete",
                                    command=lambda v=vehicle: self.delete_vehicle(v),
                                    fg_color="#E74C3C",
                                    hover_color="#C0392B",
                                    width=40,
                                    height=28)
            delete_btn.pack(side="right", padx=5)

            # Select button
            select_btn_text = "Unselect" if vehicle == self.active_vehicle else "Select"
            select_btn = ctk.CTkButton(button_frame,
                                    text=select_btn_text,
                                    command=lambda v=vehicle: self.toggle_active_vehicle(v),
                                    fg_color="#3498DB",  # Blue color (same as the previous edit button)
                                    hover_color="#2980B9",  # Darker blue on hover
                                    width=80,
                                    height=28)
            select_btn.pack(side="left", padx=5)

            # Add hover effect - store the vehicle and card info in closure
            def on_enter(event, w=card, v=vehicle):
                # Only change color if it's not already the active vehicle
                if v != self.active_vehicle:
                    w.configure(fg_color="#D4EFDF")  # Light green on hover

            def on_leave(event, w=card, v=vehicle):
                # Only change color back if it's not the active vehicle
                if v != self.active_vehicle:
                    w.configure(fg_color="#eeeeee")  # Reset to original color

            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)

    def toggle_active_vehicle(self, vehicle):
        """Set the selected vehicle as the active vehicle."""
        if self.active_vehicle == vehicle:
            self.active_vehicle = None  # Unselect the vehicle
        else:
            self.active_vehicle = vehicle  # Set the selected vehicle as active

        self.display_vehicles()  # Refresh the vehicle display
        self.display_track_days()  # Refresh the track days display
        self.refresh_maintenance_entries() # Refresh the maintenance entries display
        self.update_footer()  # Update the footer display

    def update_footer(self):
        """Update the footer to display the active vehicle."""
        if self.active_vehicle:
            self.footer_label.configure(text=f"dherslof | Racing Companion | version: {app_version} | Active Vehicle: {self.active_vehicle}")
        else:
            self.footer_label.configure(text=f"{footer_template_text}")

    def show_add_vehicle_dialog(self):
        """Display dialog for adding a new vehicle."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add New Vehicle")
        dialog.geometry("400x500")
        dialog.transient(self)  # Make dialog modal

        # Center dialog
        dialog.update_idletasks()

        # Container frame with padding
        container = ctk.CTkFrame(dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(container, text="Add New Vehicle", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # Vehicle name entry
        ctk.CTkLabel(container, text="Vehicle Name:", anchor="w").pack(fill="x", pady=(10, 0))
        vehicle_entry = ctk.CTkEntry(container, height=35, fg_color="#F5F7FA")
        vehicle_entry.pack(fill="x", pady=(5, 15))
        vehicle_entry.focus()

        # Vehicle type dropdown
        ctk.CTkLabel(container, text="Vehicle Type:", anchor="w").pack(fill="x", pady=(10, 0))
        vehicle_type_var = StringVar(value="Car")  # Default to "Car"
        vehicle_type_dropdown = ctk.CTkOptionMenu(
            container,
            values=["Car", "Motorcycle", "Quad", "Snowmobile"],
            variable=vehicle_type_var,
            fg_color="#F5F7FA",
            button_color="#D0D3D4",
            button_hover_color="#B3B6B7",
            dropdown_fg_color="#F5F7FA",
            text_color="#2C3E50"
        )
        vehicle_type_dropdown.pack(fill="x", pady=(5, 15))

        # Model year selector
        ctk.CTkLabel(container, text="Model Year:", anchor="w").pack(fill="x", pady=(10, 0))
        model_year_var = StringVar(value=str(datetime.now().year))  # Default to current year
        model_year_dropdown = ctk.CTkOptionMenu(
            container,
            values=[str(year) for year in range(1980, datetime.now().year + 1)],  # Years from 1980 to current year
            variable=model_year_var,
            fg_color="#F5F7FA",
            button_color="#D0D3D4",
            button_hover_color="#B3B6B7",
            dropdown_fg_color="#F5F7FA",
            text_color="#2C3E50"
        )
        model_year_dropdown.pack(fill="x", pady=(5, 15))

        # Miscellaneous field
        ctk.CTkLabel(container, text="Miscellaneous Info:", anchor="w").pack(fill="x", pady=(10, 0))
        misc_entry = ctk.CTkEntry(container, height=35, fg_color="#F5F7FA")
        misc_entry.pack(fill="x", pady=(5, 15))


        # Buttons frame
        buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)

        # Cancel button
        cancel_btn = ctk.CTkButton(buttons_frame,
                                text="Cancel",
                                command=dialog.destroy,
                                fg_color="#E74C3C",
                                hover_color="#C0392B",
                                width=100)
        cancel_btn.pack(side="left", padx=5)

        # Save button
        def save_new_vehicle():
            vehicle_name = vehicle_entry.get().strip()
            if vehicle_name:
                self.vehicles.append(vehicle_name)
                save_vehicles(self.vehicles, self.vehicle_data)
                self.display_vehicles()
                dialog.destroy()

        save_btn = ctk.CTkButton(buttons_frame,
                                text="Save",
                                command=save_new_vehicle,
                                fg_color="#2ECC71",
                                hover_color="#27AE60",
                                width=100)
        save_btn.pack(side="right", padx=5)

        # Make dialog modal
        dialog.grab_set()
        dialog.wait_window()

    def edit_vehicle(self, vehicle):
        """Edit an existing vehicle."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Vehicle")
        dialog.geometry("400x500")  # Increased height to accommodate all fields
        dialog.transient(self)

        # Center dialog
        dialog.update_idletasks()

        # Container frame with padding
        container = ctk.CTkFrame(dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(container, text="Edit Vehicle", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # Get existing vehicle data if it exists in dictionary format
        vehicle_data = self.vehicle_data.get(vehicle, {})

        # Vehicle name entry - pre-filled with current name
        ctk.CTkLabel(container, text="Vehicle Name:", anchor="w").pack(fill="x", pady=(10, 0))
        vehicle_entry = ctk.CTkEntry(container, height=35, fg_color="#F5F7FA")
        vehicle_entry.pack(fill="x", pady=(5, 15))
        vehicle_entry.insert(0, vehicle)  # Pre-fill with current vehicle name
        vehicle_entry.focus()

        # Vehicle type dropdown - select current type if available
        ctk.CTkLabel(container, text="Vehicle Type:", anchor="w").pack(fill="x", pady=(10, 0))
        current_type = vehicle_data.get('type', "Car")  # Default to "Car" if not found
        vehicle_type_var = StringVar(value=current_type)
        vehicle_type_dropdown = ctk.CTkOptionMenu(
            container,
            values=["Car", "Motorcycle", "Quad", "Snowmobile"],
            variable=vehicle_type_var,
            fg_color="#F5F7FA",
            button_color="#D0D3D4",
            button_hover_color="#B3B6B7",
            dropdown_fg_color="#F5F7FA",
            text_color="#2C3E50"
        )
        vehicle_type_dropdown.pack(fill="x", pady=(5, 15))

        # Model year selector - select current year if available
        ctk.CTkLabel(container, text="Model Year:", anchor="w").pack(fill="x", pady=(10, 0))
        current_year = str(vehicle_data.get('year', datetime.now().year))  # Default to current year if not found
        model_year_var = StringVar(value=current_year)
        model_year_dropdown = ctk.CTkOptionMenu(
            container,
            values=[str(year) for year in range(1980, datetime.now().year + 1)],  # Years from 1980 to current year
            variable=model_year_var,
            fg_color="#F5F7FA",
            button_color="#D0D3D4",
            button_hover_color="#B3B6B7",
            dropdown_fg_color="#F5F7FA",
            text_color="#2C3E50"
        )
        model_year_dropdown.pack(fill="x", pady=(5, 15))

        # Miscellaneous field - pre-fill with current info if available
        ctk.CTkLabel(container, text="Miscellaneous Info:", anchor="w").pack(fill="x", pady=(10, 0))
        misc_entry = ctk.CTkEntry(container, height=35, fg_color="#F5F7FA")
        misc_entry.pack(fill="x", pady=(5, 15))
        misc_entry.insert(0, vehicle_data.get('misc', ''))

        # Buttons frame
        buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)

        # Cancel button
        cancel_btn = ctk.CTkButton(buttons_frame,
                                    text="Cancel",
                                    command=dialog.destroy,
                                    fg_color="#E74C3C",
                                    hover_color="#C0392B",
                                    width=100)
        cancel_btn.pack(side="left", padx=5)

        # Save button
        def save_edited_vehicle():
            new_name = vehicle_entry.get().strip()
            new_type = vehicle_type_var.get()
            new_year = model_year_var.get()
            new_misc = misc_entry.get().strip()

            if new_name:
                # Update vehicle name in list if changed
                if new_name != vehicle:
                    index = self.vehicles.index(vehicle)
                    self.vehicles[index] = new_name

                    # Update vehicle_data dictionary
                    self.vehicle_data[new_name] = self.vehicle_data.pop(vehicle, {})
                # Update vehicle data
                self.vehicle_data[new_name] = {
                    'type': new_type,
                    'year': new_year,
                    'misc': new_misc
                }

                # Save changes
                save_vehicles(self.vehicles, self.vehicle_data)
                self.display_vehicles()
                dialog.destroy()

        save_btn = ctk.CTkButton(buttons_frame,
                                text="Save",
                                command=save_edited_vehicle,
                                fg_color="#2ECC71",
                                hover_color="#27AE60",
                                width=100)
        save_btn.pack(side="right", padx=5)

        # Make dialog modal
        dialog.grab_set()
        dialog.wait_window()

    def delete_vehicle(self, vehicle):
        """Delete a vehicle with confirmation."""
        # Create confirmation dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("400x180")
        dialog.transient(self)

        # Center dialog
        dialog.update_idletasks()

        # Container frame with padding
        container = ctk.CTkFrame(dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Warning message
        msg = ctk.CTkLabel(container,
                        text=f"Are you sure you want to delete '{vehicle}'?",
                        wraplength=350,
                        font=("Arial", 14))
        msg.pack(pady=20)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)

        # Cancel button
        cancel_btn = ctk.CTkButton(buttons_frame,
                                text="Cancel",
                                command=dialog.destroy,
                                fg_color="#7F8C8D",  # Gray
                                hover_color="#5D6D7E",
                                width=100)
        cancel_btn.pack(side="left", padx=5)

        # Delete button
        def confirm_delete():
            # Remove vehicle from storage
            self.vehicles.remove(vehicle)

            # Remove vehicle data if it exists from storage
            if vehicle in self.vehicle_data:
                del self.vehicle_data[vehicle]

            save_vehicles(self.vehicles, self.vehicle_data)
            self.display_vehicles()
            dialog.destroy()

        delete_btn = ctk.CTkButton(buttons_frame,
                                text="Delete",
                                command=confirm_delete,
                                fg_color="#E74C3C",  # Red
                                hover_color="#C0392B",
                                width=100)
        delete_btn.pack(side="right", padx=5)

        # Make dialog modal
        dialog.grab_set()
        dialog.wait_window()

    def setup_track_sessions_page(self):
        """Track session logging with card-style design."""
        self.session_frame = ctk.CTkFrame(self.tab_sessions)
        self.session_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.track_days = load_data()
        self.display_track_days()

    def setup_maintenance_page(self):
        """Maintenance log page"""
        # Data storage
        self.maintenance_entries = load_maintenance_entries()

        # Create header with tab selector
        self.maintenance_header_frame = ctk.CTkFrame(self.tab_maintenance, fg_color="transparent")
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
        self.maintenance_search_frame = ctk.CTkFrame(self.tab_maintenance, fg_color="transparent")
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
        self.advanced_maintenance_search_frame = ctk.CTkFrame(self.tab_maintenance, fg_color="#F5F7FA")

        # Vehicle filter
        vehicle_frame = ctk.CTkFrame(self.advanced_maintenance_search_frame, fg_color="transparent")
        vehicle_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(vehicle_frame, text="Vehicle:").pack(side="left", padx=(0, 10))

        filter_vehicle_options = ["All"] + self.vehicles # Values in the drop down selection
        self.maintenance_vehicle_filter = ctk.CTkComboBox(vehicle_frame, values=filter_vehicle_options)
        self.maintenance_vehicle_filter.pack(side="left", fill="x", expand=True)
        if self.active_vehicle:
            self.maintenance_vehicle_filter.set(self.active_vehicle)
        else:
            self.maintenance_vehicle_filter.set("All")  # Default to "All"

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
        self.maintenance_list_view_frame = ctk.CTkFrame(self.tab_maintenance, fg_color="transparent")
        self.maintenance_list_view_frame.pack(fill="both", expand=True)

        # Create scrollable container for entries
        self.maintenance_entries_container = ctk.CTkScrollableFrame(
            self.maintenance_list_view_frame,
            fg_color="transparent"
        )
        self.maintenance_entries_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Create statistics view (hidden by default)
        self.maintenance_stats_view_frame = ctk.CTkFrame(self.tab_maintenance, fg_color="transparent")

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
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Maintenance Entry")
        dialog.geometry("500x600")

        # Position dialog at center of parent window
        dialog.transient(self.winfo_toplevel())  # Make dialog transient for the main window

        # Wait a moment before grabbing - this allows the window to be created first
        self.after(100, lambda: self._setup_entry_dialog(dialog))

    def _setup_entry_dialog(self, dialog):
        """Set up the entry dialog after it's created"""
        # Try to grab focus - wrapped in try/except to handle potential issues
        try:
            dialog.grab_set()
            dialog.focus_set()
        except:
            pass  # If grab fails, continue anyway

        # Form frame
        form_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(title_frame, text="Title:").pack(side="left", padx=(0, 10))
        title_entry = ctk.CTkEntry(title_frame, placeholder_text="Maintenance title...")
        title_entry.pack(side="left", fill="x", expand=True)

        # Vehicle
        vehicle_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        vehicle_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(vehicle_frame, text="Vehicle:").pack(side="left", padx=(0, 10))
        vehicle_combo = ctk.CTkComboBox(vehicle_frame, values=self.vehicles)
        vehicle_combo.pack(side="left", fill="x", expand=True)

        # Date
        date_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        date_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(date_frame, text="Date:").pack(side="left", padx=(0, 10))
        date_entry = ctk.CTkEntry(date_frame, placeholder_text="YYYY-MM-DD")
        date_entry.pack(side="left", fill="x", expand=True)

        # Duration
        duration_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        duration_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(duration_frame, text="Duration:").pack(side="left", padx=(0, 10))
        duration_entry = ctk.CTkEntry(duration_frame, placeholder_text="e.g. 1 hour 30 minutes")
        duration_entry.pack(side="left", fill="x", expand=True)

        # Handbook reference
        hb_ref_label = ctk.CTkFrame(form_frame, fg_color="transparent")
        hb_ref_label.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(hb_ref_label, text="Handbook/Manual Ref:").pack(side="left", padx=(0, 10))
        hb_ref_entry = ctk.CTkEntry(hb_ref_label, placeholder_text="Haynes manual 6.7")
        hb_ref_entry.pack(side="left", fill="x", expand=True)

        # Tags
        tags_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        tags_frame.pack(fill="x", pady=(5, 5))  # Reduced vertical padding
        ctk.CTkLabel(tags_frame, text="Tags:").pack(side="left", padx=(0, 10))

        # Create a subframe for the tags with grid layout
        tags_subframe = ctk.CTkFrame(tags_frame, fg_color="transparent")
        tags_subframe.pack(side="left", fill="x", expand=True)

        tag_vars = {}
        tags = ["Routine", "Repair", "Major", "Minor", "Preventive", "Oil", "Tires", "Engine", "Chassis", "Brakes", "Update", "Electronics"]

        # Configure grid layout for tags
        columns = 4  # Number of columns in the grid
        for i, tag in enumerate(tags):
            var = ctk.BooleanVar(value=False)
            tag_vars[tag] = var
            row = i // columns  # Calculate the row index
            col = i % columns   # Calculate the column index
            ctk.CTkCheckBox(tags_subframe, text=tag, variable=var).grid(row=row, column=col, padx=5, pady=5, sticky="w")

        # Description
        desc_label = ctk.CTkLabel(form_frame, text="Description:")
        desc_label.pack(anchor="w", pady=(5, 5))  # Reduced vertical padding
        desc_text = ctk.CTkTextbox(form_frame, height=150)
        desc_text.pack(fill="x", expand=True)

        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))

        # Function to save the new entry
        def save_entry():
            # Get all values
            new_entry = {
                "title": title_entry.get(),
                "vehicle": vehicle_combo.get(),
                "date": date_entry.get(),
                "duration": duration_entry.get(),
                "handbook_ref": hb_ref_entry.get(),
                "description": desc_text.get("1.0", "end-1c"),
                "tags": [tag for tag, var in tag_vars.items() if var.get()]
            }

            # Add to entries list
            self.maintenance_entries.append(new_entry)

            save_maintenance_entries(self.maintenance_entries)

            # Refresh the display
            self.refresh_maintenance_entries()

            # Close dialog
            dialog.destroy()

        # Add buttons
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
            fg_color="#2ECC71",  # Green color
            hover_color="#27AE60",  # Darker green on hover
            width=100
        ).pack(side="right")

    def edit_maintenance_entry(self, entry):
        """Opens dialog to edit an existing entry"""
        print("'edit_maintenance_entry'- Not yet implemented")
        # This would be similar to add_new_entry but pre-populated
        pass

    def delete_maintenance_entry(self, entry):
        """Removes an entry from the maintenance log"""
        if entry in self.maintenance_entries:
            #Todo: Create confirmation dialog
            self.maintenance_entries.remove(entry)
            self.refresh_maintenance_entries()
            save_maintenance_entries(self.maintenance_entries)


    def refresh_maintenance_entries(self, user_search=False):
        """Clear and recreate all entry cards based on current filters"""
        # Clear existing entries
        for widget in self.maintenance_entries_container.winfo_children():
            widget.destroy()

        # Get filter values
        search_text = self.maintenance_search_entry.get().lower()
        vehicle_filter = self.maintenance_vehicle_filter.get()
        maintenance_type = self.maintenance_type_var.get()
        start_date = self.maintenance_entry_start_date.get()
        end_date = self.maintenance_entry_end_date.get()

        # Apply filters to entries
        filtered_entries = self.maintenance_entries.copy()

        # Apply search text filter
        if search_text:
            filtered_entries = [
                e for e in filtered_entries if
                search_text in e["title"].lower() or
                search_text in e["description"].lower() or
                search_text in e["vehicle"].lower()
            ]

        if user_search is False and self.active_vehicle is not None:
            vehicle_filter = self.active_vehicle

        # Apply vehicle filter
        if vehicle_filter != "All":
            filtered_entries = [e for e in filtered_entries if vehicle_filter in e["vehicle"]]

        # Apply maintenance type filter
        if maintenance_type != "All":
            filtered_entries = [e for e in filtered_entries if maintenance_type in e.get("tags", [])]

        # Apply date range filter
        if start_date:
            filtered_entries = [e for e in filtered_entries if e["date"] >= start_date]
        if end_date:
            filtered_entries = [e for e in filtered_entries if e["date"] <= end_date]

        # Create cards for filtered entries
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

        # Update statistics if in statistics view
        if self.maintenance_view_selector.get() == "Statistics":
            self.update_statistics()

    def create_maintenance_entry_card(self, title, description, vehicle, date, duration, tags=None, handbook_ref=""):
        """Creates a maintenance entry card"""

        # Create the entry data dictionary
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

        # Top row with title and date
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

        # Vehicle and duration row
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

        # Description
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

        # Add tags if provided
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

        # Action buttons
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
        """Toggle the visibility of advanced search options"""
        if self.advanced_maintenance_search_frame.winfo_ismapped():
            self.advanced_maintenance_search_frame.pack_forget()
            self.maintenance_filter_button.configure(text="Filter", fg_color="#6C7A89", hover_color="#34495E")
        else:
            self.advanced_maintenance_search_frame.pack(fill="x", padx=20, pady=(0, 10))
            self.maintenance_filter_button.configure(text="Hide Filter", fg_color="#E67E22", hover_color="#D35400")

    def clear_maintenance_filters(self):
        """Clear all filters"""
        self.maintenance_vehicle_filter.set("All")
        self.maintenance_entry_start_date.delete(0, 'end')
        self.maintenance_entry_end_date.delete(0, 'end')
        self.maintenance_type_var.set("All")
        self.maintenance_search_entry.delete(0, 'end')
        self.refresh_maintenance_entries()

    def apply_maintenance_filters(self):
        """Apply the selected filters to the maintenance entries"""
        user_search = True
        self.refresh_maintenance_entries(user_search)  # This will apply filters


    def setup_maintenance_statistics_view(self):
        """Set up the statistics view with charts"""
        # Create tabs for different charts
        self.stats_tabs = ctk.CTkTabview(self.maintenance_stats_view_frame)
        self.stats_tabs.pack(fill="both", expand=True, padx=20, pady=20)

        # Create tabs
        self.stats_tabs.add("Maintenance Frequency")
        self.stats_tabs.add("Time Spent")
        self.stats_tabs.add("Vehicle Comparison")

        # Maintenance frequency chart
        freq_frame = ctk.CTkFrame(self.stats_tabs.tab("Maintenance Frequency"), fg_color="transparent")
        freq_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.freq_fig, self.freq_ax = plt.subplots(figsize=(10, 6))
        self.freq_canvas = FigureCanvasTkAgg(self.freq_fig, master=freq_frame)
        self.freq_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Time spent chart
        time_frame = ctk.CTkFrame(self.stats_tabs.tab("Time Spent"), fg_color="transparent")
        time_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.time_fig, self.time_ax = plt.subplots(figsize=(10, 6))
        self.time_canvas = FigureCanvasTkAgg(self.time_fig, master=time_frame)
        self.time_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Vehicle comparison chart
        vehicle_frame = ctk.CTkFrame(self.stats_tabs.tab("Vehicle Comparison"), fg_color="transparent")
        vehicle_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.vehicle_fig, self.vehicle_ax = plt.subplots(figsize=(10, 6))
        self.vehicle_canvas = FigureCanvasTkAgg(self.vehicle_fig, master=vehicle_frame)
        self.vehicle_canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_maintenance_statistics(self):
        """Update all statistics charts with current data"""
        # Clear previous charts
        self.freq_ax.clear()
        self.time_ax.clear()
        self.vehicle_ax.clear()

        if not self.maintenance_entries:
            return

        # Group data
        vehicles = {}
        months = {}
        maintenance_types = {}

        for entry in self.maintenance_entries:
            # Process by vehicle
            vehicle = entry.get("vehicle", "Unknown")
            if vehicle not in vehicles:
                vehicles[vehicle] = {"count": 0, "time": 0}
            vehicles[vehicle]["count"] += 1

            # Extract duration in minutes
            duration_str = entry.get("duration", "0 minutes")
            duration_match = re.search(r'(\d+)\s*(?:hour|hr)s?', duration_str, re.IGNORECASE)
            hours = int(duration_match.group(1)) if duration_match else 0

            duration_match = re.search(r'(\d+)\s*(?:minute|min)s?', duration_str, re.IGNORECASE)
            minutes = int(duration_match.group(1)) if duration_match else 0

            total_minutes = hours * 60 + minutes
            vehicles[vehicle]["time"] += total_minutes

            # Process by month
            date_str = entry.get("date", "2025-01-01")
            month = date_str[:7]  # Get YYYY-MM
            if month not in months:
                months[month] = 0
            months[month] += 1

            # Process by maintenance type
            for tag in entry.get("tags", []):
                if tag not in maintenance_types:
                    maintenance_types[tag] = 0
                maintenance_types[tag] += 1

        # Maintenance frequency chart (by month)
        sorted_months = sorted(months.keys())
        month_counts = [months[m] for m in sorted_months]
        month_labels = [m[5:7] + "/" + m[0:4] for m in sorted_months]  # Format as MM/YYYY

        self.freq_ax.bar(month_labels, month_counts)
        self.freq_ax.set_title('Maintenance Frequency by Month')
        self.freq_ax.set_xlabel('Month')
        self.freq_ax.set_ylabel('Number of Maintenance Tasks')
        self.freq_fig.tight_layout()
        self.freq_canvas.draw()

        # Time spent chart (by maintenance type)
        if maintenance_types:
            types = list(maintenance_types.keys())
            counts = list(maintenance_types.values())

            self.time_ax.pie(counts, labels=types, autopct='%1.1f%%', startangle=90,
                       colors=plt.cm.tab10.colors[:len(types)])
            self.time_ax.set_title('Maintenance Tasks by Type')
            self.time_fig.tight_layout()
            self.time_canvas.draw()

        # Vehicle comparison chart
        if vehicles:
            vehicle_names = list(vehicles.keys())
            counts = [vehicles[v]["count"] for v in vehicle_names]
            times = [vehicles[v]["time"]/60 for v in vehicle_names]  # Convert to hours

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

    def setup_part_inventory_page(self):
        """Placeholder for maintenance log page."""
        label = ctk.CTkLabel(self.tab_part_inventory, text="Part inventory list - Coming Soon", font=("Arial", 16))
        label.pack(pady=20)

    def display_track_days(self):
        """Display stored track days as expandable cards."""
        for widget in self.session_frame.winfo_children():
            widget.destroy()

        # Filter track days based on the active vehicle
        if self.active_vehicle:
            filtered_track_days = [day for day in self.track_days if day.get("vehicle") == self.active_vehicle]
        else:
            filtered_track_days = self.track_days  # Show all track days if no active vehicle is selected

         # Handle case where no track days match the filter

        if not filtered_track_days:
            no_track_days_label = ctk.CTkLabel(
                self.session_frame,
                text="No track days available for the selected vehicle.",
                font=("Arial", 14),
                text_color="gray"
            )
            no_track_days_label.pack(pady=20)
            new_session_button = ctk.CTkButton(self.session_frame, text="+ Create New Track Day",
                                         command=self.create_new_track_day)
            new_session_button.pack(pady=10)
            return

        for idx, track_day in enumerate(filtered_track_days):
            # Create the main card frame
            card = ctk.CTkFrame(self.session_frame, corner_radius=10, border_width=1)
            card.pack(fill="x", pady=5, padx=10)

            # Create header frame for the card
            header_frame = ctk.CTkFrame(card, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=5)

            # Header with basic info
            title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            title_frame.pack(side="left", fill="x", expand=True)

            title = ctk.CTkLabel(title_frame, text=f"{track_day['track']} - {track_day['date']}",
                               font=("Arial", 16, "bold"))
            title.pack(side="top", anchor="w")

            organizer = ctk.CTkLabel(title_frame, text=f"Organizer: {track_day['organizer']}")
            organizer.pack(side="top", anchor="w")

            # Display the associated vehicle
            vehicle_label = ctk.CTkLabel(title_frame, text=f"Vehicle: {track_day.get('vehicle', 'N/A')}")
            vehicle_label.pack(side="top", anchor="w")

            # Buttons frame for actions
            buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            buttons_frame.pack(side="right", padx=10)

            # Delete track day button
            delete_button = ctk.CTkButton(buttons_frame, text="Delete",
                                       width=80, height=32,
                                       command=lambda i=idx: self.delete_track_day(i),
                                       fg_color="#E74C3C",  # Red color
                                       hover_color="#C0392B")  # Darker red on hover
            delete_button.pack(side="left", padx=5)

            # Toggle button
            toggle_button = ctk.CTkButton(buttons_frame, text="View Sessions",
                                        width=120, height=32,
                                        command=lambda i=idx, c=card: self.toggle_sessions_inline(i, c))
            toggle_button.pack(side="left", padx=5)

            # Create hidden content frame for sessions
            content_frame = ctk.CTkFrame(card, fg_color="transparent")
            content_frame.pack(fill="x", padx=10, pady=(0, 10), expand=False)

            # Store reference to content frame and button
            self.session_content_frames[idx] = {
                "frame": content_frame,
                "button": toggle_button,
                "visible": False  # Track visibility state
            }

            # Initially hide the content frame
            content_frame.pack_forget()

        new_session_button = ctk.CTkButton(self.session_frame, text="+ Create New Track Day",
                                         command=self.create_new_track_day)
        new_session_button.pack(pady=10)

    def delete_track_day(self, track_day_idx):
        """Delete a track day with confirmation."""
        track_day = self.track_days[track_day_idx]

        # Create confirmation dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("450x200")
        dialog.transient(self)

        # Ensure the dialog is fully initialized and visible
        dialog.update_idletasks()  # Add this line
        dialog.grab_set()  # Now call grab_set()

        # Container frame with padding
        container = ctk.CTkFrame(dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Warning message
        msg = ctk.CTkLabel(container,
                            text=f"Are you sure you want to delete the track day at {track_day['track']} on {track_day['date']}?\n\nThis will delete ALL sessions from this track day.",
                            wraplength=400,
                            font=("Arial", 14))
        msg.pack(pady=20)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)

        # Cancel button
        cancel_btn = ctk.CTkButton(buttons_frame,
                                    text="Cancel",
                                    command=dialog.destroy,
                                    fg_color="#7F8C8D",  # Gray
                                    hover_color="#5D6D7E",
                                    width=100)
        cancel_btn.pack(side="left", padx=5)

        # Delete button
        def confirm_delete():
            # Remove the track day
            self.track_days.pop(track_day_idx)
            save_data(self.track_days)

            # Clear the reference from session frames dictionary
            if track_day_idx in self.session_content_frames:
                del self.session_content_frames[track_day_idx]

            # Re-index the remaining frames
            new_frames = {}
            for k, v in self.session_content_frames.items():
                if k > track_day_idx:
                    new_frames[k-1] = v
                else:
                    new_frames[k] = v
            self.session_content_frames = new_frames

            # Refresh the display
            self.display_track_days()
            dialog.destroy()

        delete_btn = ctk.CTkButton(buttons_frame,
                                    text="Delete",
                                    command=confirm_delete,
                                    fg_color="#E74C3C",  # Red
                                    hover_color="#C0392B",
                                    width=100)
        delete_btn.pack(side="right", padx=5)

        # Make dialog modal
        dialog.grab_set()
        dialog.wait_window()

    def toggle_sessions_inline(self, idx, card):
        """Toggle the visibility of the sessions within the card."""
        content_data = self.session_content_frames[idx]
        content_frame = content_data["frame"]
        toggle_button = content_data["button"]

        # Toggle visibility state
        is_visible = content_data["visible"]
        content_data["visible"] = not is_visible

        if is_visible:
            # Hide if visible
            content_frame.pack_forget()
            toggle_button.configure(text="View Sessions", fg_color="#1F6AA5", hover_color="#144870")  # Reset to default blue
        else:
            # Show and populate if hidden
            for widget in content_frame.winfo_children():
                widget.destroy()

            # Add divider
            divider = ctk.CTkFrame(content_frame, height=1, fg_color="#D0D3D4")  # Light gray divider
            divider.pack(fill="x", pady=5)

            # Display sessions inside the card
            self.display_sessions_inline(self.track_days[idx], content_frame, idx)

            # Make content visible
            content_frame.pack(fill="x", padx=10, pady=(0, 10), expand=True)

            # Use damped orange for "Hide Sessions" button
            toggle_button.configure(text="Hide Sessions", fg_color="#E67E22", hover_color="#D35400")

    def display_sessions_inline(self, track_day, parent_frame, track_day_idx):
        """Display sessions within the card."""
        if not track_day['sessions']:
            empty_label = ctk.CTkLabel(parent_frame, text="No sessions recorded yet",
                                    text_color="gray")
            empty_label.pack(pady=10)
        else:
            # Create a single container for both header and rows
            table_container = ctk.CTkFrame(parent_frame, fg_color="transparent", corner_radius=0)
            table_container.pack(fill="x", pady=5)

            # Set up grid layout for the entire table
            table_container.columnconfigure(0, weight=1)  # Session #
            table_container.columnconfigure(1, weight=1)  # Laps
            table_container.columnconfigure(2, weight=2)  # Vehicle
            table_container.columnconfigure(3, weight=2)  # Weather
            table_container.columnconfigure(4, weight=2)  # Tire Info
            table_container.columnconfigure(5, weight=2)  # Best Lap

            # Create a header row frame with continuous background
            header_frame = ctk.CTkFrame(table_container, fg_color="#B8C9D6", corner_radius=0)
            header_frame.grid(row=0, column=0, columnspan=6, sticky="ew")

            # Configure header frame columns to match parent
            header_frame.columnconfigure(0, weight=1)
            header_frame.columnconfigure(1, weight=1)
            header_frame.columnconfigure(2, weight=2)
            header_frame.columnconfigure(3, weight=2)
            header_frame.columnconfigure(4, weight=2)
            header_frame.columnconfigure(5, weight=2)

            # Add header labels to the header frame
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

            # Add session rows
            for i, session in enumerate(track_day['sessions']):
                row_index = i + 1  # Start at row 1 (after header)

                # Create row frame with alternating colors and no corner radius
                row_color = "#F5F7FA" if i % 2 == 0 else "#EBEEF2"
                row_frame = ctk.CTkFrame(table_container, fg_color=row_color, corner_radius=0)
                row_frame.grid(row=row_index, column=0, columnspan=6, sticky="ew")

                # Configure row frame columns to match parent
                row_frame.columnconfigure(0, weight=1)
                row_frame.columnconfigure(1, weight=1)
                row_frame.columnconfigure(2, weight=2)
                row_frame.columnconfigure(3, weight=2)
                row_frame.columnconfigure(4, weight=2)
                row_frame.columnconfigure(5, weight=2)

                # Add content to the row with transparent backgrounds
                #TODO: Play around with 'padx' to make the table look nice visually
                session_num = ctk.CTkLabel(row_frame, text=f"#{session.get('session_number', 'N/A')}",
                                        font=("Arial", 11), fg_color="transparent")
                session_num.grid(row=0, column=0, padx=20, pady=3, sticky="w")

                laps_label = ctk.CTkLabel(row_frame, text=f"{session.get('laps', 'N/A')}",
                                        font=("Arial", 11), fg_color="transparent")
                laps_label.grid(row=0, column=1, padx=10, pady=3, sticky="w")

                # Display vehicle (may be empty for older sessions)
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

                # Add hover effect
                def on_enter(event, w=row_frame):
                    w.configure(fg_color="#FAE7A5")  # Yellow color on hover

                def on_leave(event, w=row_frame, c=row_color):
                    w.configure(fg_color=c)  # Reset to original color

                row_frame.bind("<Enter>", on_enter)  # Bind mouse enter event
                row_frame.bind("<Leave>", on_leave)  # Bind mouse leave event

                # Make the row frame respond to right-click
                row_frame.bind("<Button-3>", lambda event, s=session, idx=track_day_idx: self.show_session_context_menu(event, s, idx))

        # Add session button
        add_button_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        add_button_frame.pack(fill="x", pady=5)

        # Dropdown for selecting a session to modify
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

        # Modify button
        modify_button = ctk.CTkButton(
            add_button_frame,
            text="Modify Session",
            command=lambda: self.modify_session_form(track_day_idx, self.modify_session_var.get()),
            fg_color="#3498DB",
            hover_color="#2980B9",
            width=150,
            height=32
        )
        modify_button.pack(side="left", padx=5)

        add_session_button = ctk.CTkButton(add_button_frame, text="+ Add Session",
                                        width=150, height=32,
                                        command=lambda: self.add_session_form(track_day_idx),
                                        fg_color="#2ECC71",  # Green color
                                        hover_color="#27AE60",  # Darker green on hover
                                        text_color="white",)
        add_session_button.pack(side="right", padx=5, pady=5)

    def modify_session_form(self, track_day_idx, session_number):
        """Open a form to modify an existing session."""
        track_day = self.track_days[track_day_idx]
        session = next((s for s in track_day["sessions"] if s.get("session_number") == session_number), None)

        if not session:
            return  # No session found

        # Open the form pre-filled with session data
        self.session_form_window = ctk.CTkToplevel(self)
        self.session_form_window.title("Modify Session")
        self.session_form_window.geometry("550x950")

        # Center window relative to main window
        self.session_form_window.transient(self)
        self.session_form_window.update_idletasks()

        # Add padding around the form
        form_frame = ctk.CTkFrame(self.session_form_window)
        form_frame.pack(fill="both", expand=True, padx=30, pady=30)

        # Pre-fill session fields with existing data
        # ctk.CTkLabel(form_frame, text="Session Number:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(10, 2))
        # self.session_number_entry = ctk.CTkEntry(form_frame, width=450, height=35)
        # self.session_number_entry.insert(0, session.get("session_number", ""))
        # self.session_number_entry.pack(fill="x", pady=(0, 10))

        field_pady = 10  # Increased spacing

        ctk.CTkLabel(form_frame, text="Number of Laps:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
        self.laps_entry = ctk.CTkEntry(form_frame, width=450, height=35)
        self.laps_entry.insert(0, session.get("laps", ""))
        self.laps_entry.pack(fill="x", pady=(0, 10))

        # Weather dropdown
        ctk.CTkLabel(form_frame, text="Weather:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
        self.weather_var = StringVar(value=session.get("weather", self.weather_options[0]))  # Default to first option
        self.weather_dropdown = ctk.CTkOptionMenu(
            form_frame,
            values=self.weather_options,
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
            text_color="#2C3E50")  # Even taller for comments
        self.comments_entry.insert(0, session.get("comments", ""))
        self.comments_entry.pack(fill="x", pady=(0, field_pady))

        # Save button
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

        # Make form modal
        self.session_form_window.grab_set()
        self.session_form_window.focus_set()

    def save_modified_session(self, track_day_idx, session):
        """Save the modified session to the track day."""

        # Update session data with the modified values
        session["laps"] = self.laps_entry.get()
        session["weather"] = self.weather_var.get()
        session["tire_type"] = self.tire_type_entry.get()
        session["tire_status"] = self.tire_status_entry.get()
        session["best_lap_time"] = self.best_lap_time_entry.get()
        session["comments"] = self.comments_entry.get()

        # Save changes to the data file
        save_data(self.track_days)

        # Close the modification form
        self.session_form_window.destroy()

        # Refresh the sessions display if they are currently visible
        content_data = self.session_content_frames.get(track_day_idx)
        if content_data and content_data["visible"]:
            # Refresh the content by toggling twice
            self.toggle_sessions_inline(track_day_idx, None)  # Hide
            self.toggle_sessions_inline(track_day_idx, None)  # Show again

    def show_session_context_menu(self, event, session, track_day_idx):
        """Show a context menu for session row."""
        # This is a placeholder for future functionality
        # You would implement a popup menu with edit/delete options
        pass

    def add_session_form(self, track_day_idx):
        """Open form to add a session."""
        self.session_form_window = ctk.CTkToplevel(self)
        self.session_form_window.title("Add New Session")
        self.session_form_window.geometry("550x650")

        track_day = self.track_days[track_day_idx]
        track_day_vehicle = track_day.get("vehicle", "N/A")

        # Center window relative to main window
        self.session_form_window.transient(self)
        self.session_form_window.update_idletasks()

        # Make the main form scrollable
        scrollable_frame = ctk.CTkScrollableFrame(self.session_form_window)
        scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # --- Mouse wheel support ---
        def _on_mousewheel(event):
            # For Linux, event.num 4/5; for Windows/Mac, event.delta
            if event.num == 4 or event.delta > 0:
                scrollable_frame._parent_canvas.yview_scroll(-1, "units")
            elif event.num == 5 or event.delta < 0:
                scrollable_frame._parent_canvas.yview_scroll(1, "units")

        scrollable_frame._parent_canvas.bind_all("<MouseWheel>", _on_mousewheel)      # Windows/Mac
        scrollable_frame._parent_canvas.bind_all("<Button-4>", _on_mousewheel)        # Linux scroll up
        scrollable_frame._parent_canvas.bind_all("<Button-5>", _on_mousewheel)        # Linux scroll down

        # Unbind on close to prevent errors in other windows
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
            vehicle_value = track_day_vehicle
        else:
            ctk.CTkLabel(scrollable_frame, text="Vehicle:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
            vehicle_var = StringVar(value=self.vehicles[0])
            vehicle_dropdown = ctk.CTkOptionMenu(
                scrollable_frame,
                values=self.vehicles,
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
            vehicle_value = vehicle_var

        ctk.CTkLabel(scrollable_frame, text="Weather:", anchor="w", font=("Arial", 12)).pack(fill="x", pady=(field_pady, 2))
        weather_var = StringVar(value=self.weather_options[0])
        weather_dropdown = ctk.CTkOptionMenu(
            scrollable_frame,
            values=self.weather_options,
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

        # Button frame (not scrollable, stays at the bottom)
        button_frame = ctk.CTkFrame(self.session_form_window, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 10), side="bottom")

        def save_session():
            # Get values from form
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

            # Create session dict
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

            # Append to sessions list
            self.track_days[track_day_idx]["sessions"].append(new_session)
            save_data(self.track_days)
            self.session_form_window.destroy()
            self.display_track_days()
            cleanup_mousewheel_bindings()

        # Cancel button
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

        # Save session button
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

        # Make form window modal
        self.session_form_window.grab_set()
        self.session_form_window.focus_set()


    def create_new_track_day(self):
        """Popup for entering new track day details."""
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

        # Vehicle Selection Dropdown
        ctk.CTkLabel(self.new_window, text="Vehicle Used:").pack()
        self.vehicle_var = StringVar(value=self.vehicles[0] if self.vehicles else "No Vehicles Available")
        self.vehicle_dropdown = ctk.CTkOptionMenu(
            self.new_window,
            values=self.vehicles if self.vehicles else ["No Vehicles Available"],
            variable=self.vehicle_var
        )
        self.vehicle_dropdown.pack()

        save_button = ctk.CTkButton(self.new_window, text="Save", command=self.save_track_day)
        save_button.pack(pady=10)


    def save_track_day(self):
        """Save new track day entry."""
        selected_vehicle = self.vehicle_var.get()

        # Ensure a valid vehicle is selected
        if not self.vehicles or selected_vehicle == "No Vehicles Available":
            ctk.CTkLabel(self.new_window, text="Please add a vehicle before creating a track day.", text_color="red").pack()
            return

        new_day = {
            "track": self.track_entry.get(),
            "date": self.date_entry.get(),
            "organizer": self.organizer_entry.get(),
            "vehicle": selected_vehicle,
            "sessions": []
        }

        self.track_days.append(new_day)
        save_data(self.track_days)
        self.new_window.destroy()
        self.display_track_days()

if __name__ == "__main__":
    app = RacingDiaryApp()
    app.mainloop()