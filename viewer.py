import datetime

from announcer import TripAnnouncer


class TripViewer:
    def show_next_stop_times(self):
        raise NotImplementedError


class CommandlineDisplay(TripViewer):
    def __init__(self, trip_announcer: TripAnnouncer):
        self._trip_announcer = trip_announcer

    def show_next_stop_times(self):
        stops_display = "\n".join(
            f"{stop_time.stop.name}"
            "| {self._route_time_format(stop_time.route_time)}"
            for stop_time in self._trip_announcer.next_stop_times
        )

        header_length = max(len(line) for line in stops_display.split("\n"))
        header = f"Route {self._trip_announcer.route_number}".center(
            header_length, "-"
        )
        print("\n" + header)
        print(stops_display + "\n")

    @classmethod
    def _route_time_format(cls, route_time: datetime.timedelta) -> str:
        hours, minutes, seconds = str(route_time).split(":")
        seconds = seconds.split(".")[0]
        if int(hours) == 0:
            return f"{minutes}:{seconds}"
        else:
            return f"{hours}:{minutes}:{seconds}"
