from property import Property, PropertyType, PropertyLocation
from analysis import Timing
from datetime import date
from enum import Enum

class RollToMarketStrategy(Enum):
    IN_MONTH = "In Month"
    YES = "Yes"
    NO = "No"

class RollToMarket:
    def __init__(self, strategy: RollToMarketStrategy, start_month: int|None):
        if strategy == RollToMarketStrategy.IN_MONTH and start_month is None:
            raise ValueError("Please provide a month for your roll to market strategy")
        self.strategy = strategy
        self.start_month = start_month

class RentGrowthStrategy(Enum):
    INCREASE_PER_YEAR = "Inc. %/Year",
    DETAIL = "Detailed"

class RentGrowth:
    def __init__(self, growth_percentage: float|None=None, growth_percentage_matrix: list[float]|None=None):
        if growth_percentage is None and growth_percentage_matrix is None:
            raise ValueError("Please provide rent growth or detailed rent growth matrix")
        elif growth_percentage is not None and growth_percentage_matrix is None:
            self.rent_growth_stradegy: RentGrowthStrategy = RentGrowthStrategy.INCREASE_PER_YEAR
            self.growth_percentage = growth_percentage
        elif growth_percentage is not None and growth_percentage_matrix is None:
            self.rent_growth_stradegy: RentGrowthStrategy = RentGrowthStrategy.DETAIL
            self.growth_percentage_matrix: list[float] = growth_percentage_matrix
        else:
            raise ValueError("Please only provide a rent growth rate or detailed rent growth")

class ApartmentTenant:
    def __init__(
        self,
        unit_name: str,
        beds: float,
        bath: float,
        unit_size: int,
        total_units: int,
        units_lease_initial: int,
        lease_up_pace: int,
        in_place_rent: int,
        roll_to_market: RollToMarket,
        market_rent: float,
        rent_growth: RentGrowth,
        utility_reimbursement: float,
        make_ready_new_cost: float,
        make_ready_renew_cost: float,
        free_rent_new: float,
        free_rent_renew: float,
        free_rent_second_generation: bool,
        renew_probability: float,
        downtime: int
    ):
        self.unit_name = unit_name
        self.beds = beds
        self.bath = bath
        self.unit_size = unit_size
        self.total_units = total_units
        self.units_lease_initial = units_lease_initial,
        self.vacant_units_initial = total_units - units_lease_initial
        self.initial_occupancy = units_lease_initial / total_units
        self.lease_up_pace = lease_up_pace
        self.in_place_rent = in_place_rent
        self.roll_to_market = roll_to_market
        self.rent_growth = rent_growth
        self.utility_reimbursement = utility_reimbursement
        self.make_ready_new_cost = make_ready_new_cost
        self.make_ready_renew_cost = make_ready_renew_cost
        self.free_rent_new = free_rent_new
        self.free_rent_renew = free_rent_renew
        self.free_rent_second_generation = free_rent_second_generation
        self.renew_probability = renew_probability
        self.downtime = downtime

class Apartment(Property):
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
        tenants: list[ApartmentTenant]=[]
    ):
        super().__init__(name, property_type, location, acres, gross_buildable_area, timing, year_built, year_renovated)
        self.tenants: list[ApartmentTenant] = tenants

    def add_tenant(self, tenant: ApartmentTenant):
        self.tenants.append(tenant)

app = Apartment(
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
    units_lease_initial=90,
    lease_up_pace=15,
    in_place_rent=1050,
    roll_to_market=RollToMarket(RollToMarketStrategy.IN_MONTH, 25),
    market_rent=1050,
    rent_growth=RentGrowth(.03),
    utility_reimbursement=60,
    make_ready_new_cost=550,
    make_ready_renew_cost=150,
    free_rent_new=1,
    free_rent_renew=0.5,
    free_rent_second_generation=False,
    renew_probability=0.6,
    downtime=10
)