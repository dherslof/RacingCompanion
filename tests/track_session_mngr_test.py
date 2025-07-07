# This file is part of the Racing-Companion project.
#
# Description: Unit tests for the track session management functionality
# License: TBD
import pytest
import os
import csv
import tempfile
from rcfunc.track_session_mngr import TrackSessionMngr

class TestTrackSessionMngr:
   @pytest.fixture(autouse=True)
   def setup(self):
      self.track_days = [
         {
            "track": "Track1",
            "date": "2024-06-12",
            "organizer": "Org1",
            "vehicle": "Car1",
            "sessions": [
               {"session_number": "1", "laps": "10", "vehicle": "Car1", "weather": "Sunny"}
            ]
         },
         {
            "track": "Track2",
            "date": "2024-06-13",
            "organizer": "Org2",
            "vehicle": "Car2",
            "sessions": []
         }
      ]
      self.vehicles = ["Car1", "Car2"]
      self.active_vehicle = "Car1"
      self.weather_options = ["Sunny", "Rain"]
      self.saved = None

      def save_callback(data):
         self.saved = data
      self.save_callback = save_callback
      self.mngr = TrackSessionMngr(
         track_days=self.track_days.copy(),
         vehicles=self.vehicles,
         active_vehicle=self.active_vehicle,
         weather_options=self.weather_options,
         save_callback=self.save_callback
      )

   def test_get_filtered_track_days(self):
      filtered = self.mngr.get_filtered_track_days()
      assert len(filtered) == 1
      assert filtered[0]["vehicle"] == "Car1"

   def test_has_track_days(self):
      assert self.mngr.has_track_days() is True
      self.mngr.active_vehicle = "NonExistent"
      assert self.mngr.has_track_days() is False

   def test_get_track_day(self):
      assert self.mngr.get_track_day(0)["track"] == "Track1"
      assert self.mngr.get_track_day(1) is None

   def test_get_track_day_index_in_original_list(self):
      assert self.mngr.get_track_day_index_in_original_list(0) == 0
      assert self.mngr.get_track_day_index_in_original_list(1) == -1

   def test_delete_track_day(self):
      deleted = self.mngr.delete_track_day(0)
      assert deleted["track"] == "Track1"
      assert self.saved == self.mngr.track_days
      assert self.mngr.delete_track_day(0) is None

   def test_create_track_day(self):
      new_day = self.mngr.create_track_day("Track3", "2024-06-14", "Org3", "Car2")
      assert new_day in self.mngr.track_days
      assert self.saved == self.mngr.track_days

   def test_create_track_day_no_vehicle(self):
      self.mngr.vehicles = []
      with pytest.raises(ValueError):
         self.mngr.create_track_day("Track4", "2024-06-15", "Org4", "No Vehicles Available")

   def test_get_sessions(self):
      sessions = self.mngr.get_sessions(0)
      assert isinstance(sessions, list)
      assert sessions[0]["session_number"] == "1"
      assert self.mngr.get_sessions(1) == []

   def test_has_sessions(self):
      assert self.mngr.has_sessions(0) is True
      assert self.mngr.has_sessions(1) is False

   def test_get_session_numbers(self):
      nums = self.mngr.get_session_numbers(0)
      assert nums == ["1"]
      assert self.mngr.get_session_numbers(1) == []

   def test_find_session_by_number(self):
      session = self.mngr.find_session_by_number(0, "1")
      assert session["laps"] == "10"
      assert self.mngr.find_session_by_number(0, "2") is None

   def test_update_session(self):
      updated = self.mngr.update_session(0, "1", {"laps": "12"})
      assert updated is True
      assert self.mngr.get_sessions(0)[0]["laps"] == "12"
      assert self.saved == self.mngr.track_days

   def test_update_session_not_found(self):
      updated = self.mngr.update_session(0, "99", {"laps": "12"})
      assert updated is False

   def test_add_session(self):
      result = self.mngr.add_session(0, {"session_number": "2", "laps": "8", "vehicle": "Car1", "weather": "Rain"})
      assert result is True
      assert len(self.mngr.get_sessions(0)) == 2
      assert self.saved == self.mngr.track_days

   def test_add_session_invalid_index(self):
      result = self.mngr.add_session(99, {"session_number": "1"})
      assert result is False

   def test_get_next_session_number(self):
      assert self.mngr.get_next_session_number(0) == "2"
      assert self.mngr.get_next_session_number(1) == "1"

   def test_validate_session_data(self):
      valid, msg = self.mngr.validate_session_data({
         "session_number": "1", "laps": "10", "vehicle": "Car1", "weather": "Sunny"
      })
      assert valid
      valid, msg = self.mngr.validate_session_data({
         "laps": "10", "vehicle": "Car1", "weather": "Sunny"
      })
      assert not valid
      assert "Missing required field" in msg

   def test_get_track_day_vehicle(self):
      assert self.mngr.get_track_day_vehicle(0) == "Car1"
      assert self.mngr.get_track_day_vehicle(99) == "N/A"

   def test_update_data_references(self):
      new_days = []
      new_vehicles = ["Car3"]
      self.mngr.update_data_references(new_days, new_vehicles, "Car3")
      assert self.mngr.track_days == new_days
      assert self.mngr.vehicles == new_vehicles
      assert self.mngr.active_vehicle == "Car3"

   def test_export_track_day_to_csv(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmpfile:
            tmp_path = tmpfile.name
        try:
            result = self.mngr.export_track_day_to_csv(0, tmp_path)
            assert result is True

            # Check that the file exists and has expected content
            assert os.path.exists(tmp_path)
            with open(tmp_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
                # Should have as many rows as sessions in track day 0
                assert len(rows) == len(self.track_days[0]["sessions"])
                assert rows[0]["track"] == self.track_days[0]["track"]
                assert rows[0]["session_number"] == self.track_days[0]["sessions"][0]["session_number"]
        finally:
            os.remove(tmp_path)

   def test_export_track_day_to_csv_invalid_index(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmpfile:
            tmp_path = tmpfile.name
        try:
            # Export with invalid index
            result = self.mngr.export_track_day_to_csv(99, tmp_path)
            assert result is False
            # File should be empty or not written
            with open(tmp_path, "r", encoding="utf-8") as f:
                content = f.read()
                assert content == ""
        finally:
            os.remove(tmp_path)

   def test_export_track_day_to_csv_no_sessions(self):
    # Add a track day with no sessions
    self.mngr.track_days.append({
        "track": "Track3",
        "date": "2024-06-15",
        "organizer": "Org3",
        "vehicle": "Car3",
        "sessions": []
    })
    self.mngr.active_vehicle = "Car3"  # Ensure filtering includes the new track day
    idx = 0  # It's the only one for Car3
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmpfile:
        tmp_path = tmpfile.name
    try:
        result = self.mngr.export_track_day_to_csv(idx, tmp_path)
        assert result is True
        with open(tmp_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            # Should have one row (track day info, empty session fields)
            assert len(rows) == 1
            assert rows[0]["track"] == "Track3"
            assert rows[0]["session_number"] == ""
    finally:
        os.remove(tmp_path)
