# This file is part of the Racing-Companion project.
#
# Description: Unit tests for data_utils module
# License: TBD

import unittest
import os

from rcfunc.data_utils import save_vehicles, load_vehicles, save_maintenance_entries, load_maintenance_entries, save_data, load_data


class TestDataUtils(unittest.TestCase):
   def setUp(self):
      # Set test data
      self.test_workdir = "tmp-test"
      self.test_vehicle_file = self.test_workdir + "/test_vehicles.json"
      self.test_vehicle_list = ["Car1", "mc1", "sled1", "quad1"]
      self.test_vehicle_data = {
      "Car1": {
            "type": "Motorcycle",
            "year": "2025",
            "misc": "Fast and furious",
        },
         "mc1": {
               "type": "Motorcycle",
               "year": "2023",
               "misc": "Two wheels, one love",
        },
         "sled1": {
               "type": "Snowmobile",
               "year": "2022",
               "misc": "Winter warrior",
        },
         "quad1": {
               "type": "ATV",
               "year": "2024",
               "misc": "All-terrain fun",
        }}

      self.test_maintenance_file = self.test_workdir + "/test_maintenance_entries.json"
      self.test_maintenance_entries = [
         {
         "title": "Oil change",
         "vehicle": "Yamaha R1",
         "date": "2025-05-10",
         "duration": "1h30m",
         "handbook_ref": "6.7",
         "description": "Normal oil change",
         "tags": [
               "Minor",
               "Oil"
         ]
         },
         {
         "title": "Tire change",
         "vehicle": "Yamaha R1",
         "date": "2025-05-15",
         "duration": "2h",
         "handbook_ref": "8.3",
         "description": "Changed tires for summer season",
         "tags": [
               "Major",
               "Tires"
         ]
         }
      ]

      self.test_track_days_file = self.test_workdir + "/test_track_days.json"
      self.test_track_days = [
         {
            "track": "Test-Track1",
            "date": "2025-10515",
            "organizer": "Me",
            "vehicle": "Yamaha R1",
            "sessions": [
                  {
                     "session_number": "1",
                     "laps": "42",
                     "vehicle": "Yamaha R1",
                     "weather": "Sunny",
                     "tire_type": "Slicks",
                     "tire_status": "New",
                     "best_lap_time": "1.42.0",
                     "comments": ""
                  }
            ]
         },
         {
            "track": "Test-Track2",
            "date": "2025-10516",
            "organizer": "Me",
            "vehicle": "Yamaha R1",
            "sessions": [
                  {
                     "session_number": "1",
                     "laps": "42",
                     "vehicle": "Yamaha R1",
                     "weather": "Sunny",
                     "tire_type": "Rain",
                     "tire_status": "New",
                     "best_lap_time": "1.24.0",
                     "comments": ""
                  }
            ]
         }
      ]

   def tearDown(self):
      try:
         # Remove test files if they exist
         os.remove(self.test_vehicle_file)
         os.remove(self.test_maintenance_file)
         os.remove(self.test_track_days_file)
      except FileNotFoundError:
         pass

      # Remove test directory if it exists
      try:
         os.rmdir(self.test_workdir)
      except FileNotFoundError:
         pass
      except OSError:
         # Directory not empty, write warning
         print(f"Warning: Directory {self.test_workdir} is not empty and cannot be removed.")
      except Exception as e:
         # Catch any other exceptions and write a warning
         print(f"Warning: An unexpected error occurred while removing {self.test_workdir}: {e}")

   # Test cases for save vehicles and load vehicles functions
   def test_save_and_load_vehicles(self):
         save_vehicles(self.test_vehicle_list, self.test_vehicle_data, filename=self.test_vehicle_file)
         loaded_vehicles, loaded_data = load_vehicles(filename=self.test_vehicle_file)
         self.assertEqual(loaded_vehicles, self.test_vehicle_list)
         self.assertEqual(loaded_data, self.test_vehicle_data)

   def test_load_vehicles_no_file(self):
         loaded_vehicles, loaded_data = load_vehicles(filename=self.test_vehicle_file)
         self.assertEqual(loaded_vehicles, [])
         self.assertEqual(loaded_data, {})

   def test_save_vehicles_no_data(self):
         save_vehicles([], {}, filename=self.test_vehicle_file)
         loaded_vehicles, loaded_data = load_vehicles(filename=self.test_vehicle_file)
         self.assertEqual(loaded_vehicles, [])
         self.assertEqual(loaded_data, {})

   def test_save_vehicles_empty_list(self):
         save_vehicles([], self.test_vehicle_data, filename=self.test_vehicle_file)
         loaded_vehicles, loaded_data = load_vehicles( filename=self.test_vehicle_file)
         self.assertEqual(loaded_vehicles, [])
         self.assertEqual(loaded_data, self.test_vehicle_data)

   # Test cases for save maintenance and maintenance functions
   def test_save_and_load_maintenance_entries(self):
         save_maintenance_entries(self.test_maintenance_entries, filename=self.test_maintenance_file)
         loaded_entries = load_maintenance_entries(filename=self.test_maintenance_file)
         self.assertEqual(loaded_entries, self.test_maintenance_entries)

   def test_load_maintenance_entries_no_file(self):
         loaded_entries = load_maintenance_entries(filename=self.test_maintenance_file)
         self.assertEqual(loaded_entries, [])

   def test_save_maintenance_entries_no_data(self):
         save_maintenance_entries([], filename=self.test_maintenance_file)
         loaded_entries = load_maintenance_entries(filename=self.test_maintenance_file)
         self.assertEqual(loaded_entries, [])

   def test_save_maintenance_entries_empty_list(self):
         save_maintenance_entries([], filename=self.test_maintenance_file)
         loaded_entries = load_maintenance_entries(filename=self.test_maintenance_file)
         self.assertEqual(loaded_entries, [])

   # Test cases for save track days and load track days functions
   def test_save_and_load_track_days(self):
         save_data(self.test_track_days, filename=self.test_track_days_file)
         loaded_days = load_data(filename=self.test_track_days_file)
         self.assertEqual(loaded_days, self.test_track_days)

   def test_load_track_days_no_file(self):
         loaded_days = load_data(filename=self.test_track_days_file)
         self.assertEqual(loaded_days, [])

   def test_save_track_days_no_data(self):
         save_data([], filename=self.test_track_days_file)
         loaded_days = load_data(filename=self.test_track_days_file)
         self.assertEqual(loaded_days, [])

   def test_save_track_days_empty_list(self):
         save_data([], filename=self.test_track_days_file)
         loaded_days = load_data(filename=self.test_track_days_file)
         self.assertEqual(loaded_days, [])


if __name__ == "__main__":
    unittest.main()
