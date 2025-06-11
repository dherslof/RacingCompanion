# vehicle_manager.py
# This file is part of the Racing-Companion project.
#
# Description: Unit tests for data_utils module
# License: TBD

from datetime import datetime
from typing import List, Dict, Optional

class VehicleMngr:

   def __init__(self, vehicles: List[str] = None, vehicle_data: Dict = None):
      self.vehicles = vehicles or []
      self.vehicle_data = vehicle_data or {}
      self.active_vehicle: Optional[str] = None

   def add_vehicle(self, name: str, vehicle_type: str = "Car",
               year: int = None, misc: str = "") -> bool:
      """Add a new vehicle. Returns True if successful, False if vehicle already exists."""
      if not name or name.strip() == "":
         return False

      name = name.strip()
      if name in self.vehicles:
         return False

      self.vehicles.append(name)
      self.vehicle_data[name] = {
         'type': vehicle_type,
         'year': year or datetime.now().year,
         'misc': misc
      }
      return True

   def edit_vehicle(self, old_name: str, new_name: str = None,
                vehicle_type: str = None, year: int = None,
                misc: str = None) -> bool:
      """Edit an existing vehicle. Returns True if successful."""
      if old_name not in self.vehicles:
         return False

      # Update name if provided and different
      if new_name and new_name.strip() and new_name != old_name:
         new_name = new_name.strip()
         if new_name in self.vehicles:  # Name already exists
            return False

         # Update the vehicles list
         index = self.vehicles.index(old_name)
         self.vehicles[index] = new_name

         # Update vehicle data
         self.vehicle_data[new_name] = self.vehicle_data.pop(old_name)

         # Update active vehicle if it was the renamed one
         if self.active_vehicle == old_name:
            self.active_vehicle = new_name

         vehicle_name = new_name
      else:
         vehicle_name = old_name

      # Update other fields if provided
      if vehicle_name in self.vehicle_data:
         if vehicle_type is not None:
            self.vehicle_data[vehicle_name]['type'] = vehicle_type
         if year is not None:
            self.vehicle_data[vehicle_name]['year'] = year
         if misc is not None:
            self.vehicle_data[vehicle_name]['misc'] = misc

      return True

   def delete_vehicle(self, name: str) -> bool:
      """Delete a vehicle. Returns True if successful."""
      if name not in self.vehicles:
         return False

      self.vehicles.remove(name)
      if name in self.vehicle_data:
         del self.vehicle_data[name]

      # Clear active vehicle if it was deleted
      if self.active_vehicle == name:
         self.active_vehicle = None

      return True

   def set_active_vehicle(self, name: str) -> bool:
      """Set the active vehicle. Returns True if successful."""
      if name not in self.vehicles:
         return False
      self.active_vehicle = name
      return True

   def clear_active_vehicle(self):
      """Clear the active vehicle."""
      self.active_vehicle = None

   def toggle_active_vehicle(self, name: str) -> bool:
      """Toggle vehicle as active/inactive. Returns True if successful."""
      if name not in self.vehicles:
         return False

      if self.active_vehicle == name:
         self.active_vehicle = None
      else:
         self.active_vehicle = name
      return True

   def get_vehicle_info(self, name: str) -> Optional[Dict]:
      """Get vehicle information."""
      return self.vehicle_data.get(name)

   def get_vehicle_type_abbreviation(self, name: str) -> str:
      """Get vehicle type abbreviation."""
      vehicle_info = self.get_vehicle_info(name)
      if not vehicle_info:
         return "UNK"

      vehicle_type = vehicle_info.get('type', 'Car')
      abbreviations = {
         "Car": "CAR",
         "Motorcycle": "MC",
         "Quad": "QUAD",
         "Snowmobile": "SLED"
      }
      return abbreviations.get(vehicle_type, vehicle_type[:4].upper())

   def is_active_vehicle(self, name: str) -> bool:
      """Check if vehicle is the active one."""
      return self.active_vehicle == name

   def get_all_vehicles(self) -> List[str]:
      """Get list of all vehicles."""
      return self.vehicles.copy()

   def has_vehicles(self) -> bool:
      """Check if any vehicles exist."""
      return len(self.vehicles) > 0