import pandas as pd

useful_data = {
    "routes": ["route_id", "route_short_name"],
    "trips": ["trip_id", "route_id", "trip_headsign", "direction_id"],
    "stop_times": ["trip_id", "stop_id", "arrival_time", "stop_sequence"],
    "stops": ["stop_id", "stop_name", "stop_lat", "stop_lon"],
}


def main():
    for table_name, attributes in useful_data.items():
        table = pd.read_csv(f"raw_data/{table_name}.txt")
        table = table[useful_data[table_name]]
        table.to_csv(f"useful_data/{table_name}.csv")

    # remove stops that don't have a numerical stop id
    stops = pd.read_csv(f"../../useful_data/stops.csv")
    stops = stops[stops["stop_id"].str.isdigit()]
    stops.to_csv(f"useful_data/stops.csv")


if __name__ == "__main__":
    main()
