# Bus Trip Announcer

## What is it?

**BusTripAnnouncer** is an app that tells you the next stops on the bus. The user can get this info by inputting their location, the bus number, and the headsign of the bus. It currently supports buses in South East Queensland, Australia.

## Why is this useful?

Most buses in South East Queensland do not announce the stops. If you do not know the location very well, you may have difficulty figuring out when to get off the bus.
**BusTripAnnouncer** makes this process easier.

## Example usage
```
Input route number: 66
Which headsign did you see?
1: RBWH station
2: UQ Lakes station
Enter number: 2
Input Latitude: -27.482215
Input Longitude: 153.022947
Input time: 14:17

------------------Route 66------------------
South Bank busway station, platform 2 | 0min
Mater Hill station, platform 2 | 2min
PA Hospital station, platform 2 | 5min
Boggo Road station, platform 6 | 7min
Dutton Park Place | 10min
UQ Lakes station | 12min
```

## Dependencies
- Pandas
- Flet

## Future Improvements
- Make a mobile app.
- Comprehensive testing.
- Have ways to manage mistakes the app makes in figuring out the trip.
- Add support for other locations.


## UML Class Diagram

![new_bus-trip-announcer drawio](https://user-images.githubusercontent.com/101725589/218023724-4830377d-3553-4062-bef9-2160b59390b9.png)
