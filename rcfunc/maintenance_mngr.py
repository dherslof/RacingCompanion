# This file is part of the Racing-Companion project.
#
# Description: Unit tests for functionality in the maintenance tab
# License: TBD

from typing import List, Dict, Any, Optional, Tuple
import re
from dataclasses import dataclass, field
from rcfunc.data_utils import save_maintenance_entries, load_maintenance_entries

@dataclass
class MaintenanceEntry:
   """Data class representing a maintenance entry"""
   title: str
   vehicle: str
   date: str
   duration: str
   description: str
   handbook_ref: str = ""
   tags: List[str] = field(default_factory=list)

   def to_dict(self) -> Dict[str, Any]:
      """Convert to dictionary for compatibility with existing data format"""
      return {
         "title": self.title,
         "vehicle": self.vehicle,
         "date": self.date,
         "duration": self.duration,
         "description": self.description,
         "handbook_ref": self.handbook_ref,
         "tags": self.tags
      }

   @classmethod
   def from_dict(cls, data: Dict[str, Any]) -> 'MaintenanceEntry':
      """Create from dictionary"""
      return cls(
         title=data.get("title", ""),
         vehicle=data.get("vehicle", ""),
         date=data.get("date", ""),
         duration=data.get("duration", ""),
         description=data.get("description", ""),
         handbook_ref=data.get("handbook_ref", ""),
         tags=data.get("tags", [])
      )

@dataclass
class MaintenanceFilter:
   """Data class for maintenance filtering criteria"""
   search_text: str = ""
   vehicle: str = "All"
   maintenance_type: str = "All"
   start_date: str = ""
   end_date: str = ""

@dataclass
class MaintenanceStatistics:
   """Data class for maintenance statistics"""
   vehicles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
   months: Dict[str, int] = field(default_factory=dict)
   maintenance_types: Dict[str, int] = field(default_factory=dict)

class MaintenanceMngr:
   """Business logic for maintenance management"""

   def __init__(self, vehicles: List[str], active_vehicle: Optional[str] = None):
      self.vehicles = vehicles
      self.active_vehicle = active_vehicle
      self._entries: List[MaintenanceEntry] = []
      self._load_entries()

   def _load_entries(self) -> None:
      """Load maintenance entries from storage"""
      try:
         raw_entries = load_maintenance_entries()
         self._entries = [MaintenanceEntry.from_dict(entry) for entry in raw_entries]
      except Exception as e:
         print(f"Error loading maintenance entries: {e}")
         self._entries = []

   def _save_entries(self) -> None:
      """Save maintenance entries to storage"""
      try:
         raw_entries = [entry.to_dict() for entry in self._entries]
         save_maintenance_entries(raw_entries)
      except Exception as e:
         print(f"Error saving maintenance entries: {e}")

   def add_entry(self, entry_data: Dict[str, Any]) -> MaintenanceEntry:
      """Add a new maintenance entry"""
      entry = MaintenanceEntry.from_dict(entry_data)
      self._entries.append(entry)
      self._save_entries()
      return entry

   def update_entry(self, old_entry: MaintenanceEntry, new_data: Dict[str, Any]) -> MaintenanceEntry:
      """Update an existing maintenance entry"""
      try:
         index = self._entries.index(old_entry)
         updated_entry = MaintenanceEntry.from_dict(new_data)
         self._entries[index] = updated_entry
         self._save_entries()
         return updated_entry
      except ValueError:
         raise ValueError("Entry not found")

   def delete_entry(self, entry: MaintenanceEntry) -> bool:
      """Delete a maintenance entry"""
      try:
         self._entries.remove(entry)
         self._save_entries()
         return True
      except ValueError:
         return False

   def get_all_entries(self) -> List[MaintenanceEntry]:
      """Get all maintenance entries"""
      return self._entries.copy()

   def filter_entries(self, filter_criteria: MaintenanceFilter, use_active_vehicle: bool = True) -> List[MaintenanceEntry]:
      """Filter maintenance entries based on criteria"""
      filtered_entries = self._entries.copy()
      if filter_criteria.search_text:
         search_text = filter_criteria.search_text.lower()
         filtered_entries = [
            entry for entry in filtered_entries
            if self._matches_search_text(entry, search_text)
         ]
      vehicle_filter = filter_criteria.vehicle
      if use_active_vehicle and not filter_criteria.search_text and self.active_vehicle:
         vehicle_filter = self.active_vehicle
      if vehicle_filter != "All":
         filtered_entries = [
            entry for entry in filtered_entries
            if vehicle_filter in entry.vehicle
         ]
      if filter_criteria.maintenance_type != "All":
         filtered_entries = [
            entry for entry in filtered_entries
            if filter_criteria.maintenance_type in entry.tags
         ]
      if filter_criteria.start_date:
         filtered_entries = [
            entry for entry in filtered_entries
            if entry.date >= filter_criteria.start_date
         ]
      if filter_criteria.end_date:
         filtered_entries = [
            entry for entry in filtered_entries
            if entry.date <= filter_criteria.end_date
         ]
      return filtered_entries

   def _matches_search_text(self, entry: MaintenanceEntry, search_text: str) -> bool:
      """Check if entry matches search text"""
      return (
         search_text in entry.title.lower() or
         search_text in entry.description.lower() or
         search_text in entry.vehicle.lower()
      )

   def get_statistics(self) -> MaintenanceStatistics:
      """Calculate maintenance statistics"""
      stats = MaintenanceStatistics()
      for entry in self._entries:
         vehicle = entry.vehicle or "Unknown"
         if vehicle not in stats.vehicles:
            stats.vehicles[vehicle] = {"count": 0, "time": 0}
         stats.vehicles[vehicle]["count"] += 1
         stats.vehicles[vehicle]["time"] += self._parse_duration_minutes(entry.duration)
         month = entry.date[:7] if len(entry.date) >= 7 else "Unknown"
         stats.months[month] = stats.months.get(month, 0) + 1
         for tag in entry.tags:
            stats.maintenance_types[tag] = stats.maintenance_types.get(tag, 0) + 1
      return stats

   def _parse_duration_minutes(self, duration_str: str) -> int:
      """Parse duration string and return total minutes"""
      if not duration_str:
         return 0
      hours_match = re.search(r'(\d+)\s*(?:hour|hr)s?', duration_str, re.IGNORECASE)
      minutes_match = re.search(r'(\d+)\s*(?:minute|min)s?', duration_str, re.IGNORECASE)
      hours = int(hours_match.group(1)) if hours_match else 0
      minutes = int(minutes_match.group(1)) if minutes_match else 0
      return hours * 60 + minutes

   def get_chart_data(self, chart_type: str) -> Dict[str, Any]:
      """Get data formatted for specific chart types"""
      stats = self.get_statistics()
      if chart_type == "frequency":
         sorted_months = sorted(stats.months.keys())
         return {
            "labels": [self._format_month_label(m) for m in sorted_months],
            "values": [stats.months[m] for m in sorted_months],
            "title": "Maintenance Frequency by Month",
            "xlabel": "Month",
            "ylabel": "Number of Maintenance Tasks"
         }
      elif chart_type == "pie":
         if not stats.maintenance_types:
            return {"labels": [], "values": [], "title": "Maintenance Tasks by Type"}
         return {
            "labels": list(stats.maintenance_types.keys()),
            "values": list(stats.maintenance_types.values()),
            "title": "Maintenance Tasks by Type"
         }
      elif chart_type == "vehicle_comparison":
         if not stats.vehicles:
            return {
               "vehicle_names": [], "counts": [], "times": [],
               "title": "Maintenance Comparison by Vehicle"
            }
         vehicle_names = list(stats.vehicles.keys())
         return {
            "vehicle_names": [v.split(" (")[0] for v in vehicle_names],
            "counts": [stats.vehicles[v]["count"] for v in vehicle_names],
            "times": [stats.vehicles[v]["time"] / 60 for v in vehicle_names],
            "title": "Maintenance Comparison by Vehicle"
         }
      return {}

   def _format_month_label(self, month_str: str) -> str:
      """Format month string for display"""
      if len(month_str) >= 7:
         return f"{month_str[5:7]}/{month_str[0:4]}"
      return month_str

   def validate_entry_data(self, entry_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
      """Validate maintenance entry data"""
      errors = []
      if not entry_data.get("title", "").strip():
         errors.append("Title is required")
      if not entry_data.get("vehicle", "").strip():
         errors.append("Vehicle is required")
      if not entry_data.get("date", "").strip():
         errors.append("Date is required")
      else:
         date_str = entry_data["date"].strip()
         if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            errors.append("Date must be in YYYY-MM-DD format")
      return len(errors) == 0, errors

   def get_available_vehicles(self) -> List[str]:
      """Get list of available vehicles"""
      return self.vehicles.copy()

   def get_active_vehicle(self) -> Optional[str]:
      """Get the active vehicle"""
      return self.active_vehicle
