import pytest
from rcfunc.track_day_report_mngr import TrackDayReportMngr

class TestTrackDayReportMngr:
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
                "date": "2023-07-15",
                "organizer": "Org2",
                "vehicle": "Car2",
                "sessions": []
            },
            {
                "track": "Track1",
                "date": "2023-08-20",
                "organizer": "Org1",
                "vehicle": "Car1",
                "sessions": [
                    {"session_number": "2", "laps": "8", "vehicle": "Car1", "weather": "Rain"}
                ]
            }
        ]
        self.vehicles = ["Car1", "Car2"]
        self.mngr = TrackDayReportMngr(self.track_days, self.vehicles)

    def test_get_available_years_all(self):
        years = self.mngr.get_available_years()
        assert years == ["2023", "2024"]

    def test_get_available_years_for_vehicle(self):
        years_car1 = self.mngr.get_available_years("Car1")
        assert years_car1 == ["2023", "2024"]
        years_car2 = self.mngr.get_available_years("Car2")
        assert years_car2 == ["2023"]

    def test_generate_summary(self):
        result = self.mngr.generate_report("summary", "Car1", "2023")
        assert "Summary for Car1 in 2023" in result
        assert "Track Days: 1" in result
        assert "Sessions: 1" in result

    def test_generate_summary_all_vehicles(self):
        result = self.mngr.generate_report("summary", None, "2023")
        assert "Summary for All Vehicles in 2023" in result
        assert "Track Days: 2" in result
        assert "Sessions: 1" in result

    def test_generate_extensive(self):
        result = self.mngr.generate_report("extensive", "Car1")
        assert "Extensive Report for Car1" in result
        assert "- Track1 on 2024-06-12: 1 sessions" in result
        assert "- Track1 on 2023-08-20: 1 sessions" in result

    def test_generate_extensive_all_vehicles(self):
        result = self.mngr.generate_report("extensive")
        assert "Extensive Report for All Vehicles" in result
        assert "- Track2 on 2023-07-15: 0 sessions" in result

    def test_generate_report_unknown_type(self):
        result = self.mngr.generate_report("unknown")
        assert result == "Unknown report type."

    def test_get_available_tracks_all(self):
        tracks = self.mngr.get_available_tracks()
        assert sorted(tracks) == ["Track1", "Track2"]

    def test_get_available_tracks_for_vehicle(self):
        tracks_car1 = self.mngr.get_available_tracks(vehicle="Car1")
        assert tracks_car1 == ["Track1"]
        tracks_car2 = self.mngr.get_available_tracks(vehicle="Car2")
        assert tracks_car2 == ["Track2"]

    def test_get_available_tracks_for_vehicle_and_year(self):
        tracks = self.mngr.get_available_tracks(vehicle="Car1", year="2024")
        assert tracks == ["Track1"]
        tracks_none = self.mngr.get_available_tracks(vehicle="Car2", year="2024")
        assert tracks_none == []