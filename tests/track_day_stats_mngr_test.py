import pytest

from rcfunc.track_day_stats_mngr import TrackDayStatsMngr


class TestTrackDayStatsMngr:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.track_days = [
            {
                "track": "Track A",
                "date": "2024-05-10",
                "organizer": "Org1",
                "vehicle": "Car1",
                "sessions": [
                    {"session_number": "1", "laps": "10", "vehicle": "Car1", "weather": "Sunny"},
                    {"session_number": "2", "laps": "8", "vehicle": "Car1", "weather": "Cloudy"},
                ],
            },
            {
                "track": "Track B",
                "date": "2024-06-15",
                "organizer": "Org2",
                "vehicle": "Car2",
                "sessions": [
                    {"session_number": "1", "laps": "12", "vehicle": "Car2", "weather": "Sunny"},
                ],
            },
            {
                "track": "Track A",
                "date": "2023-08-20",
                "organizer": "Org1",
                "vehicle": "Car1",
                "sessions": [
                    {"session_number": "1", "laps": "9", "vehicle": "Car1", "weather": "Rain"},
                ],
            },
            {
                "track": "Track C",
                "date": "2023-09-01",
                "organizer": "Org3",
                "vehicle": "Car2",
                "sessions": [],
            },
        ]
        self.vehicles = ["Car1", "Car2"]
        self.mngr = TrackDayStatsMngr(self.track_days, self.vehicles, active_vehicle="Car1")

    def test_track_frequency_data_all(self):
        data = self.mngr.get_chart_data("track_frequency")
        assert data["labels"] == ["Track A", "Track B", "Track C"]
        assert data["values"] == [2, 1, 1]
        assert data["xlabel"] == "Track"
        assert data["ylabel"] == "Number of Days"

    def test_track_frequency_data_filtered_by_vehicle_and_year(self):
        data = self.mngr.get_chart_data("track_frequency", vehicle="Car1", year="2024")
        assert data["labels"] == ["Track A"]
        assert data["values"] == [1]

    def test_performance_metrics_data_all(self):
        data = self.mngr.get_chart_data("performance_metrics")
        assert data["labels"] == ["Car1", "Car2"]

        # Car1 totals: laps=27, days=2, sessions=3
        assert data["avg_laps"][0] == pytest.approx(13.5)
        assert data["avg_sessions"][0] == pytest.approx(1.5)

        # Car2 totals: laps=12, days=2, sessions=1
        assert data["avg_laps"][1] == pytest.approx(6.0)
        assert data["avg_sessions"][1] == pytest.approx(0.5)

    def test_performance_metrics_filtered_vehicle(self):
        data = self.mngr.get_chart_data("performance_metrics", vehicle="Car1")
        assert data["labels"] == ["Car1"]
        assert data["avg_laps"] == [pytest.approx(13.5)]
        assert data["avg_sessions"] == [pytest.approx(1.5)]

    def test_vehicle_activity_filtered_vehicle(self):
        data = self.mngr.get_chart_data("vehicle_activity", vehicle="Car2")
        assert data["vehicle_names"] == ["Car2"]
        assert data["days_count"] == [2]
        assert data["sessions_count"] == [1]

    def test_weather_distribution_filtered_vehicle_and_year(self):
        data = self.mngr.get_chart_data("weather_distribution", vehicle="Car1", year="2024")
        assert data["labels"] == ["Cloudy", "Sunny"]
        assert data["values"] == [1, 1]

    def test_get_available_years_all_and_vehicle_specific(self):
        assert self.mngr.get_available_years() == ["2023", "2024"]
        assert self.mngr.get_available_years("Car1") == ["2023", "2024"]
        assert self.mngr.get_available_years("Car2") == ["2023", "2024"]

    def test_get_available_vehicles(self):
        assert self.mngr.get_available_vehicles() == ["Car1", "Car2"]

    def test_get_chart_data_unknown_type(self):
        assert self.mngr.get_chart_data("unknown") == {}

    def test_empty_data_returns_empty_series(self):
        empty_mngr = TrackDayStatsMngr([], [])

        freq = empty_mngr.get_chart_data("track_frequency")
        assert freq["labels"] == []
        assert freq["values"] == []

        perf = empty_mngr.get_chart_data("performance_metrics")
        assert perf["labels"] == []
        assert perf["avg_laps"] == []
        assert perf["avg_sessions"] == []

        activity = empty_mngr.get_chart_data("vehicle_activity")
        assert activity["vehicle_names"] == []
        assert activity["days_count"] == []
        assert activity["sessions_count"] == []

        weather = empty_mngr.get_chart_data("weather_distribution")
        assert weather["labels"] == []
        assert weather["values"] == []

    def test_update_data_references(self):
        new_days = [
            {
                "track": "Track D",
                "date": "2025-01-01",
                "organizer": "OrgX",
                "vehicle": "Car3",
                "sessions": [{"session_number": "1", "laps": "7", "vehicle": "Car3", "weather": "Sunny"}],
            }
        ]
        new_vehicles = ["Car3"]

        self.mngr.update_data_references(new_days, new_vehicles, "Car3")

        data = self.mngr.get_chart_data("track_frequency", vehicle="Car3")
        assert data["labels"] == ["Track D"]
        assert data["values"] == [1]
        assert self.mngr.get_available_vehicles() == ["Car3"]
