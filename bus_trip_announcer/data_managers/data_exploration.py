import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


from bus_trip_announcer.utils import SEQDirection


routes = pd.read_csv("../../raw_data/routes.txt")
trips = pd.read_csv("../../raw_data/trips.txt")
stop_times = pd.read_csv("../../raw_data/stop_times.txt")
stop_times["stop_id"] = stop_times["stop_id"].astype(str)
stops = pd.read_csv("../../raw_data/stops.txt")


def show_route(route_number: int) -> None:
    route_id = routes.loc[
        routes["route_short_name"] == str(route_number), "route_id"
    ].iloc[0]
    example_trip_id = (
        trips.loc[trips["route_id"] == route_id, "trip_id"]
    ).iloc[0]
    route_stops = stop_times[stop_times["trip_id"] == example_trip_id]
    route_stops = route_stops[["stop_id", "arrival_time", "stop_sequence"]]

    route = pd.merge(
        route_stops, stops, on="stop_id"
    ).sort_values("stop_sequence")
    route = route[["stop_name", "arrival_time", "stop_lat", "stop_lon"]]
    plt.plot(route["stop_lon"], route["stop_lat"], "-bx", mfc="red", mec="red")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title(f"Route {route_number} Map")
    return route

def time_until_stops(route_number: int, direction: SEQDirection, stop_times: pd.DataFrame):
    route_id = routes.loc[
        routes["route_short_name"] == str(route_number), "route_id"
    ].iloc[0]
    trip_ids = trips.loc[(trips["route_id"] == route_id)
                        & (trips["direction_id"] == direction.value),
                        "trip_id"]

    route_stops = pd.merge(stop_times, trip_ids, on='trip_id')

    for _, trip in route_stops.groupby("trip_id"):
        trip["arrival_time"] = trip["arrival_time"].astype("timedelta64")

        start_time = trip["arrival_time"].iloc[0]
        time_diff = (trip["arrival_time"] - start_time) / 6e10

        plt.plot(np.arange(1, len(trip) + 1), time_diff)
        plt.xlabel("Stop Number")
        plt.ylabel("Time Until Stop (minutes)")
        plt.title(f"Route {route_number} Time Until Stop")

time_until_stops(66, SEQDirection.ZERO, stop_times)
# route = show_route(29)
plt.show()





route = show_route(29)
plt.show()


trips["direction_id"].value_counts()
trips.groupby("route_id")["trip_headsign"].nunique()

# number of headsigns for bus trips
bus_routes = routes.loc[routes["route_type"] == 3, "route_id"]
bus_trips = pd.merge(bus_routes, trips, on="route_id")
bus_trips.groupby("route_id")["trip_headsign"].nunique()
bus_trips.groupby("route_id")["trip_headsign"].nunique().value_counts()


# # this shows that the stop times for different trips varies. Some trips take longer
# standardized_times = np.zeros((100, 13))
# for i in range(100):
#     example_66_trip_id = (trips.loc[trips["route_id"] == route_66_id, "trip_id"]).iloc[i]
#     route_66_stops = stop_times[stop_times["trip_id"] == example_66_trip_id]
#     route_66_stops = route_66_stops[["stop_id", "arrival_time", "stop_sequence"]]
#
#     route_66 = pd.merge(route_66_stops, stops, on="stop_id")  #.sort_values("stop_sequence")
#     route_66 = route_66[["stop_name", "arrival_time", "stop_lat", "stop_lon"]]
#     standardized_times[i] = route_66["arrival_time"].astype("timedelta64") - route_66["arrival_time"].astype("timedelta64").iloc[0]
#
# plt.plot(np.arange(13), standardized_times.T)
# plt.xlabel("Stop Number")
# plt.ylabel("Time")
#
