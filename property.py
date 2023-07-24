from enum import Enum
from analysis import Timing
from datetime import date

class PropertyType(Enum):
    APARTMENT = "Apartment"

class PropertyLocation:

    def __init__(
        self,
        address: str,
        city: str,
        state: str,
        zipcode: str
    ):
        self.address = address,
        self.city = city,
        self.state = state
        self.zipcode = zipcode


class Property:

    def __init__(
        self,
        name: str,
        property_type: PropertyType,
        location: PropertyLocation,
        acres: float,
        gross_buildable_area: int,
        timing: Timing,
        year_built: str,
        year_renovated: str|None=None,
    ):
        self.name = name,
        self.property_type = property_type,
        self.location = location,
        self.acres = acres,
        self.gross_buildable_area = gross_buildable_area
        self.year_built = year_built
        self.year_renovated = year_renovated
        self.timing = timing