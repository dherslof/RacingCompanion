# This file is part of the Racing-Companion project.
#
# Description: Track day statistics and analytics for the Racing Companion application.
# License: TBD

from collections import defaultdict


class TrackDayStatsMngr:
    """Manager for computing track day statistics and analytics."""

    def __init__(self, track_days, vehicles, active_vehicle=None):
        self.track_days = track_days
        self.vehicles = vehicles
        self.active_vehicle = active_vehicle

    def _filter_track_days(self, vehicle=None, year=None):
        """Filter track days by vehicle and/or year."""
        filtered = self.track_days
        if vehicle:
            filtered = [d for d in filtered if d.get("vehicle") == vehicle]
        if year:
            filtered = [d for d in filtered if d.get("date", "").startswith(str(year))]
        return filtered

    def get_chart_data(self, chart_type, vehicle=None, year=None):
        """Get data formatted for specific chart types."""
        if chart_type == "track_frequency":
            return self._track_frequency_data(vehicle, year)
        elif chart_type == "performance_metrics":
            return self._performance_metrics_data(vehicle, year)
        elif chart_type == "vehicle_activity":
            return self._vehicle_activity_data(vehicle, year)
        elif chart_type == "weather_distribution":
            return self._weather_distribution_data(vehicle, year)
        else:
            return {}

    def _track_frequency_data(self, vehicle=None, year=None):
        """Compute track frequency (most/least visited tracks)."""
        days = self._filter_track_days(vehicle, year)
        track_count = defaultdict(int)
        for day in days:
            track = day.get("track", "N/A")
            track_count[track] += 1

        if not track_count:
            return {"labels": [], "values": [], "title": "Track Frequency", "xlabel": "Track", "ylabel": "Days Visited"}

        sorted_tracks = sorted(track_count.items(), key=lambda x: x[1], reverse=True)
        labels = [track for track, _ in sorted_tracks]
        values = [count for _, count in sorted_tracks]

        return {
            "labels": labels,
            "values": values,
            "title": "Track Frequency (Most to Least Visited)",
            "xlabel": "Track",
            "ylabel": "Number of Days",
        }

    def _performance_metrics_data(self, vehicle=None, year=None):
        """Compute performance metrics: avg laps per day, avg sessions per day."""
        days = self._filter_track_days(vehicle, year)

        if not days:
            return {
                "labels": [],
                "avg_laps": [],
                "avg_sessions": [],
                "title": "Performance Metrics",
                "ylabel": "Count",
            }

        # Group by vehicle to show metrics per vehicle
        vehicle_metrics = defaultdict(lambda: {"total_days": 0, "total_laps": 0, "total_sessions": 0})

        for day in days:
            v = day.get("vehicle", "N/A")
            vehicle_metrics[v]["total_days"] += 1
            vehicle_metrics[v]["total_sessions"] += len(day.get("sessions", []))
            vehicle_metrics[v]["total_laps"] += sum(
                int(s.get("laps", 0)) for s in day.get("sessions", []) if s.get("laps")
            )

        labels = sorted(vehicle_metrics.keys())
        avg_laps = [
            vehicle_metrics[v]["total_laps"] / vehicle_metrics[v]["total_days"]
            if vehicle_metrics[v]["total_days"] > 0
            else 0
            for v in labels
        ]
        avg_sessions = [
            vehicle_metrics[v]["total_sessions"] / vehicle_metrics[v]["total_days"]
            if vehicle_metrics[v]["total_days"] > 0
            else 0
            for v in labels
        ]

        return {
            "labels": labels,
            "avg_laps": avg_laps,
            "avg_sessions": avg_sessions,
            "title": "Performance Metrics (Averages per Day)",
            "ylabel": "Average Count",
        }

    def _vehicle_activity_data(self, vehicle=None, year=None):
        """Compute vehicle activity: track days and sessions per vehicle."""
        days = self._filter_track_days(vehicle, year)

        vehicle_activity = defaultdict(lambda: {"days": 0, "sessions": 0})
        for day in days:
            v = day.get("vehicle", "N/A")
            vehicle_activity[v]["days"] += 1
            vehicle_activity[v]["sessions"] += len(day.get("sessions", []))

        labels = sorted(vehicle_activity.keys())
        days_count = [vehicle_activity[v]["days"] for v in labels]
        sessions_count = [vehicle_activity[v]["sessions"] for v in labels]

        return {
            "vehicle_names": labels,
            "days_count": days_count,
            "sessions_count": sessions_count,
            "title": "Vehicle Activity",
        }

    def _weather_distribution_data(self, vehicle=None, year=None):
        """Compute weather distribution as a pie chart (per year)."""
        days = self._filter_track_days(vehicle, year)

        weather_count = defaultdict(int)
        for day in days:
            for session in day.get("sessions", []):
                weather = session.get("weather", "Unknown")
                weather_count[weather] += 1

        if not weather_count:
            return {"labels": [], "values": [], "title": "Weather Distribution"}

        labels = sorted(weather_count.keys())
        values = [weather_count[w] for w in labels]

        return {
            "labels": labels,
            "values": values,
            "title": "Weather Distribution (Sessions by Weather)",
        }

    def get_available_years(self, vehicle=None):
        """Get available years for filtering."""
        days = self._filter_track_days(vehicle)
        years = sorted({d.get("date", "")[:4] for d in days if d.get("date", "")})
        return years

    def get_available_vehicles(self):
        """Get available vehicles."""
        return sorted(self.vehicles) if self.vehicles else []

    def update_data_references(self, track_days, vehicles, active_vehicle):
        """Update internal data references (useful when data changes externally)."""
        self.track_days = track_days
        self.vehicles = vehicles
        self.active_vehicle = active_vehicle
