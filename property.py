from enum import Enum
from analysis import Timing
from datetime import date
from apartment import ApartmentTenant, RollToMarket, RollToMarketStrategy

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
        tenants: list=[]
    ):
        self.name = name,
        self.property_type = property_type,
        self.location = location,
        self.acres = acres,
        self.gross_buildable_area = gross_buildable_area
        self.year_built = year_built
        self.year_renovated = year_renovated
        self.timing = timing
        self.tenants = tenants
    
    def add_tenant(self,tenant):
        self.tenants.append(tenant)
        
    def rent_roll(self):
        for tenant in self.tenants:
            tenant.rent_roll(timing=self.timing)

prop = Property(
    name="Home",
    property_type=PropertyType.APARTMENT,
    location=PropertyLocation("250 W 82nd St", "New York", "NY", "10024"),
    acres=8.6,
    gross_buildable_area=100000,
    year_built="2016",
    timing=Timing(10, date(2024,1,1), 13)
)

tenant1 = ApartmentTenant(
    unit_name="A1",
    beds=1,
    bath=1,
    unit_size=650,
    total_units=90,
    units_lease_initial=50,
    lease_up_pace=15,
    in_place_rent=1050,
    roll_to_market=RollToMarket(RollToMarketStrategy.YES, 25),
    market_rent=2000,
    rent_growth_matrix={13: 0.03, 25: 0.03, 37: 0.03, 49: 0.03, 61: 0.03, 73: 0.03, 85: 0.03, 97: 0.03, 109: 0.03, 121: 0.03},
    utility_reimbursement=60,
    make_ready_new_cost=550,
    make_ready_renew_cost=150,
    free_rent_new=1,
    free_rent_renew=0.5,
    free_rent_second_generation=False,
    renew_probability=0.6,
    downtime=10
)

prop.add_tenant(tenant1)
prop.rent_roll()