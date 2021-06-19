import unittest

from datetime import datetime
from math import log, sin, cos, atan2, asin, degrees, radians, sqrt
import numpy


earth_radius = 6371  # kilometers


def haversine(point1, point2):
    """
    Calculates the distance between two points on the earth.
    haversine((52.2296756, 21.0122287), (52.406374, 16.9251681))
    278.4581750754194
    """
    lat1, lat2 = radians(point1[0]), radians(point2[0])
    lon1, lon2 = radians(point1[1]), radians(point2[1])
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    a = (sin(delta_lat/2)*2) + (cos(lat1)*cos(lat2)*sin(delta_lon/2)*2)
    c = 2*atan2(sqrt(a), sqrt(1-a))
    distance = earth_radius * c
    return distance


class SeismicStation:
    """
    Class that creates the objects for a seismic station with a 'name', and
    a set of gps coordinates, lat and lon (degrees)
    """

    def _init_(self, name, coords: tuple):
        self.name = name
        self.coords = coords
        self.latitude = coords[0]
        self.longitude = coords[1]
        self.events = list()

    def add_event(self, event):
        """
        Adds a single event to the events list.
        """
        self.events.append(event)
        return None

    def _str_(self):
        result = '{0.name} at {0.coords}'.format(self)
        return result

    def _repr_(self):
        result = '{0.name}'.format(self)
        return result


class StationEvent:
    """
    An object pertaining to a single seismic event at a single seismic recording
    station.
    """

    def _init_(self, p_arrival_time, s_arrival_time, max_amplitude):
        p_time, s_time = self.parse_station_time(p_arrival_time, s_arrival_time)
        self.delta = s_time - p_time
        self.delta_sec = self.delta.seconds
        self.p_arrival_time = p_time
        self.s_arrival_time = s_time
        self.max_amplitude = max_amplitude 
        self.Vsp = self.wave_velocity()  
        self.dist_to_eq = self.calc_distance()
        self.magnitude = self.calc_magnitude()
        self.seismic_moment = self.calc_seismic_moment()
        self.energy = self.calc_seismic_energy()

    def _str_(self):
        message = "{} | Tsp(s): {}, Amp(mm): {}"
        return message.format(self.p_arrival_time, self.delta_sec, self.max_amplitude)

    def _repr_(self):
        message = "{} | Tsp(s): {}, Amp(mm): {}"
        return message.format(self.p_arrival_time, self.delta_sec, self.max_amplitude)

    def wave_velocity(self, VS=3.67, VP=6.34):
        """
        Calculates the wave velocity based upon assumptions VS and VP.
        VS = avg velocity of s-waves in CA crustal rocks (km/sec)
        VP = avg velocity of p-waves in CA crustal rocks (km/sec)
        """

        Vsp = (VS*VP) / (VP-VS)
        return Vsp 

    def parse_station_time(self, p_time, s_time):
        """
        parse_station_time("08:00:00", "08:00:49")
        """
        p_time = datetime.strptime(p_time, "%H:%M:%S")
        s_time = datetime.strptime(s_time, "%H:%M:%S")
        return p_time, s_time

    def calc_distance(self):
        """
        Calculates the distance from the epicenter of the earthquake from
        one seismic station. Using assumption of average velocity in California
        crustal rocks for Vsp. (adaptable for location of stations or earthquake)
        """

        self.dist_to_eq = float(self.delta_sec * self.Vsp)
        return self.dist_to_eq

    def calc_magnitude(self):
        """
        Calculates the magnitude of the Earthquake on the Richter Scale.
        source: http://crack.seismo.unr.edu/ftp/pub/louie/class/100/magnitude.html
        """
        result = log(self.max_amplitude) + (3*log(8*self.delta_sec)-2.92)
        self.magnitude = result
        return self.magnitude  
    def calc_seismic_moment(self):
        """
        Calculates the seismic moment (dyne-cm) of the earthquake based upon relationship
        with Magnitude. source: https://goo.gl/lLpS9x
        """
        result = 10 * ((3/2)(self.magnitude+16))
        self.seismic_moment = result
        return self.seismic_moment  

    def calc_seismic_energy(self, method='moment'):
        """
        Calculates the amount of Energy (ergs) released by the earthquake, based on
        either the magnitude or the seismic moment.
        """
        if method == 'magnitude':
            """
            E = 10 ^ (11.8 + (1.5 * Magnitude))
            """
            result = 10 ** (11.8+(1.5*self.magnitude))

        elif method == 'moment':
            """
            E = Moment / 20,000
            """
            result = self.seismic_moment / 20000

        else:
            print("Error, available methods are 'moment' or 'magnitude'.")
            result = None

        self.energy = result
        return self.energy

    def print_report(self):
        """
        Prints out the results. :)
        """
        message = 'The difference between p- and s-wave arrival times was: {} seconds.\
                   \nThe distance to the earthquake is {} kilometers.'
        print(message.format(self.delta_sec, self.dist_to_eq))


class Earthquake:
    """
    Compiles data from at least three seismic station events to determine
    the epicenter of the earthquake.
    """

    def _init_(self, *args):
        self.station1 = args[0]
        self.station2 = args[1]
        self.station3 = args[2]
        self.epicenter = Earthquake.calc_epicenter(self)

    def calc_epicenter(self):
        '''
        Calculates the epicenter of the Earthquake with the following steps:
        1. Gets the latitude (radians), longitude (radians), and radius (km) of each of the 3 seismic station events given
        2. Converts the geodetic latitude and longitude to ECEF xyz coordinates.
        3. Apply each X, Y, Z set of coordinates for each of the 3 points to it's own numpy array.
        4. Individually calculate the X, Y, and Z coordinates of the epicenter.
        5. Convert the ECEF xyz coordinates of the epicenter back to Geodetic Latitude and Longitude.

        returns the location of the epicenter as a tuple (latitude, longitude)
        '''

        lat1 = radians(self.station1.coords[0])  
        lon1 = radians(self.station1.coords[1])  
        r1 = self.station1.events[0].dist_to_eq  

        lat2 = radians(self.station2.coords[0])
        lon2 = radians(self.station2.coords[1])
        r2 = self.station2.events[0].dist_to_eq  

        lat3 = radians(self.station3.coords[0])
        lon3 = radians(self.station3.coords[1])
        r3 = self.station3.events[0].dist_to_eq  

        x1 = earth_radius * (cos(lat1) * cos(lon1))
        y1 = earth_radius * (cos(lat1) * sin(lon1))
        z1 = earth_radius * (sin(lat1))

        x2 = earth_radius * (cos(lat2) * cos(lon2))
        y2 = earth_radius * (cos(lat2) * sin(lon2))
        z2 = earth_radius * (sin(lat2))

        x3 = earth_radius * (cos(lat3) * cos(lon3))
        y3 = earth_radius * (cos(lat3) * sin(lon3))
        z3 = earth_radius * (sin(lat3))

 
        P1 = numpy.array([x1, y1, z1]) 
        P2 = numpy.array([x2, y2, z2])
        P3 = numpy.array([x3, y3, z3])

        ex = (P2 - P1)/(numpy.linalg.norm(P2 - P1))                 
        i = numpy.dot(ex, P3 - P1)                               
        ey = (P3 - P1 - i*ex)/(numpy.linalg.norm(P3 - P1 - i*ex))  
        ez = numpy.cross(ex, ey)                                   
        d = float(numpy.linalg.norm(P2 - P1))
        j = numpy.dot(ey, P3 - P1)

        x = ((r1*2) - (r22) + (d*2)) / (2*d)
        y = (((r1*2) - (r32) + (i2) + (j*2))/(2*j)) - ((i/j)*x)
        z = sqrt(abs((r1*2) - (x2) - (y*2)))

        tri_point = P1 + (x*ex) + (y*ey) + (z*ez)

        lat = degrees(asin(tri_point[2] / earth_radius))

        lon = degrees(atan2(tri_point[1], tri_point[0]))
        epicenter = (lat, lon)

        self.epicenter = epicenter
        return self.epicenter





sensor1 = SeismicStation('sensor1', (40.8021, -124.1637))
sensor2 = SeismicStation('sensor2', (40.8324, -115.7631))
sensor3 = SeismicStation('sensor3', (36.1699, -115.1398))

event1 = StationEvent("00:00:00", "00:01:08", 250)
event2 = StationEvent("00:00:00", "00:01:14", 50)
event3 = StationEvent("00:00:00", "00:01:04", 100)

sensor1.add_event(event1)
sensor2.add_event(event2)
sensor3.add_event(event3)

eq=Earthquake(sensor1, sensor2, sensor3)
print("The epicenter of the earthquake is: " + str(eq.calc_epicenter()))
print("The magnitude of the eathquake is: " + str(eq.calc_magnitude()))