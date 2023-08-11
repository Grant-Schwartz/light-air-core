from enum import Enum
from analysis import Timing
from datetime import date, datetime
from apartment import ApartmentTenant, RollToMarket, RollToMarketStrategy, ApartmentIncome, ApartmentExpense, ExpenseType
import numpy as np
import json
from utils import JSONHandler

class PropertyType(str, Enum):
    APARTMENT = "Apartment"

class PropertyLocation:

    def __init__(
        self,
        address: str,
        city: str,
        state: str,
        zipcode: str
    ):
        self.address: str = address,
        self.city: str = city,
        self.state: str = state
        self.zipcode: str = zipcode
    
    def json(self):
        return self.__dict__


class Property:

    def __init__(
        self,
        name: str,
        property_type: PropertyType,
        location: PropertyLocation,
        acres: float,
        gross_buildable_area: int,
        vacancy_rate: float,
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
        self.vacancy_rate = vacancy_rate

        self.physical_occupancy = []

        self.rental_revenue = {}
        self.rental_revenues = []

        self.incomes = []
        self.total_other_income = []
        self.total_potential_gross_income = []
        self.general_vacancy = []
        self.effective_gross_income = []

        self.opex = []
        self.capex = []
        self.total_expenses = []

        self.noi = []
        self.cf_from_operations = []
    
    def add_tenant(self,tenant):
        self.tenants.append(tenant)
        
    def rent_roll(self):
        for tenant in self.tenants:
            tenant_data = tenant.rent_roll(timing=self.timing)
            self.rental_revenues.append(tenant_data)
            
        self.calc_rental_revenue()
        return

    def calc_physical_occupancy(self):
        total_leased_units = np.zeros(self.timing.analysis_length_months)
        total_units = 0
        for tenant in self.tenants:
            total_leased_units = np.add(total_leased_units, tenant.units_leased)
            total_units += tenant.total_units
        
        self.physical_occupancy = total_leased_units / total_units
        return

    def calc_rental_revenue(self):
        empty_field = np.zeros(self.timing.analysis_length_months)
        total_rental_revenue = {
            "gross_revenue": empty_field,
            "concessions": empty_field,
            "downtime_loss_to_lease": empty_field
        }
        for unit in self.rental_revenues:
            unit["gross_revenue"] = unit["market_rents"] * unit["units_leased"]
            unit["concessions"] = np.add(unit["first_generation_free_rent"], unit["second_generation_free_rent"])
            unit["downtime_loss_to_lease"] = np.add(unit["downtime_cost"], unit["loss_to_lease"])

            total_rental_revenue["gross_revenue"] += unit["gross_revenue"]
            total_rental_revenue["concessions"] += unit["concessions"]
            total_rental_revenue["downtime_loss_to_lease"] += unit["downtime_loss_to_lease"]

        total_rental_revenue["total_rental_revenue"] = total_rental_revenue["gross_revenue"] - total_rental_revenue["concessions"] - total_rental_revenue["downtime_loss_to_lease"]
        self.rental_revenue = total_rental_revenue

        return

    def add_income(self, income_stream):
        self.incomes.append(income_stream)

    def income_roll(self):
        self.calc_physical_occupancy()
        total_other_income = np.zeros(self.timing.analysis_length_months)
        for income in self.incomes:
            roll_data = income.roll(physical_occupancy=self.physical_occupancy, timing=self.timing)
            total_other_income += roll_data

        self.total_other_income = total_other_income
        self.total_potential_gross_income = self.rental_revenue["gross_revenue"] + total_other_income
        self.general_vacancy = self.total_potential_gross_income * self.vacancy_rate
        self.effective_gross_income = self.total_potential_gross_income - self.general_vacancy
        return
    
    def add_expense(self, expense_stream):
        if expense_stream.type == ExpenseType.CAPEX:
            self.capex.append(expense_stream)
        elif expense_stream.type == ExpenseType.OPEX:
            self.opex.append(expense_stream)
    
    def expense_roll(self):
        self.calc_physical_occupancy()
        total_opex = np.zeros(self.timing.analysis_length_months)
        total_capex = np.zeros(self.timing.analysis_length_months)

        for expense in self.opex:
            roll_data = expense.roll(physical_occupancy=self.physical_occupancy, timing=self.timing)
            total_opex += roll_data
        
        for expense in self.capex:
            roll_data = expense.roll(physical_occupancy=self.physical_occupancy, timing=self.timing)
            total_capex += roll_data
        
        self.opex = total_opex
        self.capex = total_capex

        self.noi = self.effective_gross_income - self.opex
        self.total_expenses = self.opex + self.capex
        self.cf_from_operations = self.noi - self.capex

        return
    
    def json(self):
        return self.__dict__


prop = Property(
    name="Home",
    property_type=PropertyType.APARTMENT,
    location=PropertyLocation("250 W 82nd St", "New York", "NY", "10024"),
    acres=8.6,
    gross_buildable_area=100000,
    vacancy_rate=0.05,
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

rubs = ApartmentIncome(
    name="Utility Reimbursement",
    cagr=.02,
    percent_fixed=0,
    base_amount=93600,
)
parking = ApartmentIncome(
    name="Parking",
    cagr=.02,
    percent_fixed=0,
    base_amount= 120375
)
storage = ApartmentIncome(
    name="Storage",
    cagr=.02,
    percent_fixed=0,
    base_amount=10098,
)
other = ApartmentIncome(
    name="Other",
    cagr=.02,
    percent_fixed=0,
    base_amount=128454,
)
payroll = ApartmentExpense(
    name="Payroll",
    type=ExpenseType.OPEX,
    cagr=.02,
    percent_fixed=.75,
    base_amount=70000
)


prop.add_tenant(tenant1)
prop.rent_roll()
prop.add_income(rubs)
prop.add_income(parking)
prop.add_income(storage)
prop.add_income(other)
prop.income_roll()
prop.add_expense(payroll)
prop.expense_roll()

print(json.dumps(prop, default=JSONHandler))
