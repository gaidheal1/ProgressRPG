from django.db import models
from math import sqrt


##########################################################
##### UTILITIES ##########################################
##########################################################


class Position(models.Model):
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def calculate_distance(self, other):
        return sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def is_near(self, other, threshold=1.0):
        return self.calculate_distance(other) <= threshold


class Movable(models.Model):
    movement_speed = models.FloatField(default=1.0)
    is_moving = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def move_to(self, new_position, speed_modifier=1.0):
        distance = self.position.calculate_distance(new_position)
        travel_time = distance / (self.movement_speed * speed_modifier)
        self.position = new_position
        self.is_moving = False
        self.save()
        return travel_time


##########################################################
##### LOCATIONS ##########################################
##########################################################


class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent_location = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, related_name="sub_locations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=2000, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PopulationCentre(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=2000, null=True, blank=True)
    population = models.IntegerField()
    is_unlocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_average_happiness(self):
        characters = Character.objects.filter(
            residence__building__location__populationcentre=self
        )
        if characters.exists():
            individual_happiness = (
                sum(character.happiness for character in characters)
                / characters.count()
            )
        else:
            individual_happiness = 0

        public_spaces = PublicSpace.objects.filter(population_centre=self)
        if public_spaces.exists():
            environmental_happiness = (
                sum(
                    (
                        public_space.cleanliness
                        + public_space.condition
                        + public_space.reputation
                    )
                    / 3
                    for public_space in public_spaces
                )
                / public_spaces.count()
            )
        else:
            environmental_happiness = 50

        average_happiness = (individual_happiness * 0.6) + (
            environmental_happiness * 0.4
        )
        return average_happiness


##########################################################
##### BUILDINGS   ########################################
##########################################################


class BuildingType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Building(models.Model):
    location = models.OneToOneField(
        "Location", on_delete=models.CASCADE, null=True, related_name="building"
    )
    position = models.OneToOneField(
        "Position", on_delete=models.SET_NULL, null=True, related_name="building"
    )
    size = models.IntegerField(blank=True, null=True)
    condition = models.IntegerField(default=80)
    improvable_fields = ["condition"]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str_(self):
        return self.name


class Residence(models.Model):
    building = models.OneToOneField(
        "Building", on_delete=models.CASCADE, related_name="residence"
    )
    max_occupants = models.IntegerField(default=4)
    comfort_level = models.IntegerField(default=50, help_text="Comfort percentage")
    improvable_fields = ["comfort_level"]

    def __str__(self):
        return f"Residence at {self.building.name}"


class Shop(models.Model):
    building = models.OneToOneField(
        "Building", on_delete=models.CASCADE, related_name="shop"
    )
    inventory_capacity = models.IntegerField(default=50)
    trade_rating = models.IntegerField(default=80)
    improvable_fields = ["trade_rating"]

    def __str__(self):
        return f"Shop at {self.building.name}"


class Workshop(models.Model):
    building = models.OneToOneField(
        "Building", on_delete=models.CASCADE, related_name="workshop"
    )
    productivity = models.IntegerField(default=80)
    tool_quality = models.IntegerField(default=80)
    improvable_fields = ["productivity", "tool_quality"]

    def __str__(self):
        return f"Workshop at {self.building.name}"


class Storage(models.Model):
    building = models.OneToOneField(
        "Building", on_delete=models.CASCADE, related_name="storage"
    )
    STORAGE_TYPES = [
        ("food", "Food"),
        ("construction", "Construction Materials"),
        ("cold", "Cold"),
    ]
    storage_type = models.CharField(max_length=50, choices=STORAGE_TYPES)
    capacity = models.IntegerField(default=100, help_text="Max storage units available")
    quantity = models.IntegerField(default=0, help_text="Quantity of item in storage")
    security_level = models.IntegerField(default=80)
    improvable_fields = ["security_level"]

    def __str__(self):
        return f"Storage at {self.building.name}, capacity {self.capacity} units"


class Social(models.Model):
    building = models.OneToOneField(
        "Building", on_delete=models.CASCADE, related_name="social"
    )
    capacity = models.IntegerField(default=30)

    def __str__(self):
        return f"Social space at {self.building.name}"


##########################################################
##### AGRICULTURE ########################################
##########################################################


class Crop(models.Model):
    name = models.CharField(max_length=255, unique=True)
    growth_time = models.IntegerField(help_text="Growth time in days")
    yield_per_sq_meter = models.DecimalField(max_digits=5, decimal_places=2)
    food_unit_weight = models.IntegerField(
        default=500, help_text="Weight of one food unit in grams"
    )

    def calculate_food_units(self):
        return self.yield_per_sq_metre / self.food_unit_weight

    def __str__(self):
        return self.name


class Tree(models.Model):
    name = models.CharField(max_length=255, unique=True)
    growth_time = models.IntegerField(help_text="Growth time in days")
    yield_per_instance = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name


class Animal(models.Model):
    name = models.CharField(max_length=255, unique=True)
    food_consumption_per_day = models.DecimalField(
        max_digits=5, decimal_places=2, help_text="Food units per day"
    )

    def __str__(self):
        return self.name


class FarmSpace(models.Model):
    location = models.OneToOneField(
        "Location", on_delete=models.CASCADE, null=True, related_name="farmspace"
    )
    position = models.OneToOneField(
        "Position", on_delete=models.SET_NULL, null=True, related_name="farmspace"
    )
    size = models.IntegerField(blank=True, null=True)
    in_use = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class GrowingArea(models.Model):
    base_productivity_per_sq_metre = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.0
    )
    water_availability = models.IntegerField(default=80)
    fertility = models.IntegerField(default=80)
    improvable_fields = ["fertility"]

    class Meta:
        abstract = True


class AnimalArea(models.Model):
    fencing_state = models.IntegerField(
        default=80, help_text="Fencing health percentage"
    )
    animal_health = models.IntegerField(
        default=80, help_text="Animal health percentage"
    )

    class Meta:
        abstract = True


class Field(GrowingArea):
    farm_space = models.OneToOneField(
        "FarmSpace", on_delete=models.CASCADE, null=True, related_name="field"
    )
    soil_health = models.IntegerField(default=80)
    improvable_fields = ["soil_health"]


class Orchard(GrowingArea):
    farm_space = models.OneToOneField(
        "FarmSpace", on_delete=models.CASCADE, null=True, related_name="orchard"
    )
    tree_health = models.IntegerField(default=80)
    fruit_quality = models.IntegerField(default=80)
    improvable_fields = ["fruit_quality", "tree_health"]


class AnimalPen(AnimalArea):
    farm_space = models.OneToOneField(
        "FarmSpace", on_delete=models.CASCADE, null=True, related_name="animal_pen"
    )
    capacity = models.IntegerField()
    cleanliness = models.IntegerField(default=80, help_text="Cleanliness percentage")
    improvable_fields = ["cleanliness"]


class Pasture(AnimalArea):
    farm_space = models.OneToOneField(
        "FarmSpace", on_delete=models.CASCADE, null=True, related_name="pasture"
    )
    grazing_quality = models.IntegerField(
        default=80, help_text="Grass quality percentage"
    )
    improvable_fields = ["grazing_quality"]


class FieldCrop(models.Model):
    field = models.ForeignKey(
        "Field", on_delete=models.CASCADE, related_name="field_crops"
    )
    crop = models.ForeignKey(
        "Crop", on_delete=models.CASCADE, related_name="field_crops"
    )
    size = models.IntegerField(help_text="Area in sq meters for this crop")

    def calculate_food_units(self):
        return self.crop.calculate_food_units() * self.size


class OrchardTree(models.Model):
    orchard = models.ForeignKey(
        "Orchard", on_delete=models.CASCADE, related_name="orchard_trees"
    )
    crop = models.ForeignKey(
        "Crop", on_delete=models.CASCADE, related_name="orchard_trees"
    )
    count = models.IntegerField(default=1)


class PenAnimal(models.Model):
    pen = models.ForeignKey(
        "AnimalPen", on_delete=models.CASCADE, related_name="pen_animals"
    )
    animal = models.ForeignKey(
        "Animal", on_delete=models.CASCADE, related_name="pen_animals"
    )
    count = models.IntegerField(default=1)


class PastureAnimal(models.Model):
    pasture = models.ForeignKey(
        "Pasture", on_delete=models.CASCADE, related_name="pasture_animals"
    )
    animal = models.ForeignKey(
        "Animal", on_delete=models.CASCADE, related_name="pasture_animals"
    )
    count = models.IntegerField(default=1)


##########################################################
##### PUBLIC SPACES  #####################################
##########################################################


class PublicSpace(models.Model):
    name = models.CharField(max_length=255)
    location = models.OneToOneField(
        "Location", on_delete=models.CASCADE, null=True, related_name="publicspace"
    )
    position = models.OneToOneField(
        "Position", on_delete=models.SET_NULL, null=True, related_name="publicspace"
    )
    size = models.IntegerField(blank=True, null=True)
    cleanliness = models.IntegerField(default=80)
    capacity = models.IntegerField(default=30)
    condition = models.IntegerField(default=50)
    reputation = models.IntegerField(default=50)
    improvable_fields = ["cleanliness", "condition", "reputation"]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str_(self):
        return self.name


class Market(models.Model):
    public_space = models.OneToOneField(
        "PublicSpace", on_delete=models.CASCADE, related_name="market"
    )

    def __str__(self):
        return f"Town Square at {self.parent_location.name}"


class Park(models.Model):
    public_space = models.OneToOneField(
        "PublicSpace", on_delete=models.CASCADE, related_name="park"
    )
    biodiversity = models.IntegerField(default=30)

    def __str__(self):
        return f"Park at {self.parent_location.name}"


class Cemetary(models.Model):
    public_space = models.OneToOneField(
        "PublicSpace", on_delete=models.CASCADE, related_name="cemetary"
    )

    def __str__(self):
        return f"Cemetary at {self.parent_location.name}"


##########################################################
##### FACTORY FUNCTION  ##################################
##########################################################


def create_location(location_type, name, position, parent_location=None, **kwargs):
    """Factory function to create locations of different types."""

    location = Location.objects.create(name=name, parent_location=parent_location)

    if location_type == "farm_space":
        farm_space = FarmSpace.objects.create(
            location=location, position=position, **kwargs
        )
        return pasture
    elif location_type == "public_space":
        public_space = PublicSpace.objects.create(
            location=location, position=position, **kwargs
        )
        return pasture
    elif location_type == "building":
        building = Building.objects.create(
            location=location, position=position, **kwargs
        )
        return building

    return location  # Return the generic Location if no specific type matches
