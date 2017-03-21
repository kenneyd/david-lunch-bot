import os
import googlemaps
import pprint
from types import GeneratorType
from datetime import datetime


class mapsClient:
    """For interacting with google maps API"""

    def __init__(self, location=(35.642145, 139.713487), language='en-US'):
        """setup the API keys"""

        API_KEY = os.environ.get("MAPS_API_KEY")
        self.gmaps = googlemaps.Client(key=API_KEY)

        self.location = location
        self.language = language

        self.pp = pprint.PrettyPrinter(indent=4)

    def getCoordinates(self, name):
        """Get coordinates by placename"""

        location = self.gmaps.geocode(name)

        return (location[0]['geometry']['location']['lat'],
                location[0]['geometry']['location']['lng'])

    def makeGoogleMapUrl(self, placename, lat, lng, zoom_level=17):

        return ("https://www.google.com/maps/place/{name}/@{lat!s},{lng!s},{zoom}z/".format(
            name=placename, lat=lat, lng=lng, zoom=zoom_level))

    def getDistanceMatrix(self, destinations, mode='walking'):
        """Find the travel distance/ time between origin, and list of destinations"""

        origin = [self.location]
        matrix = self.gmaps.distance_matrix(origin, destinations, mode=mode)

        return matrix

    def placesSearch(self, keyword="pizza", radius=700, rank_by='prominence'):
        """Search for nearby places using keyword(s)"""

        locations = self.gmaps.places_nearby(location=self.location, radius=radius,
                                             language=self.language, min_price=1,
                                             max_price=3, open_now=True,
                                             keyword=keyword, rank_by=rank_by)

        # If google returned no results, return an empty list
        if not locations:
            return []

        # Because the distance matrix takes a list of coordinates, let's create a seperate list
        # so that we can make a single API call for all destinations later
        destinations = []

        # Let's go through all the results and generate a URL for them, and record the coords
        for place in locations['results']:

            lat, lng = place['geometry']['location'][
                'lat'], place['geometry']['location']['lng']
            place['url'] = self.makeGoogleMapUrl(
                place['name'], lat=lat, lng=lng)
            destinations.append((lat, lng))

        # Now that we have a complete list of destination coords, let's get the distance to each
        distances = self.getDistanceMatrix(destinations=destinations)

        # And then append the distances (travel time) to each destination's dictionary
        for key, distance in enumerate(distances['rows'][0]['elements']):
            locations['results'][key]['distance'] = distance['duration']['text']

        return locations['results']


if __name__ == "__main__":
    mapsClient().placesSearch()
