# This file is part of the Racing-Companion project.
#
# Description: Track session management functionality for the Racing Companion application.
# License: TBD

class TrackSessionMngr:
   """Business logic manager for track sessions and track days."""

   def __init__(self, track_days, vehicles, active_vehicle, weather_options, save_callback):
      self.track_days = track_days
      self.vehicles = vehicles
      self.active_vehicle = active_vehicle
      self.weather_options = weather_options
      self.save_callback = save_callback

   def get_filtered_track_days(self):
      """Get track days filtered by active vehicle."""
      if self.active_vehicle:
         return [day for day in self.track_days if day.get("vehicle") == self.active_vehicle]
      return self.track_days

   def has_track_days(self):
      """Check if there are any track days for the active vehicle."""
      return len(self.get_filtered_track_days()) > 0

   def get_track_day(self, index):
      """Get a track day by index."""
      filtered_days = self.get_filtered_track_days()
      if 0 <= index < len(filtered_days):
         return filtered_days[index]
      return None

   def get_track_day_index_in_original_list(self, filtered_index):
      """Get the original index of a track day in the unfiltered list."""
      filtered_days = self.get_filtered_track_days()
      if 0 <= filtered_index < len(filtered_days):
         target_day = filtered_days[filtered_index]
         return self.track_days.index(target_day)
      return -1

   def delete_track_day(self, filtered_index):
      """Delete a track day by its filtered index."""
      original_index = self.get_track_day_index_in_original_list(filtered_index)
      if original_index >= 0:
         deleted_day = self.track_days.pop(original_index)
         self.save_callback(self.track_days)
         return deleted_day
      return None

   def create_track_day(self, track_name, date, organizer, vehicle):
      """Create a new track day."""
      if not self.vehicles or vehicle == "No Vehicles Available":
         raise ValueError("Please add a vehicle before creating a track day.")
      new_day = {
         "track": track_name,
         "date": date,
         "organizer": organizer,
         "vehicle": vehicle,
         "sessions": []
      }
      self.track_days.append(new_day)
      self.save_callback(self.track_days)
      return new_day

   def get_sessions(self, track_day_index):
      """Get sessions for a specific track day."""
      track_day = self.get_track_day(track_day_index)
      if track_day:
         return track_day.get('sessions', [])
      return []

   def has_sessions(self, track_day_index):
      """Check if a track day has any sessions."""
      return len(self.get_sessions(track_day_index)) > 0

   def get_session_numbers(self, track_day_index):
      """Get list of session numbers for a track day."""
      sessions = self.get_sessions(track_day_index)
      return [session.get("session_number", f"Session {i+1}") for i, session in enumerate(sessions)]

   def find_session_by_number(self, track_day_index, session_number):
      """Find a session by its number within a track day."""
      track_day = self.get_track_day(track_day_index)
      if track_day:
         for session in track_day["sessions"]:
            if session.get("session_number") == session_number:
               return session
      return None

   def update_session(self, track_day_index, session_number, session_data):
      """Update an existing session."""
      session = self.find_session_by_number(track_day_index, session_number)
      if session:
         session.update(session_data)
         self.save_callback(self.track_days)
         return True
      return False

   def add_session(self, track_day_index, session_data):
      """Add a new session to a track day."""
      original_index = self.get_track_day_index_in_original_list(track_day_index)
      if original_index >= 0:
         self.track_days[original_index]["sessions"].append(session_data)
         self.save_callback(self.track_days)
         return True
      return False

   def get_next_session_number(self, track_day_index):
      """Get the next session number for a track day."""
      sessions = self.get_sessions(track_day_index)
      return str(len(sessions) + 1)

   def validate_session_data(self, session_data):
      """Validate session data before saving."""
      required_fields = ["session_number", "laps", "vehicle", "weather"]
      for field in required_fields:
         if field not in session_data or not session_data[field]:
            return False, f"Missing required field: {field}"
      return True, "Valid"

   def get_track_day_vehicle(self, track_day_index):
      """Get the vehicle for a specific track day."""
      track_day = self.get_track_day(track_day_index)
      if track_day:
         return track_day.get("vehicle", "N/A")
      return "N/A"

   def update_data_references(self, track_days, vehicles, active_vehicle):
      """Update internal data references (useful when data changes externally)."""
      self.track_days = track_days
      self.vehicles = vehicles
      self.active_vehicle = active_vehicle
