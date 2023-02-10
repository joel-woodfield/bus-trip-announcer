# Bus Trip Announcer

While on the bus, the user can use this app to find out what the next stop is. The user can get this info by inputting their location, the bus number, and the headsign of the bus.

Example usage:
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

UML Class Diagram:

![bus-trip-announcer drawio (5)](https://user-images.githubusercontent.com/101725589/216879457-9ba0663f-ebe7-464f-a00f-a4ca66c90737.png)

Current Limitations:
- Routes that do not have two headsigns in the database do not work. An example of this is route 29.
