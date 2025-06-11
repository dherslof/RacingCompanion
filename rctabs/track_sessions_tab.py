import customtkinter as ctk
from tkinter import StringVar
from rcfunc.data_utils import save_data

class TrackSessionsPage(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.track_days = self.app.track_days
        self.vehicles = self.app.vehicles
        self.active_vehicle = self.app.active_vehicle
        self.weather_options = self.app.weather_options
        self.session_content_frames = {}

        self.setup_track_sessions_page()

    def setup_track_sessions_page(self):
        """Track session logging with card-style design."""
        self.session_frame = ctk.CTkFrame(self)
        self.session_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.display_track_days()

    def display_track_days(self):
        """Display stored track days as expandable cards."""
        for widget in self.session_frame.winfo_children():
            widget.destroy()

        # Always use up-to-date data
        self.track_days = self.app.track_days
        self.vehicles = self.app.vehicles
        self.active_vehicle = self.app.active_vehicle

        # Filter track days based on the active vehicle
        if self.active_vehicle:
            filtered_track_days = [day for day in self.track_days if day.get("vehicle") == self.active_vehicle]
        else:
            filtered_track_days = self.track_days  # Show all track days if no active vehicle is selected

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
                                       command=lambda i=idx: self.delete_track_day(i),
                                       fg_color="#E74C3C",
                                       hover_color="#C0392B")
            delete_button.pack(side="left", padx=5)

            toggle_button = ctk.CTkButton(buttons_frame, text="View Sessions",
                                        width=120, height=32,
                                        command=lambda i=idx, c=card: self.toggle_sessions_inline(i, c))
            toggle_button.pack(side="left", padx=5)

            content_frame = ctk.CTkFrame(card, fg_color="transparent")
            content_frame.pack(fill="x", padx=10, pady=(0, 10), expand=False)

            self.session_content_frames[idx] = {
                "frame": content_frame,
                "button": toggle_button,
                "visible": False
            }
            content_frame.pack_forget()

        new_session_button = ctk.CTkButton(self.session_frame, text="+ Create New Track Day",
                                         command=self.create_new_track_day)
        new_session_button.pack(pady=10)

    def delete_track_day(self, track_day_idx):
        """Delete a track day with confirmation."""
        track_day = self.track_days[track_day_idx]

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
            self.track_days.pop(track_day_idx)
            save_data(self.track_days)
            if track_day_idx in self.session_content_frames:
                del self.session_content_frames[track_day_idx]
            new_frames = {}
            for k, v in self.session_content_frames.items():
                if k > track_day_idx:
                    new_frames[k-1] = v
                else:
                    new_frames[k] = v
            self.session_content_frames = new_frames
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
            self.display_sessions_inline(self.track_days[idx], content_frame, idx)
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
            fg_color="#3498DB",
            hover_color="#2980B9",
            width=150,
            height=32
        )
        modify_button.pack(side="left", padx=5)

        add_session_button = ctk.CTkButton(add_button_frame, text="+ Add Session",
                                        width=150, height=32,
                                        command=lambda: self.add_session_form(track_day_idx),
                                        fg_color="#2ECC71",
                                        hover_color="#27AE60",
                                        text_color="white",)
        add_session_button.pack(side="right", padx=5, pady=5)

    def modify_session_form(self, track_day_idx, session_number):
        track_day = self.track_days[track_day_idx]
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
        self.weather_var = StringVar(value=session.get("weather", self.weather_options[0]))
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
        save_data(self.track_days)
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

        track_day = self.track_days[track_day_idx]
        track_day_vehicle = track_day.get("vehicle", "N/A")

        self.session_form_window.transient(self)
        self.session_form_window.update_idletasks()

        scrollable_frame = ctk.CTkScrollableFrame(self.session_form_window)
        scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)

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

            self.track_days[track_day_idx]["sessions"].append(new_session)
            save_data(self.track_days)
            self.session_form_window.destroy()
            self.display_track_days()
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
        selected_vehicle = self.vehicle_var.get()
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