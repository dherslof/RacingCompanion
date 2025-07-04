# Add description and author information

import json
import os

import os
BASE_DIR = os.path.join(os.path.expanduser("~"), ".local/racing-companion")
data_file = os.path.join(BASE_DIR, ".rcstorage/track_sessions.json")
vehicles_file = os.path.join(BASE_DIR, ".rcstorage/vehicles.json")
maintenance_file = os.path.join(BASE_DIR, ".rcstorage/maintenance_entries.json")

def load_data(filename=data_file):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file)
    return []

def save_data(data, filename=data_file):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def load_vehicles(filename=vehicles_file):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            data = json.load(file)
            return data.get("vehicles", []), data.get("vehicle_data", {})
    return [], {}

def save_vehicles(vehicles, vehicle_data, filename=vehicles_file):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    data_to_save = {
        "vehicles": vehicles,
        "vehicle_data": vehicle_data
    }
    with open(filename, "w") as file:
        json.dump(data_to_save, file, indent=4)

def save_maintenance_entries(maintenance_entries, filename=maintenance_file):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as file:
        json.dump(maintenance_entries, file, indent=4)

def load_maintenance_entries(filename=maintenance_file):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            return json.load(file)
    else:
        return []