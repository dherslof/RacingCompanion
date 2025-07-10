import customtkinter as ctk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Dict, Any, Optional

# Import the business logic layer
from rcfunc.maintenance_mngr import MaintenanceMngr, MaintenanceEntry, MaintenanceFilter

class MaintenancePage(ctk.CTkFrame):
   """GUI layer for maintenance management"""
   def __init__(self, master, app):
      super().__init__(master)
      self.app = app
      self.maintenance_manager = MaintenanceMngr(
         vehicles=app.vehicles,
         active_vehicle=app.active_vehicle
      )
      self.current_filter = MaintenanceFilter()
      self.advanced_search_visible = False
      self.setup_maintenance_page()

   def setup_maintenance_page(self):
      self._create_header()
      self._create_search_and_filter()
      self._create_advanced_search()
      self._create_views()
      self._setup_statistics_view()
      self.refresh_maintenance_entries()

   def _create_header(self):
      self.maintenance_header_frame = ctk.CTkFrame(self, fg_color="transparent")
      self.maintenance_header_frame.pack(fill="x", padx=20, pady=(20, 10))
      self.maintenance_title_label = ctk.CTkLabel(
         self.maintenance_header_frame,
         text="Maintenance Log",
         font=ctk.CTkFont(size=24, weight="bold")
      )
      self.maintenance_title_label.pack(side="left")
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

   def _create_search_and_filter(self):
      self.maintenance_search_frame = ctk.CTkFrame(self, fg_color="transparent")
      self.maintenance_search_frame.pack(fill="x", padx=20, pady=10)
      self.maintenance_search_entry = ctk.CTkEntry(
         self.maintenance_search_frame,
         placeholder_text="Search entries..."
      )
      self.maintenance_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
      self.maintenance_search_entry.bind("<KeyRelease>", self._on_search_changed)
      self.maintenance_filter_button = ctk.CTkButton(
         self.maintenance_search_frame,
         text="Filter",
         width=80,
         fg_color="#6C7A89",
         command=self.toggle_advanced_search
      )
      self.maintenance_filter_button.pack(side="right")

   def _create_advanced_search(self):
      self.advanced_maintenance_search_frame = ctk.CTkFrame(self, fg_color="#F5F7FA")
      vehicle_frame = ctk.CTkFrame(self.advanced_maintenance_search_frame, fg_color="transparent")
      vehicle_frame.pack(fill="x", pady=5)
      ctk.CTkLabel(vehicle_frame, text="Vehicle:").pack(side="left", padx=(0, 10))

      filter_vehicle_options = ["All"] + self.maintenance_manager.get_available_vehicles()
      self.maintenance_vehicle_filter = ctk.CTkComboBox(vehicle_frame, values=filter_vehicle_options)
      self.maintenance_vehicle_filter.pack(side="left", fill="x", expand=True)

      active_vehicle = self.maintenance_manager.get_active_vehicle()
      if active_vehicle:
         self.maintenance_vehicle_filter.set(active_vehicle)
      else:
         self.maintenance_vehicle_filter.set("All")

      date_frame = ctk.CTkFrame(self.advanced_maintenance_search_frame, fg_color="transparent")
      date_frame.pack(fill="x", pady=5)
      ctk.CTkLabel(date_frame, text="Date range:").pack(side="left", padx=(0, 10))

      self.maintenance_entry_start_date = ctk.CTkEntry(date_frame, placeholder_text="YYYY-MM-DD")
      self.maintenance_entry_start_date.pack(side="left", padx=(0, 5))
      ctk.CTkLabel(date_frame, text="to").pack(side="left", padx=5)
      self.maintenance_entry_end_date = ctk.CTkEntry(date_frame, placeholder_text="YYYY-MM-DD")
      self.maintenance_entry_end_date.pack(side="left", padx=(5, 0))

      type_frame = ctk.CTkFrame(self.advanced_maintenance_search_frame, fg_color="transparent")
      type_frame.pack(fill="x", pady=5)
      ctk.CTkLabel(type_frame, text="Type:").pack(side="left", padx=(0, 10))
      self.maintenance_type_var = ctk.StringVar(value="All")
      types = ["All", "Routine", "Repair", "Major", "Preventive"]

      for t in types:
         ctk.CTkRadioButton(type_frame, text=t, variable=self.maintenance_type_var, value=t).pack(side="left", padx=10)

      filter_button_frame = ctk.CTkFrame(self.advanced_maintenance_search_frame, fg_color="transparent")
      filter_button_frame.pack(fill="x", pady=10)
      ctk.CTkButton(filter_button_frame, text="Apply Filters", command=self.apply_maintenance_filters).pack(side="right")
      ctk.CTkButton(filter_button_frame, text="Clear", command=self.clear_maintenance_filters,
         fg_color="#6C7A89").pack(side="right", padx=10)

   def _create_views(self):
      self.maintenance_list_view_frame = ctk.CTkFrame(self, fg_color="transparent")
      self.maintenance_list_view_frame.pack(fill="both", expand=True)
      self.maintenance_entries_container = ctk.CTkScrollableFrame(
         self.maintenance_list_view_frame,
         fg_color="transparent"
      )
      self.maintenance_entries_container.pack(fill="both", expand=True, padx=20, pady=20)
      self.maintenance_stats_view_frame = ctk.CTkFrame(self, fg_color="transparent")
      
      def _on_mousewheel(event):
        if event.num == 4 or event.delta > 0:
            self.maintenance_entries_container._parent_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.maintenance_entries_container._parent_canvas.yview_scroll(1, "units")

      self.maintenance_entries_container._parent_canvas.bind_all("<MouseWheel>", _on_mousewheel)
      self.maintenance_entries_container._parent_canvas.bind_all("<Button-4>", _on_mousewheel)
      self.maintenance_entries_container._parent_canvas.bind_all("<Button-5>", _on_mousewheel)

   def _setup_statistics_view(self):
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

   def _on_search_changed(self, event=None):
      self.current_filter.search_text = self.maintenance_search_entry.get()
      self.refresh_maintenance_entries(user_search=True)

   def switch_maintenance_view(self, view):
      if view == "List View":
         self.maintenance_stats_view_frame.pack_forget()
         self.maintenance_list_view_frame.pack(fill="both", expand=True)
      else:
         self.maintenance_list_view_frame.pack_forget()
         self.maintenance_stats_view_frame.pack(fill="both", expand=True)
         self.update_maintenance_statistics()

   def toggle_advanced_search(self):
      if self.advanced_search_visible:
         self.advanced_maintenance_search_frame.pack_forget()
         self.maintenance_filter_button.configure(text="Filter", fg_color="#6C7A89", hover_color="#34495E")
         self.advanced_search_visible = False
      else:
         self.advanced_maintenance_search_frame.pack(fill="x", padx=20, pady=(0, 10))
         self.maintenance_filter_button.configure(text="Hide Filter", fg_color="#E67E22", hover_color="#D35400")
         self.advanced_search_visible = True

   def apply_maintenance_filters(self):
      self.current_filter.vehicle = self.maintenance_vehicle_filter.get()
      self.current_filter.maintenance_type = self.maintenance_type_var.get()
      self.current_filter.start_date = self.maintenance_entry_start_date.get()
      self.current_filter.end_date = self.maintenance_entry_end_date.get()
      self.refresh_maintenance_entries(user_search=True)

   def clear_maintenance_filters(self):
      self.maintenance_vehicle_filter.set("All")
      self.maintenance_entry_start_date.delete(0, 'end')
      self.maintenance_entry_end_date.delete(0, 'end')
      self.maintenance_type_var.set("All")
      self.maintenance_search_entry.delete(0, 'end')
      self.current_filter = MaintenanceFilter()
      self.refresh_maintenance_entries()

   def add_new_maintenance_entry(self):
      MaintenanceEntryDialog(self.app, self.maintenance_manager, self._on_entry_saved)

   def edit_maintenance_entry(self, entry: MaintenanceEntry):
      MaintenanceEntryDialog(self.app, self.maintenance_manager, self._on_entry_saved, entry)

   def delete_maintenance_entry(self, entry: MaintenanceEntry):
      if messagebox.askyesno("Confirm Delete", f"Delete maintenance entry '{entry.title}'?"):
         if self.maintenance_manager.delete_entry(entry):
            self.refresh_maintenance_entries()
         else:
            messagebox.showerror("Error", "Failed to delete entry")

   def _on_entry_saved(self):
      self.refresh_maintenance_entries()

   def refresh_maintenance_entries(self, user_search=False):
      for widget in self.maintenance_entries_container.winfo_children():
         widget.destroy()
      filtered_entries = self.maintenance_manager.filter_entries(
         self.current_filter,
         use_active_vehicle=not user_search
      )

      reversed_maintenance_entries = list(reversed(filtered_entries))
      for entry in reversed_maintenance_entries:
         self._create_maintenance_entry_card(entry)
      if self.maintenance_view_selector.get() == "Statistics":
         self.update_maintenance_statistics()

   def _create_maintenance_entry_card(self, entry: MaintenanceEntry):
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
         text=entry.title,
         font=ctk.CTkFont(size=16, weight="bold"),
         anchor="w"
      )
      title_label.pack(side="left")
      date_label = ctk.CTkLabel(
         top_row,
         text=entry.date,
         font=ctk.CTkFont(size=14),
         text_color="#6C7A89"
      )
      date_label.pack(side="right")
      info_row = ctk.CTkFrame(card, fg_color="transparent")
      info_row.pack(fill="x", padx=15, pady=5)
      vehicle_label = ctk.CTkLabel(
         info_row,
         text=f"Vehicle: {entry.vehicle}",
         font=ctk.CTkFont(size=14),
         anchor="w"
      )
      vehicle_label.pack(side="left")
      duration_label = ctk.CTkLabel(
         info_row,
         text=f"Duration: {entry.duration}",
         font=ctk.CTkFont(size=14),
         text_color="#6C7A89"
      )
      duration_label.pack(side="right")
      desc_frame = ctk.CTkFrame(card, fg_color="transparent")
      desc_frame.pack(fill="x", padx=15, pady=(5, 10))
      desc_label = ctk.CTkLabel(
         desc_frame,
         text=entry.description,
         font=ctk.CTkFont(size=14),
         anchor="w",
         justify="left",
         wraplength=500
      )
      desc_label.pack(side="left", fill="x")
      if entry.tags:
         tags_frame = ctk.CTkFrame(card, fg_color="transparent")
         tags_frame.pack(fill="x", padx=15, pady=(0, 10))
         for tag in entry.tags:
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

   def update_maintenance_statistics(self):
      self._update_frequency_chart()
      self._update_time_chart()
      self._update_vehicle_chart()

   def _update_frequency_chart(self):
      self.freq_ax.clear()
      chart_data = self.maintenance_manager.get_chart_data("frequency")
      if chart_data.get("labels"):
         self.freq_ax.bar(chart_data["labels"], chart_data["values"])
         self.freq_ax.set_title(chart_data["title"])
         self.freq_ax.set_xlabel(chart_data["xlabel"])
         self.freq_ax.set_ylabel(chart_data["ylabel"])
      self.freq_fig.tight_layout()
      self.freq_canvas.draw()

   def _update_time_chart(self):
      self.time_ax.clear()
      chart_data = self.maintenance_manager.get_chart_data("pie")
      if chart_data.get("labels"):
         self.time_ax.pie(
            chart_data["values"],
            labels=chart_data["labels"],
            autopct='%1.1f%%',
            startangle=90,
            colors=plt.cm.tab10.colors[:len(chart_data["labels"])]
         )
         self.time_ax.set_title(chart_data["title"])
      self.time_fig.tight_layout()
      self.time_canvas.draw()

   def _update_vehicle_chart(self):
      self.vehicle_ax.clear()
      chart_data = self.maintenance_manager.get_chart_data("vehicle_comparison")
      if chart_data.get("vehicle_names"):
         x = np.arange(len(chart_data["vehicle_names"]))
         width = 0.35
         self.vehicle_ax.bar(x - width/2, chart_data["counts"], width, label='# of Tasks')
         self.vehicle_ax.bar(x + width/2, chart_data["times"], width, label='Hours Spent')
         self.vehicle_ax.set_title(chart_data["title"])
         self.vehicle_ax.set_xticks(x)
         self.vehicle_ax.set_xticklabels(chart_data["vehicle_names"])
         self.vehicle_ax.legend()
         self.vehicle_ax.set_ylabel('Count / Hours', loc='center')
      self.vehicle_fig.tight_layout()
      self.vehicle_fig.subplots_adjust(left=0.10)
      self.vehicle_canvas.draw()

class MaintenanceEntryDialog:
   """Dialog for adding/editing maintenance entries"""
   def __init__(self, parent, maintenance_manager: MaintenanceMngr,
             callback, entry_to_edit: Optional[MaintenanceEntry] = None):
      self.parent = parent
      self.maintenance_manager = maintenance_manager
      self.callback = callback
      self.entry_to_edit = entry_to_edit
      self.is_editing = entry_to_edit is not None
      self._create_dialog()
      self._setup_form()
      if self.is_editing:
         self._populate_form()

   def _create_dialog(self):
      self.dialog = ctk.CTkToplevel(self.parent)
      title = "Edit Maintenance Entry" if self.is_editing else "Add Maintenance Entry"
      self.dialog.title(title)
      self.dialog.geometry("520x600")
      self.dialog.transient(self.parent)
      self.parent.after(100, self._setup_dialog_focus)

   def _setup_dialog_focus(self):
      try:
         self.dialog.grab_set()
         self.dialog.focus_set()
      except Exception as e:
         # Todo: Write a proper error log, displayed in the GUI somewhere.
         print(f"Error setting dialog focus: {e}")
         pass

   def _setup_form(self):
      form_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
      form_frame.pack(fill="both", expand=True, padx=20, pady=20)

      title_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
      title_frame.pack(fill="x", pady=(0, 10))
      ctk.CTkLabel(title_frame, text="Title:").pack(side="left", padx=(0, 10))

      self.title_entry = ctk.CTkEntry(title_frame, placeholder_text="Maintenance title...")
      self.title_entry.pack(side="left", fill="x", expand=True)
      vehicle_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
      vehicle_frame.pack(fill="x", pady=10)
      ctk.CTkLabel(vehicle_frame, text="Vehicle:").pack(side="left", padx=(0, 10))

      self.vehicle_combo = ctk.CTkComboBox(
         vehicle_frame, 
         values=self.maintenance_manager.get_available_vehicles()
      )
      self.vehicle_combo.pack(side="left", fill="x", expand=True)
      date_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
      date_frame.pack(fill="x", pady=10)
      ctk.CTkLabel(date_frame, text="Date:").pack(side="left", padx=(0, 10))

      self.date_entry = ctk.CTkEntry(date_frame, placeholder_text="YYYY-MM-DD")
      self.date_entry.pack(side="left", fill="x", expand=True)
      duration_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
      duration_frame.pack(fill="x", pady=10)
      ctk.CTkLabel(duration_frame, text="Duration:").pack(side="left", padx=(0, 10))
      self.duration_entry = ctk.CTkEntry(duration_frame, placeholder_text="e.g. 1 hour 30 minutes")
      self.duration_entry.pack(side="left", fill="x", expand=True)

      hb_ref_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
      hb_ref_frame.pack(fill="x", pady=(0, 10))
      ctk.CTkLabel(hb_ref_frame, text="Handbook/Manual Ref:").pack(side="left", padx=(0, 10))
      self.hb_ref_entry = ctk.CTkEntry(hb_ref_frame, placeholder_text="Haynes manual 6.7")
      self.hb_ref_entry.pack(side="left", fill="x", expand=True)

      tags_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
      tags_frame.pack(fill="x", pady=(5, 5))
      ctk.CTkLabel(tags_frame, text="Tags:").pack(side="left", padx=(0, 10))
      tags_subframe = ctk.CTkFrame(tags_frame, fg_color="transparent")
      tags_subframe.pack(side="left", fill="x", expand=True)
      self.tag_vars = {}
      tags = ["Routine", "Repair", "Major", "Minor", "Preventive", "Oil",
            "Tires", "Engine", "Chassis", "Brakes", "Update", "Electronics"]
      columns = 4

      for i, tag in enumerate(tags):
         var = ctk.BooleanVar(value=False)
         self.tag_vars[tag] = var
         row = i // columns
         col = i % columns
         ctk.CTkCheckBox(tags_subframe, text=tag, variable=var).grid(
            row=row, column=col, padx=5, pady=5, sticky="w"
         )
      desc_label = ctk.CTkLabel(form_frame, text="Description:")
      desc_label.pack(anchor="w", pady=(5, 5))
      self.desc_text = ctk.CTkTextbox(form_frame, height=150)
      self.desc_text.pack(fill="x", expand=True)

      button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
      button_frame.pack(fill="x", pady=(20, 0))
      ctk.CTkButton(
         button_frame,
         text="Cancel",
         command=self._cancel,
         fg_color="#E74C3C",
         hover_color="#C0392B",
         width=100
      ).pack(side="right", padx=(10, 0))

      save_text = "Update" if self.is_editing else "Save"
      ctk.CTkButton(
         button_frame,
         text=save_text,
         command=self._save_entry,
         fg_color="#2ECC71",
         hover_color="#27AE60",
         width=100
      ).pack(side="right")

   def _populate_form(self):
      if not self.entry_to_edit:
         return
      self.title_entry.insert(0, self.entry_to_edit.title)
      self.vehicle_combo.set(self.entry_to_edit.vehicle)
      self.date_entry.insert(0, self.entry_to_edit.date)
      self.duration_entry.insert(0, self.entry_to_edit.duration)
      self.hb_ref_entry.insert(0, self.entry_to_edit.handbook_ref)
      self.desc_text.insert("1.0", self.entry_to_edit.description)
      for tag in self.entry_to_edit.tags:
         if tag in self.tag_vars:
            self.tag_vars[tag].set(True)

   def _get_form_data(self) -> Dict[str, Any]:
      return {
         "title": self.title_entry.get(),
         "vehicle": self.vehicle_combo.get(),
         "date": self.date_entry.get(),
         "duration": self.duration_entry.get(),
         "handbook_ref": self.hb_ref_entry.get(),
         "description": self.desc_text.get("1.0", "end-1c"),
         "tags": [tag for tag, var in self.tag_vars.items() if var.get()]
      }

   def _save_entry(self):
      entry_data = self._get_form_data()
      is_valid, errors = self.maintenance_manager.validate_entry_data(entry_data)
      if not is_valid:
         error_message = "Please fix the following errors:\n\n" + "\n".join(f"• {error}" for error in errors)
         messagebox.showerror("Validation Error", error_message, parent=self.dialog)
         return
      try:
         if self.is_editing:
            self.maintenance_manager.update_entry(self.entry_to_edit, entry_data)
         else:
            self.maintenance_manager.add_entry(entry_data)
         if self.callback:
            self.callback()
         self._close_dialog()
      except Exception as e:
         messagebox.showerror("Error", f"Failed to save entry: {str(e)}", parent=self.dialog)

   def _cancel(self):
      self._close_dialog()

   def _close_dialog(self):
      self.dialog.destroy()
