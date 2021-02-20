import json
import math
import matplotlib as mil
mil.use('TkAgg')
import matplotlib.pyplot as plt

class Agent:
    # 1 * = Quand on sait pas combien d'élément précis il y aura en param, ils seront donc transformé en tuples
    # 2 ** = dictionnaire en tant que fonction
    def __init__(self, position, **agent_attributes):
        self.position = position
        for attr_name, attr_value in agent_attributes.items():
            setattr(self, attr_name, attr_value)


class Position:
    def __init__(self, longitude_degrees, latitude_degrees):
        self.longitude_degrees = longitude_degrees
        self.latitude_degrees = latitude_degrees

    @property  # Passe la fonction en propriété, pas besoin des () pour l'appelé
    def longitude(self):
        return self.longitude_degrees * math.pi / 180

    @property
    def latitude(self):
        return self.latitude_degrees * math.pi / 180  # Convertie des degrés aux radians


class Zone:
    # Attribut de class, défini avant les fonctions, s'écrit en majuscule
    ZONES = []
    MIN_LONGITUDE_DEGREES = -180
    MAX_LONGITUDE_DEGREES = 180
    MIN_LATITUDE_DEGREES = -90
    MAX_LATITUDE_DEGREES = 90
    EARTH_RADIUS_KM = 6371
    WIDTH_DEGREES = 1  # Ajoute un degrés de longitude
    HEIGHT_DEGREES = 1  # Ajoute un degrés de latitude

    def __init__(self, corner1, corner2):
        self.corner1 = corner1
        self.corner2 = corner2
        self.inhabitants = []

    @property
    def population(self):
        return len(self.inhabitants)

    @property
    def width(self):
        return abs(self.corner1.longitude - self.corner2.longitude) * self.EARTH_RADIUS_KM

    @property
    def height(self):
        return abs(self.corner1.latitude - self.corner2.latitude) * self.EARTH_RADIUS_KM

    @property
    def area(self):
        return self.height * self.width

    def population_density(self):
        return self.population / self.area

    def add_inhabitant(self, inhabitant):
        self.inhabitants.append(inhabitant)


    def average_agreeableness(self):
        if not self.inhabitants:
            return 0
        return sum([inhabitant.agreeableness for inhabitant in self.inhabitants]) / self.population  # List comprehension


    def contains(self, position):
        return position.longitude >= min(self.corner1.longitude, self.corner2.longitude) and \
            position.longitude < max(self.corner1.longitude, self.corner2.longitude) and \
            position.latitude >= min(self.corner1.latitude, self.corner2.latitude) and \
            position.latitude < max(self.corner1.latitude, self.corner2.latitude)

    @classmethod  # Défini la méthode au niveau de la class et non de l'instance, on remplace donc self par cls
    def find_zone_that_contains(cls, position):
        # Compute the index in the ZONES array that contains the given position
        if not cls.ZONES:
            cls._initialize_zones()
        longitude_index = int((position.longitude_degrees - cls.MIN_LONGITUDE_DEGREES) / cls.WIDTH_DEGREES)
        latitude_index = int((position.latitude_degrees - cls.MIN_LATITUDE_DEGREES) / cls.HEIGHT_DEGREES)
        longitude_bins = int(
            (cls.MAX_LONGITUDE_DEGREES - cls.MIN_LONGITUDE_DEGREES) / cls.WIDTH_DEGREES)  # 180-(-180) / 1
        zone_index = latitude_index * longitude_bins + longitude_index

        # Just checking that the index is correct
        zone = cls.ZONES[zone_index]
        assert zone.contains(position)

        return zone


    @classmethod
    def _initialize_zones(cls):  # _ va permettre de protéger la méthode
        cls.ZONES = []  # range va permettre de créer une liste avec une valeur min, max et un intervalle
        for latitude in range(cls.MIN_LATITUDE_DEGREES, cls.MAX_LATITUDE_DEGREES, cls.HEIGHT_DEGREES):
            for longitude in range(cls.MIN_LONGITUDE_DEGREES, cls.MAX_LONGITUDE_DEGREES, cls.WIDTH_DEGREES):
                bottom_left_corner = Position(longitude, latitude)
                top_right_corner = Position(longitude + cls.WIDTH_DEGREES, latitude + cls.HEIGHT_DEGREES)
                zone = Zone(bottom_left_corner, top_right_corner)
                cls.ZONES.append(zone)


class BaseGraph:

    def __init__(self):
        self.title = "Titre du graphique"
        self.x_label = "X-axis"
        self.y_label = "Y-axis"
        self.show_grid = True

    def show(self, zones):
        x_values, y_values = self.xy_value(zones)
        plt.plot(x_values, y_values, '.')
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        plt.title(self.title)
        plt.grid(self.show_grid)
        plt.show()

    def xy_value(self, zones):
        raise NotImplementedError

class agreeablenessGraph(BaseGraph):

    def __init__(self):
        super().__init__() # super() va faire un appel à la classe parent et execute une méthode de celle ci, ici __init__
        self.title = "Titre"
        self.x_label = "Densité de population"
        self.y_label = "Agréabilité"

    def xy_value(self, zones):
        x_values = [zone.population_density() for zone in zones]
        y_values = [zone.average_agreeableness() for zone in zones]
        return x_values, y_values


def main():
    for agent_attributes in json.load(open("agents-100k.json")):
        latitude = agent_attributes.pop('latitude')
        longitude = agent_attributes.pop('longitude')
        position = Position(longitude, latitude)
        agent = Agent(position, **agent_attributes)  # On appelle les attributs disponibles dans le dictionnaire
        zone = Zone.find_zone_that_contains(position)
        zone.add_inhabitant(agent)

    agrea_graph = agreeablenessGraph()
    agrea_graph.show(Zone.ZONES)

main()