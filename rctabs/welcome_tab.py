# Welcome tab for Racing Companion
# Author: dherslof

import customtkinter as ctk
from tkinter import StringVar
from datetime import datetime
from data_utils import save_vehicles

class WelcomePage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.setup_welcome_page()

    def setup_welcome_page(self):
        # Main container
        welcome_container = ctk.CTkFrame(self, fg_color="transparent")
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

        if not self.app.vehicles:
            empty_label = ctk.CTkLabel(self.vehicles_container, text="No vehicles added yet. Click '+ Add Vehicle' to add one.",
                                    font=("Arial", 14), text_color="gray")
            empty_label.pack(pady=20)
            return

        grid_frame = ctk.CTkFrame(self.vehicles_container, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.columnconfigure(2, weight=1)

        for i, vehicle in enumerate(self.app.vehicles):
            row = i // 3
            col = i % 3
            card_color = "#D4EFDF" if vehicle == self.app.active_vehicle else "#eeeeee"
            card = ctk.CTkFrame(grid_frame, corner_radius=10, border_width=1, fg_color=card_color)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")

            content_frame = ctk.CTkFrame(card, fg_color="transparent")
            content_frame.pack(fill="both", expand=True, padx=15, pady=15)

            vehicle_type = self.app.vehicle_data.get(vehicle, {}).get('type', 'Car')
            abbreviations = {
                "Car": "CAR",
                "Motorcycle": "MC",
                "Quad": "QUAD",
                "Snowmobile": "SLED"
            }
            vehicle_type_abbr = abbreviations.get(vehicle_type, vehicle_type[:4].upper())

            icon_frame = ctk.CTkFrame(content_frame, width=40, height=40,
                                    corner_radius=20, fg_color="#3498DB")
            icon_frame.pack(pady=5)
            icon_frame.pack_propagate(False)
            icon_label = ctk.CTkLabel(icon_frame, text=vehicle_type_abbr,
                                    font=("Arial", 10, "bold"),
                                    text_color="white", anchor="center")
            icon_label.pack(expand=True, padx=5, pady=5)

            name_label = ctk.CTkLabel(content_frame, text=vehicle, font=("Arial", 14, "bold"))
            name_label.pack(pady=5)

            button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            button_frame.pack(fill="x", pady=10)

            edit_btn = ctk.CTkButton(button_frame,
                                    text="Edit",
                                    command=lambda v=vehicle: self.edit_vehicle(v),
                                    fg_color="#6C7A89",
                                    width=40,
                                    height=28)
            edit_btn.pack(side="left", padx=5)

            delete_btn = ctk.CTkButton(button_frame,
                                    text="Delete",
                                    command=lambda v=vehicle: self.delete_vehicle(v),
                                    fg_color="#E74C3C",
                                    hover_color="#C0392B",
                                    width=40,
                                    height=28)
            delete_btn.pack(side="right", padx=5)

            select_btn_text = "Unselect" if vehicle == self.app.active_vehicle else "Select"
            select_btn = ctk.CTkButton(button_frame,
                                    text=select_btn_text,
                                    command=lambda v=vehicle: self.toggle_active_vehicle(v),
                                    fg_color="#3498DB",
                                    hover_color="#2980B9",
                                    width=80,
                                    height=28)
            select_btn.pack(side="left", padx=5)

            def on_enter(event, w=card, v=vehicle):
                if v != self.app.active_vehicle:
                    w.configure(fg_color="#D4EFDF")
            def on_leave(event, w=card, v=vehicle):
                if v != self.app.active_vehicle:
                    w.configure(fg_color="#eeeeee")
            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)

    def toggle_active_vehicle(self, vehicle):
        """Set the selected vehicle as the active vehicle."""
        if self.app.active_vehicle == vehicle:
            self.app.active_vehicle = None
        else:
            self.app.active_vehicle = vehicle

        self.display_vehicles()
        if hasattr(self.app, "sessions_page"):
            self.app.sessions_page.display_track_days()
        if hasattr(self.app, "maintenance_page"):
            self.app.maintenance_page.refresh_maintenance_entries()
        if hasattr(self.app, "update_footer"):
            self.app.update_footer()

    def show_add_vehicle_dialog(self):
        """Display dialog for adding a new vehicle."""
        dialog = ctk.CTkToplevel(self.app)
        dialog.title("Add New Vehicle")
        dialog.geometry("400x500")
        dialog.transient(self.app)
        dialog.update_idletasks()

        container = ctk.CTkFrame(dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(container, text="Add New Vehicle", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        ctk.CTkLabel(container, text="Vehicle Name:", anchor="w").pack(fill="x", pady=(10, 0))
        vehicle_entry = ctk.CTkEntry(container, height=35, fg_color="#F5F7FA")
        vehicle_entry.pack(fill="x", pady=(5, 15))
        vehicle_entry.focus()

        ctk.CTkLabel(container, text="Vehicle Type:", anchor="w").pack(fill="x", pady=(10, 0))
        vehicle_type_var = StringVar(value="Car")
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

        ctk.CTkLabel(container, text="Model Year:", anchor="w").pack(fill="x", pady=(10, 0))
        model_year_var = StringVar(value=str(datetime.now().year))
        model_year_dropdown = ctk.CTkOptionMenu(
            container,
            values=[str(year) for year in range(1980, datetime.now().year + 1)],
            variable=model_year_var,
            fg_color="#F5F7FA",
            button_color="#D0D3D4",
            button_hover_color="#B3B6B7",
            dropdown_fg_color="#F5F7FA",
            text_color="#2C3E50"
        )
        model_year_dropdown.pack(fill="x", pady=(5, 15))

        ctk.CTkLabel(container, text="Miscellaneous Info:", anchor="w").pack(fill="x", pady=(10, 0))
        misc_entry = ctk.CTkEntry(container, height=35, fg_color="#F5F7FA")
        misc_entry.pack(fill="x", pady=(5, 15))

        buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)

        cancel_btn = ctk.CTkButton(buttons_frame,
                                text="Cancel",
                                command=dialog.destroy,
                                fg_color="#E74C3C",
                                hover_color="#C0392B",
                                width=100)
        cancel_btn.pack(side="left", padx=5)

        def save_new_vehicle():
            vehicle_name = vehicle_entry.get().strip()
            vehicle_type = vehicle_type_var.get()
            model_year = model_year_var.get()
            misc = misc_entry.get().strip()
            if vehicle_name:
                self.app.vehicles.append(vehicle_name)
                self.app.vehicle_data[vehicle_name] = {
                  'type': vehicle_type,
                  'year': model_year,
                  'misc': misc
                }
                save_vehicles(self.app.vehicles, self.app.vehicle_data)
                self.display_vehicles()
                dialog.destroy()

        save_btn = ctk.CTkButton(buttons_frame,
                                text="Save",
                                command=save_new_vehicle,
                                fg_color="#2ECC71",
                                hover_color="#27AE60",
                                width=100)
        save_btn.pack(side="right", padx=5)

        dialog.grab_set()
        dialog.wait_window()

    def edit_vehicle(self, vehicle):
        """Edit an existing vehicle."""
        dialog = ctk.CTkToplevel(self.app)
        dialog.title("Edit Vehicle")
        dialog.geometry("400x500")
        dialog.transient(self.app)
        dialog.update_idletasks()

        container = ctk.CTkFrame(dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        title = ctk.CTkLabel(container, text="Edit Vehicle", font=("Arial", 16, "bold"))
        title.pack(pady=10)

        vehicle_data = self.app.vehicle_data.get(vehicle, {})

        ctk.CTkLabel(container, text="Vehicle Name:", anchor="w").pack(fill="x", pady=(10, 0))
        vehicle_entry = ctk.CTkEntry(container, height=35, fg_color="#F5F7FA")
        vehicle_entry.pack(fill="x", pady=(5, 15))
        vehicle_entry.insert(0, vehicle)
        vehicle_entry.focus()

        ctk.CTkLabel(container, text="Vehicle Type:", anchor="w").pack(fill="x", pady=(10, 0))
        current_type = vehicle_data.get('type', "Car")
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

        ctk.CTkLabel(container, text="Model Year:", anchor="w").pack(fill="x", pady=(10, 0))
        current_year = str(vehicle_data.get('year', datetime.now().year))
        model_year_var = StringVar(value=current_year)
        model_year_dropdown = ctk.CTkOptionMenu(
            container,
            values=[str(year) for year in range(1980, datetime.now().year + 1)],
            variable=model_year_var,
            fg_color="#F5F7FA",
            button_color="#D0D3D4",
            button_hover_color="#B3B6B7",
            dropdown_fg_color="#F5F7FA",
            text_color="#2C3E50"
        )
        model_year_dropdown.pack(fill="x", pady=(5, 15))

        ctk.CTkLabel(container, text="Miscellaneous Info:", anchor="w").pack(fill="x", pady=(10, 0))
        misc_entry = ctk.CTkEntry(container, height=35, fg_color="#F5F7FA")
        misc_entry.pack(fill="x", pady=(5, 15))
        misc_entry.insert(0, vehicle_data.get('misc', ''))

        buttons_frame = ctk.CTkFrame(container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=10)

        cancel_btn = ctk.CTkButton(buttons_frame,
                                    text="Cancel",
                                    command=dialog.destroy,
                                    fg_color="#E74C3C",
                                    hover_color="#C0392B",
                                    width=100)
        cancel_btn.pack(side="left", padx=5)

        def save_edited_vehicle():
            new_name = vehicle_entry.get().strip()
            new_type = vehicle_type_var.get()
            new_year = model_year_var.get()
            new_misc = misc_entry.get().strip()

            if new_name:
                if new_name != vehicle:
                    index = self.app.vehicles.index(vehicle)
                    self.app.vehicles[index] = new_name
                    self.app.vehicle_data[new_name] = self.app.vehicle_data.pop(vehicle, {})
                self.app.vehicle_data[new_name] = {
                    'type': new_type,
                    'year': new_year,
                    'misc': new_misc
                }
                save_vehicles(self.app.vehicles, self.app.vehicle_data)
                self.display_vehicles()
                dialog.destroy()

        save_btn = ctk.CTkButton(buttons_frame,
                                text="Save",
                                command=save_edited_vehicle,
                                fg_color="#2ECC71",
                                hover_color="#27AE60",
                                width=100)
        save_btn.pack(side="right", padx=5)

        dialog.grab_set()
        dialog.wait_window()

    def delete_vehicle(self, vehicle):
        """Delete a vehicle with confirmation."""
        dialog = ctk.CTkToplevel(self.app)
        dialog.title("Confirm Delete")
        dialog.geometry("400x180")
        dialog.transient(self.app)
        dialog.update_idletasks()

        container = ctk.CTkFrame(dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        msg = ctk.CTkLabel(container,
                        text=f"Are you sure you want to delete '{vehicle}'?",
                        wraplength=350,
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
            self.app.vehicles.remove(vehicle)
            if vehicle in self.app.vehicle_data:
                del self.app.vehicle_data[vehicle]
            save_vehicles(self.app.vehicles, self.app.vehicle_data)
            self.display_vehicles()
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