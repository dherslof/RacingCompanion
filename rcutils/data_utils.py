# Add description and author information

import json
import os

data_file = "track_sessions.json"
vehicles_file = "vehicles.json"

def load_data():
    if os.path.exists(data_file):
        with open(data_file, "r") as file:
            return json.load(file)
    return []

def save_data(data):
    with open(data_file, "w") as file:
        json.dump(data, file, indent=4)

def load_vehicles():
    if os.path.exists(vehicles_file):
        with open(vehicles_file, "r") as file:
            data = json.load(file)
            return data.get("vehicles", []), data.get("vehicle_data", {})
    return [], {}

def save_vehicles(vehicles, vehicle_data):
    data_to_save = {
        "vehicles": vehicles,
        "vehicle_data": vehicle_data
    }
    with open(vehicles_file, "w") as file:
        json.dump(data_to_save, file, indent=4)

def save_maintenance_entries(maintenance_entries):
    maintenance_file = "maintenance_entries.json"
    with open(maintenance_file, "w") as file:
        json.dump(maintenance_entries, file, indent=4)

def load_maintenance_entries():
    maintenance_file = "maintenance_entries.json"
    if os.path.exists(maintenance_file):
        with open(maintenance_file, "r") as file:
            return json.load(file)
    else:
        return []