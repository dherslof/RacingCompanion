# This file is part of the Racing-Companion project.
#
# Description: Unit tests for functionality in the welcome-tab
# License: TBD

import pytest
from datetime import datetime
from rcfunc.vehicle_mngr import VehicleMngr

class TestVehicleManager:
   def test_init_empty(self):
      """Test initialization with no parameters."""
      vm = VehicleMngr()
      assert vm.vehicles == []
      assert vm.vehicle_data == {}
      assert vm.active_vehicle is None

   def test_init_with_data(self):
      """Test initialization with existing data."""
      vehicles = ["Volvo XC90", "Honda CBR"]
      vehicle_data = {
         "Volvo XC90": {"type": "Car", "year": 2025, "misc": "Daily driver"},
         "Honda CBR": {"type": "Motorcycle", "year": 2003, "misc": ""}
      }
      vm = VehicleMngr(vehicles, vehicle_data)
      assert vm.vehicles == vehicles
      assert vm.vehicle_data == vehicle_data
      assert vm.active_vehicle is None

   def test_add_vehicle_success(self):
      """Test successful vehicle addition."""
      vm = VehicleMngr()
      result = vm.add_vehicle("Volvo XC90", "Car", 2020, "Daily driver")
      assert result is True
      assert "Volvo XC90" in vm.vehicles
      assert vm.vehicle_data["Volvo XC90"]["type"] == "Car"
      assert vm.vehicle_data["Volvo XC90"]["year"] == 2020
      assert vm.vehicle_data["Volvo XC90"]["misc"] == "Daily driver"

   def test_add_vehicle_default_values(self):
      """Test vehicle addition with default values."""
      vm = VehicleMngr()
      current_year = datetime.now().year
      result = vm.add_vehicle("Test Vehicle")
      assert result is True
      assert vm.vehicle_data["Test Vehicle"]["type"] == "Car"
      assert vm.vehicle_data["Test Vehicle"]["year"] == current_year
      assert vm.vehicle_data["Test Vehicle"]["misc"] == ""

   def test_add_vehicle_duplicate_name(self):
      """Test adding vehicle with duplicate name."""
      vm = VehicleMngr()
      vm.add_vehicle("Volvo XC90")
      result = vm.add_vehicle("Volvo XC90")
      assert result is False
      assert vm.vehicles.count("Volvo XC90") == 1

   def test_add_vehicle_empty_name(self):
      """Test adding vehicle with empty name."""
      vm = VehicleMngr()
      result = vm.add_vehicle("")
      assert result is False
      result = vm.add_vehicle("   ")
      assert result is False
      result = vm.add_vehicle(None)
      assert result is False

   def test_add_vehicle_whitespace_handling(self):
      """Test that vehicle names are properly trimmed."""
      vm = VehicleMngr()
      result = vm.add_vehicle("  Volvo XC90  ")
      assert result is True
      assert "Volvo XC90" in vm.vehicles
      assert "  Volvo XC90  " not in vm.vehicles

   def test_edit_vehicle_rename(self):
      """Test renaming a vehicle."""
      vm = VehicleMngr()
      vm.add_vehicle("Volvo XC90", "Car", 2020, "Daily driver")
      result = vm.edit_vehicle("Volvo XC90", new_name="Honda Accord")
      assert result is True
      assert "Honda Accord" in vm.vehicles
      assert "Volvo XC90" not in vm.vehicles
      assert "Honda Accord" in vm.vehicle_data
      assert "Volvo XC90" not in vm.vehicle_data

   def test_edit_vehicle_update_fields(self):
      """Test updating vehicle fields without renaming."""
      vm = VehicleMngr()
      vm.add_vehicle("Volvo XC90", "Car", 2020, "Daily driver")
      result = vm.edit_vehicle("Volvo XC90", vehicle_type="Motorcycle", year=2021, misc="Weekend ride")
      assert result is True
      assert vm.vehicle_data["Volvo XC90"]["type"] == "Motorcycle"
      assert vm.vehicle_data["Volvo XC90"]["year"] == 2021
      assert vm.vehicle_data["Volvo XC90"]["misc"] == "Weekend ride"

   def test_edit_vehicle_nonexistent(self):
      """Test editing non-existent vehicle."""
      vm = VehicleMngr()
      result = vm.edit_vehicle("Non-existent Vehicle", new_name="New Name")
      assert result is False

   def test_edit_vehicle_duplicate_new_name(self):
      """Test renaming to an existing vehicle name."""
      vm = VehicleMngr()
      vm.add_vehicle("Volvo XC90")
      vm.add_vehicle("Honda CBR")
      result = vm.edit_vehicle("Volvo XC90", new_name="Honda CBR")
      assert result is False
      assert "Volvo XC90" in vm.vehicles  # Original should remain

   def test_edit_vehicle_active_vehicle_update(self):
      """Test that active vehicle is updated when renamed."""
      vm = VehicleMngr()
      vm.add_vehicle("Volvo XC90")
      vm.set_active_vehicle("Volvo XC90")
      result = vm.edit_vehicle("Volvo XC90", new_name="Honda Accord")
      assert result is True
      assert vm.active_vehicle == "Honda Accord"

   def test_delete_vehicle_success(self):
      """Test successful vehicle deletion."""
      vm = VehicleMngr()
      vm.add_vehicle("Volvo XC90", "Car", 2020, "Daily driver")
      result = vm.delete_vehicle("Volvo XC90")
      assert result is True
      assert "Volvo XC90" not in vm.vehicles
      assert "Volvo XC90" not in vm.vehicle_data

   def test_delete_vehicle_nonexistent(self):
      """Test deleting non-existent vehicle."""
      vm = VehicleMngr()
      result = vm.delete_vehicle("Non-existent Vehicle")
      assert result is False

   def test_delete_active_vehicle(self):
      """Test deleting the active vehicle clears active status."""
      vm = VehicleMngr()
      vm.add_vehicle("Volvo XC90")
      vm.set_active_vehicle("Volvo XC90")
      result = vm.delete_vehicle("Volvo XC90")
      assert result is True
      assert vm.active_vehicle is None

   def test_set_active_vehicle_success(self):
      """Test setting active vehicle."""
      vm = VehicleMngr()
      vm.add_vehicle("Volvo XC90")
      result = vm.set_active_vehicle("Volvo XC90")
      assert result is True
      assert vm.active_vehicle == "Volvo XC90"

   def test_set_active_vehicle_nonexistent(self):
      """Test setting non-existent vehicle as active."""
      vm = VehicleMngr()
      result = vm.set_active_vehicle("Non-existent Vehicle")
      assert result is False
      assert vm.active_vehicle is None

   def test_clear_active_vehicle(self):
      """Test clearing active vehicle."""
      vm = VehicleMngr()
      vm.add_vehicle("Volvo XC90")
      vm.set_active_vehicle("Volvo XC90")
      vm.clear_active_vehicle()
      assert vm.active_vehicle is None

   def test_toggle_active_vehicle(self):
      """Test toggling vehicle active status."""
      vm = VehicleMngr()
      vm.add_vehicle("Volvo XC90")
      # Toggle to active
      result = vm.toggle_active_vehicle("Volvo XC90")
      assert result is True
      assert vm.active_vehicle == "Volvo XC90"
      # Toggle to inactive
      result = vm.toggle_active_vehicle("Volvo XC90")
      assert result is True
      assert vm.active_vehicle is None

   def test_toggle_active_vehicle_nonexistent(self):
      """Test toggling non-existent vehicle."""
      vm = VehicleMngr()
      result = vm.toggle_active_vehicle("Non-existent Vehicle")
      assert result is False

   def test_get_vehicle_info(self):
      """Test getting vehicle information."""
      vm = VehicleMngr()
      vm.add_vehicle("Volvo XC90", "Car", 2020, "Daily driver")
      info = vm.get_vehicle_info("Volvo XC90")
      expected = {"type": "Car", "year": 2020, "misc": "Daily driver"}
      assert info == expected

   def test_get_vehicle_info_nonexistent(self):
      """Test getting info for non-existent vehicle."""
      vm = VehicleMngr()
      info = vm.get_vehicle_info("Non-existent Vehicle")
      assert info is None

   def test_get_vehicle_type_abbreviation(self):
      """Test getting vehicle type abbreviations."""
      vm = VehicleMngr()
      vm.add_vehicle("Car", "Car")
      vm.add_vehicle("Bike", "Motorcycle")
      vm.add_vehicle("ATV", "Quad")
      vm.add_vehicle("Sled", "Snowmobile")
      assert vm.get_vehicle_type_abbreviation("Car") == "CAR"
      assert vm.get_vehicle_type_abbreviation("Bike") == "MC"
      assert vm.get_vehicle_type_abbreviation("ATV") == "QUAD"
      assert vm.get_vehicle_type_abbreviation("Sled") == "SLED"

   def test_is_active_vehicle(self):
      """Test checking if vehicle is active."""
      vm = VehicleMngr()
      vm.add_vehicle("Volvo XC90")
      vm.add_vehicle("Honda CBR")
      vm.set_active_vehicle("Volvo XC90")
      assert vm.is_active_vehicle("Volvo XC90") is True
      assert vm.is_active_vehicle("Honda CBR") is False
      assert vm.is_active_vehicle("Non-existent") is False

   def test_get_all_vehicles(self):
      """Test getting all vehicles."""
      vm = VehicleMngr()
      vm.add_vehicle("Volvo XC90")
      vm.add_vehicle("Honda CBR")
      vehicles = vm.get_all_vehicles()
      assert vehicles == ["Volvo XC90", "Honda CBR"]
      # Ensure it returns a copy
      vehicles.append("Test")
      assert len(vm.vehicles) == 2

   def test_has_vehicles(self):
      """Test checking if any vehicles exist."""
      vm = VehicleMngr()
      assert vm.has_vehicles() is False
      vm.add_vehicle("Volvo XC90")
      assert vm.has_vehicles() is True
      vm.delete_vehicle("Volvo XC90")
      assert vm.has_vehicles() is False

   def test_integration_scenario(self):
      """Test a complete integration scenario."""
      vm = VehicleMngr()
      # Add multiple vehicles
      vm.add_vehicle("Volvo XC90", "Car", 2020, "Daily driver")
      vm.add_vehicle("Yamaha R1", "Motorcycle", 2019, "Weekend ride")
      vm.add_vehicle("Polaris RZR", "Quad", 2021, "Off-road fun")
      assert len(vm.vehicles) == 3
      assert vm.has_vehicles() is True
      # Set active vehicle
      vm.set_active_vehicle("Yamaha R1")
      assert vm.is_active_vehicle("Yamaha R1") is True
      # Edit vehicle
      vm.edit_vehicle("Volvo XC90", misc="Updated info")
      assert vm.get_vehicle_info("Volvo XC90")["misc"] == "Updated info"
      # Delete non-active vehicle
      vm.delete_vehicle("Polaris RZR")
      assert len(vm.vehicles) == 2
      assert vm.active_vehicle == "Yamaha R1"  # Should remain active
      # Delete active vehicle
      vm.delete_vehicle("Yamaha R1")
      assert len(vm.vehicles) == 1
      assert vm.active_vehicle is None  # Should be cleared

@pytest.fixture
def populated_vehicle_manager():
   """Fixture providing a VehicleMngr with test data."""
   vehicles = ["Volvo XC90", "Honda CBR", "Yamaha R1"]
   vehicle_data = {
      "Volvo XC90": {"type": "Car", "year": 2020, "misc": "Daily driver"},
      "Honda CBR": {"type": "Motorcycle", "year": 2018, "misc": "Backup car"},
      "Yamaha R1": {"type": "Motorcycle", "year": 2019, "misc": "Weekend ride"}
   }
   return VehicleMngr(vehicles, vehicle_data)

class TestVehicleManagerWithFixtures:
   def test_populated_manager_operations(self, populated_vehicle_manager):
      """Test operations on pre-populated manager."""
      vm = populated_vehicle_manager
      assert len(vm.vehicles) == 3
      assert vm.has_vehicles() is True
      # Test setting active vehicle
      vm.set_active_vehicle("Yamaha R1")
      assert vm.is_active_vehicle("Yamaha R1") is True
      # Test getting vehicle info
      civic_info = vm.get_vehicle_info("Volvo XC90")
      assert civic_info["type"] == "Car"
      assert civic_info["year"] == 2020
