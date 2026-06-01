# TODO: File header here 

class TrackDayReportMngr:
    def __init__(self, track_days, vehicles):
        self.track_days = track_days
        self.vehicles = vehicles

    def get_available_years(self, vehicle=None):
        years = set()
        for day in self.track_days:
            if vehicle and day.get("vehicle") != vehicle:
                continue
            date = day.get("date", "")
            if date and len(date) >= 4:
                years.add(date[:4])
        return sorted(years)

    def get_available_tracks(self, vehicle=None, year=None):
        tracks = set()
        for day in self.track_days:
            if vehicle and day.get("vehicle") != vehicle:
                continue
            if year and not day.get("date", "").startswith(str(year)):
                continue
            track = day.get("track", "")
            if track:
                tracks.add(track)
        return sorted(tracks)

    def generate_report(self, report_type, vehicle=None, year=None, track=None, track_day=None):
        if report_type == "summary":
            return self._generate_summary(vehicle, year, track)
        elif report_type == "extensive":
            return self._generate_extensive(vehicle)
        elif report_type == "specific" and track_day is not None:
            return self._generate_specific(track_day)
        else:
            return "Unknown report type."

    def _generate_summary(self, vehicle=None, year=None, track=None):
        # If no vehicle or year is selected, show per vehicle and per year stats
        if not vehicle and not year and not track:
            return self._generate_global_summary()
        else:
            return self._generate_vehicle_year_summary(vehicle, year, track)

    def _generate_global_summary(self):
        # Summary for all vehicles, grouped by vehicle and year
        report_lines = ["Summary Report: All Vehicles\n"]
        for v in self.vehicles:
            report_lines.append(f"Vehicle: {v}")
            vehicle_days = [d for d in self.track_days if d.get("vehicle") == v]
            years = sorted({d.get("date", "")[:4] for d in vehicle_days if d.get("date", "")})
            total_days = len(vehicle_days)
            total_laps = sum(self._count_laps(d) for d in vehicle_days)
            unique_tracks = sorted({d.get("track", "") for d in vehicle_days if d.get("track", "")})
            report_lines.append(f"  Total Track Days: {total_days}")
            report_lines.append(f"  Total Laps: {total_laps}")
            report_lines.append(f"  Unique Tracks Visited: {len(unique_tracks)} ({', '.join(unique_tracks)})")
            for y in years:
                year_days = [d for d in vehicle_days if d.get("date", "").startswith(y)]
                year_laps = sum(self._count_laps(d) for d in year_days)
                year_tracks = sorted({d.get("track", "") for d in year_days if d.get("track", "")})
                report_lines.append(f"    Year {y}:")
                report_lines.append(f"      Track Days: {len(year_days)}")
                report_lines.append(f"      Laps: {year_laps}")
                report_lines.append(f"      Tracks Visited: {len(year_tracks)} ({', '.join(year_tracks)})")
            report_lines.append("")  # Blank line between vehicles
        return "\n".join(report_lines)

    def _generate_vehicle_year_summary(self, vehicle=None, year=None, track=None):
      # Special case: summary + track only (vehicle and year empty, track set)
      if (not vehicle or vehicle.strip() == "") and (not year or year.strip() == "") and (track and track.strip() != ""):
         days = [d for d in self.track_days if d.get("track") == track]
         years_visited = sorted({d.get("date", "")[:4] for d in days if d.get("date", "")})
         num_years_visited = len(years_visited)
         vehicles_used = sorted({d.get("vehicle", "") for d in days if d.get("vehicle", "")})
         num_vehicles = len(vehicles_used)
         total_days = len(days)

         # Find best lap time and session details
         best_lap = None
         best_lap_data = None
         for d in days:
               for s in d.get("sessions", []):
                  lap_time = s.get("best_lap_time")
                  if lap_time and (best_lap is None or self._compare_lap_times(lap_time, best_lap)):
                     best_lap = lap_time
                     best_lap_data = {
                           "date": d.get("date", ""),
                           "vehicle": d.get("vehicle", ""),
                           "tire_type": s.get("tire_type", ""),
                           "tire_status": s.get("tire_status", "")
                     }

         report = f"Summary for Track '{track}':\n"
         report += f"  Years Visited: {num_years_visited} ({', '.join(years_visited)})\n"
         report += f"  Number of Vehicles: {num_vehicles} ({', '.join(vehicles_used)})\n"
         report += f"  Number of Days: {total_days}\n"
         if best_lap:
               report += f"  Best Lap Time: {best_lap} (Date: {best_lap_data['date']}, Vehicle: {best_lap_data['vehicle']}, Tire: {best_lap_data['tire_type']} {best_lap_data['tire_status']})\n"
         else:
               report += "  Best Lap Time: N/A\n"
         return report

      # Regular filtering for other cases
      days = [
         d for d in self.track_days
         if (not vehicle or d.get("vehicle") == vehicle)
         and (not year or d.get("date", "").startswith(str(year)))
         and (not track or d.get("track") == track)
      ]
      total_days = len(days)
      total_sessions = sum(len(d.get("sessions", [])) for d in days)
      total_laps = sum(self._count_laps(d) for d in days)
      years_used = sorted({d.get("date", "")[:4] for d in days if d.get("date", "")})
      num_years_used = len(years_used)

      # Find best lap time and session details
      best_lap = None
      best_lap_data = None
      for d in days:
         for s in d.get("sessions", []):
               lap_time = s.get("best_lap_time")
               if lap_time and (best_lap is None or self._compare_lap_times(lap_time, best_lap)):
                  best_lap = lap_time
                  best_lap_data = {
                     "date": d.get("date", ""),
                     "session_number": s.get("session_number", ""),
                     "laps": s.get("laps", ""),
                     "weather": s.get("weather", ""),
                     "tire_type": s.get("tire_type", ""),
                     "tire_status": s.get("tire_status", "")
                  }

      report = f"Summary for {vehicle or 'All Vehicles'}"
      if year:
         report += f" in {year}"
      if track:
         report += f" on {track}"
      report += ":\n"
      report += f"  Track Days: {total_days}\n"
      report += f"  Sessions: {total_sessions}\n"
      report += f"  Total Laps: {total_laps}\n"
      if not year:
         report += f"  Years Used: {num_years_used} ({', '.join(years_used)})\n"

      if track:
         if best_lap:
               report += f"  Best Lap Time: {best_lap} (Date: {best_lap_data['date']}, Session: {best_lap_data['session_number']}, Weather: {best_lap_data['weather']}, Tire: {best_lap_data['tire_type']} {best_lap_data['tire_status']})\n"
         else:
               report += "  Best Lap Time: N/A\n"
      else:
         unique_tracks = sorted({d.get("track", "") for d in days if d.get("track", "")})
         report += f"  Unique Tracks Visited: {len(unique_tracks)} ({', '.join(unique_tracks)})\n"

      return report

    def _compare_lap_times(self, lap1, lap2):
      """Compare lap times in format mm:ss.sss or ss.sss. Returns True if lap1 is better (lower) than lap2."""
      def parse_lap(lap):
         parts = lap.split(":")
         if len(parts) == 2:
               minutes = int(parts[0])
               seconds = float(parts[1])
               return minutes * 60 + seconds
         try:
               return float(lap)
         except Exception:
               return float('inf')
      return parse_lap(lap1) < parse_lap(lap2)

    def _count_laps(self, track_day):
        # Count laps for all sessions in a track day
        return sum(int(s.get("laps", 0)) for s in track_day.get("sessions", []) if s.get("laps"))

    def _get_tire_progression(self, sessions):
      tire_map = {}
      for s in sessions:
         tire = s.get("tire_type", "Unknown")
         status = s.get("tire_status", "Unknown")
         if tire not in tire_map:
               tire_map[tire] = []
         tire_map[tire].append(status)
      # Build progression report
      progression = []
      for tire, statuses in tire_map.items():
         first = statuses[0] if statuses else "Unknown"
         last = statuses[-1] if statuses else "Unknown"
         progression.append(f"  {tire}: first session: {first}, last session: {last}")
      return progression
    
    def _get_lap_progression(self, sessions):
      lap_times = []
      for s in sessions:
         lap_time = s.get("best_lap_time")
         if lap_time:
               lap_times.append((lap_time, s.get("session_number", "N/A")))
      if not lap_times:
         return None, None, None, None, None  # <-- Return 5 values!
      # Sort lap times from worst (highest) to best (lowest)
      lap_times_sorted = sorted(lap_times, key=lambda x: self._parse_lap_time(x[0]), reverse=True)
      worst_lap, worst_session = lap_times_sorted[0]
      best_lap, best_session = lap_times_sorted[-1]
      diff = self._parse_lap_time(worst_lap) - self._parse_lap_time(best_lap)
      return worst_lap, worst_session, best_lap, best_session, diff

    def _parse_lap_time(self, lap):
      parts = str(lap).split(":")
      if len(parts) == 2:
         minutes = int(parts[0])
         seconds = float(parts[1])
         return minutes * 60 + seconds
      try:
         return float(lap)
      except Exception:
         return float('inf')

    def _generate_extensive(self, vehicle=None):
      days = [d for d in self.track_days if not vehicle or d.get("vehicle") == vehicle]
      report = f"Extensive Report for {vehicle or 'All Vehicles'}:\n"
      for day in days:
         report += f"- {day.get('track', 'N/A')} on {day.get('date', 'N/A')}: {len(day.get('sessions', []))} sessions\n"
         report += f"  Organizer: {day.get('organizer', 'N/A')}\n"
         report += f"  Vehicle: {day.get('vehicle', 'N/A')}\n"
         # Sessions header
         report += "  Sessions:\n"
         for s in day.get("sessions", []):
               report += (
                  f"    Session {s.get('session_number', 'N/A')}: "
                  f"{s.get('laps', 'N/A')} laps, Weather: {s.get('weather', 'N/A')}, "
                  f"Tire: {s.get('tire_type', 'N/A')} ({s.get('tire_status', 'N/A')}), "
                  f"Best Lap: {s.get('best_lap_time', 'N/A')}\n"
               )
         # Tire progression header
         tire_prog = self._get_tire_progression(day.get("sessions", []))
         if tire_prog:
               report += "  Tire progression:\n"
               for line in tire_prog:
                  report += f"    {line}\n"
         #report += "\n"

         worst_lap, worst_session, best_lap, best_session, diff = self._get_lap_progression(day.get("sessions", []))
         if worst_lap and best_lap:
            report += "  Lap progression:\n"
            report += f"    Worst lap: {worst_lap} (Session {worst_session})\n"
            report += f"    Best lap: {best_lap} (Session {best_session})\n"
            report += f"    Improvement: {diff:.3f} seconds\n"

         # Personal best on this track (across all sessions)
         all_laps = []
         for d in self.track_days:
            if d.get("track") == day.get("track"):
               for s in d.get("sessions", []):
                     lap_time = s.get("best_lap_time")
                     if lap_time:
                        all_laps.append((lap_time, d.get("date", ""), s.get("session_number", "N/A")))
         if all_laps:
            best_lap_overall = min(all_laps, key=lambda x: self._parse_lap_time(x[0]))
            report += f"  Personal best on {day.get('track', 'N/A')}: {best_lap_overall[0]} (Date: {best_lap_overall[1]}, Session {best_lap_overall[2]})\n"
            if best_lap:
               best_lap_val = self._parse_lap_time(best_lap)
               personal_best_val = self._parse_lap_time(best_lap_overall[0])
               lap_diff = best_lap_val - personal_best_val
               sign = "-" if lap_diff < 0 else "+"
               report += f"  Best lap difference to personal best: {sign}{abs(lap_diff):.3f} seconds\n"
      return report

    def _generate_specific(self, track_day):
        # Detailed report for a specific track day, number of laps, best lap time.
        if not track_day:
            return "No track day selected."
        report = f"Specific Report for {track_day.get('track', 'N/A')} on {track_day.get('date', 'N/A')}:\n"
        report += f"  Organizer: {track_day.get('organizer', 'N/A')}\n"
        report += f"  Vehicle: {track_day.get('vehicle', 'N/A')}\n"
        report += "  Sessions:\n"
        for s in track_day.get("sessions", []):
            report += f"    Session {s.get('session_number', 'N/A')}: {s.get('laps', 'N/A')} laps, Weather: {s.get('weather', 'N/A')}, Tire: {s.get('tire_type', 'N/A')} ({s.get('tire_status', 'N/A')}), Best Lap: {s.get('best_lap_time', 'N/A')}\n"
        return report

