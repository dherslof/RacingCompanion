import pytest
from unittest.mock import patch, MagicMock
from rcfunc.maintenance_mngr import (
    MaintenanceMngr, MaintenanceEntry, MaintenanceFilter, MaintenanceStatistics
)

@pytest.fixture
def sample_entry():
   return {
      "title": "Oil Change",
      "vehicle": "Car1",
      "date": "2024-06-12",
      "duration": "1 hour 30 minutes",
      "description": "Changed oil",
      "handbook_ref": "6.7",
      "tags": ["Oil", "Minor"]
   }

@pytest.fixture
def manager(sample_entry):
   with patch("rcfunc.maintenance_mngr.load_maintenance_entries", return_value=[]), \
       patch("rcfunc.maintenance_mngr.save_maintenance_entries"):
      return MaintenanceMngr(vehicles=["Car1", "Car2"], active_vehicle="Car1")

class TestMaintenanceMngr:
   def test_add_entry(self, manager, sample_entry):
      with patch("rcfunc.maintenance_mngr.save_maintenance_entries"):
         entry = manager.add_entry(sample_entry)
         assert isinstance(entry, MaintenanceEntry)
         assert entry.title == "Oil Change"
         assert entry in manager.get_all_entries()

   def test_update_entry(self, manager, sample_entry):
      with patch("rcfunc.maintenance_mngr.save_maintenance_entries"):
         entry = manager.add_entry(sample_entry)
         new_data = sample_entry.copy()
         new_data["title"] = "Major Oil Change"
         updated = manager.update_entry(entry, new_data)
         assert updated.title == "Major Oil Change"
         assert updated in manager.get_all_entries()

   def test_delete_entry(self, manager, sample_entry):
      with patch("rcfunc.maintenance_mngr.save_maintenance_entries"):
         entry = manager.add_entry(sample_entry)
         assert manager.delete_entry(entry) is True
         assert entry not in manager.get_all_entries()
         assert manager.delete_entry(entry) is False

   def test_filter_entries(self, manager, sample_entry):
      with patch("rcfunc.maintenance_mngr.save_maintenance_entries"):
         manager.add_entry(sample_entry)
         filt = MaintenanceFilter(search_text="oil")
         results = manager.filter_entries(filt)
         assert len(results) == 1
         filt_none = MaintenanceFilter(search_text="brake")
         assert manager.filter_entries(filt_none) == []

   def test_validate_entry_data(self, manager, sample_entry):
      valid, errors = manager.validate_entry_data(sample_entry)
      assert valid
      bad_entry = sample_entry.copy()
      bad_entry["date"] = "12-06-2024"
      valid, errors = manager.validate_entry_data(bad_entry)
      assert not valid
      assert "Date must be in YYYY-MM-DD format" in errors

   def test_get_statistics(self, manager, sample_entry):
      with patch("rcfunc.maintenance_mngr.save_maintenance_entries"):
         manager.add_entry(sample_entry)
         stats = manager.get_statistics()
         assert isinstance(stats, MaintenanceStatistics)
         assert "Car1" in stats.vehicles

   def test_parse_duration_minutes(self, manager):
      assert manager._parse_duration_minutes("1 hour 30 minutes") == 90
      assert manager._parse_duration_minutes("2hr 15min") == 135
      assert manager._parse_duration_minutes("") == 0

   def test_get_chart_data(self, manager, sample_entry):
      with patch("rcfunc.maintenance_mngr.save_maintenance_entries"):
         manager.add_entry(sample_entry)
         freq = manager.get_chart_data("frequency")
         assert "labels" in freq and "values" in freq
         pie = manager.get_chart_data("pie")
         assert "labels" in pie and "values" in pie
         comp = manager.get_chart_data("vehicle_comparison")
         assert "vehicle_names" in comp and "counts" in comp and "times" in comp

   def test_get_available_vehicles(self, manager):
      vehicles = manager.get_available_vehicles()
      assert vehicles == ["Car1", "Car2"]

   def test_get_active_vehicle(self, manager):
      assert manager.get_active_vehicle() == "Car1"
