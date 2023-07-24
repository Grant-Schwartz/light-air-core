from enum import Enum
from typing import Optional

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
        year_built: str,
        year_renovated: str|None=None
    ):
        self.name = name,
        self.property_type = property_type,
        self.location = location,
        self.acres = acres,
        self.gross_buildable_area = gross_buildable_area
        self.year_built = year_built
        self.year_renovated = year_renovated
        
test = Property(
    name="Home",
    property_type=PropertyType.APARTMENT,
    location=PropertyLocation("250 W 82nd St", "New York", "NY", "10024"),
    acres=8.6,
    gross_buildable_area=100000,
    year_built="2016"
)