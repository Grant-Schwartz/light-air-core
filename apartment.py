from enum import Enum
from analysis import Timing
import numpy as np

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
    
    def json(self):
        return self.__dict__

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
        rent_growth_matrix: dict,
        utility_reimbursement: float,
        make_ready_new_cost: float,
        make_ready_renew_cost: float,
        free_rent_new: float,
        free_rent_renew: float,
        free_rent_second_generation: bool,
        renew_probability: float,
        downtime: int
    ):
        # UNIT INFO
        self.unit_name = unit_name
        self.beds = beds
        self.bath = bath
        self.unit_size = unit_size
        self.total_units = total_units

        # UNIT LEASE INFO
        self.units_lease_initial = units_lease_initial
        self.vacant_units_initial = total_units - units_lease_initial
        self.lease_up_pace = lease_up_pace

        # UNIT RENT INFO
        self.in_place_rent = in_place_rent
        self.market_rent = market_rent
        self.roll_to_market = roll_to_market
        self.rent_growth_matrix = rent_growth_matrix

        # UNIT TI & COSTS INFO
        self.utility_reimbursement = utility_reimbursement
        self.make_ready_new_cost = make_ready_new_cost
        self.make_ready_renew_cost = make_ready_renew_cost
        
        # UNIT GENERATION INFO
        self.free_rent_new = free_rent_new
        self.free_rent_renew = free_rent_renew
        self.free_rent_second_generation = free_rent_second_generation
        self.renew_probability = renew_probability
        self.downtime = downtime

        # RENT ROLL VARS
        self.market_rents = []
        self.units_leased = []
        self.total_rent = []
        self.loss_to_lease = []
        self.make_ready_untrended = []
        self.first_generation_free_rent = []
        self.second_generation_free_rent = []
        self.downtime_cost = []


    def get_growth_rate(self, timing: Timing, month: int):
        if month >= timing.growth_begin_month and (month - timing.growth_begin_month) % 12 == 0:
            return self.rent_growth_matrix[month] * (((month - timing.growth_begin_month) // 12) + 1)
        else:
            return 0.0
        
    def get_base_rent(self, timing: Timing, month: int):
        if self.roll_to_market.strategy == RollToMarketStrategy.YES and month >= timing.growth_begin_month:
            return self.market_rent
        elif self.roll_to_market.strategy == RollToMarketStrategy.IN_MONTH and month >= self.roll_to_market.start_month:
            return self.market_rent
        else:
            return self.in_place_rent

    def gen_market_rents(self, timing: Timing):        
        rents = []
        last_rate = 0.0
        for month in range(1, timing.analysis_length_months+1):
            base_rent = self.get_base_rent(timing, month)
            growth_rate = self.get_growth_rate(timing, month)
            if last_rate < growth_rate:
                last_rate = growth_rate
            true_rent = base_rent * (1 + last_rate)
            
            rents.append(true_rent)
        
        return rents
    
    def gen_units_leased(self, timing: Timing):
        units_leased = [self.units_lease_initial]
        for _ in range(2, timing.analysis_length_months+1):
            if units_leased[-1] + self.lease_up_pace < self.total_units:
                units_leased.append(units_leased[-1] + self.lease_up_pace)
            else:
                units_leased.append(self.total_units)
        
        return units_leased

    def gen_loss_to_lease(self, rents: list[float], units_leased: list[int], timing: Timing):
        loss_to_lease = []
        for month in range(len(units_leased)):
            loss = (self.total_units - units_leased[month]) * rents[month]
            loss_to_lease.append(loss)
        
        return loss_to_lease

    def gen_untrended_make_ready(self, units_leased: list[int], timing: Timing):
        make_ready_blended = (self.make_ready_renew_cost * self.renew_probability) + ((1 - self.renew_probability) * self.make_ready_new_cost)
        make_ready_cost = []
        for month in range(timing.analysis_length_months):
            if units_leased[month] < self.total_units:
                make_ready_cost.append(0)
            else:
                make_ready_cost.append((self.total_units / 12)*make_ready_blended)
        
        return make_ready_cost
    
    def gen_first_generation_free_rent(self, units_leased: list[int], rents: list[float], timing: Timing) -> list[float]:
        free_rent = []
        last_month_units_leased = 0
        for month in range(timing.analysis_length_months):
            if units_leased[month] < self.total_units:
                amount = (units_leased[month] - last_month_units_leased) * self.free_rent_new * rents[month]
                last_month_units_leased = units_leased[month]
                free_rent.append(amount)
            else:
                free_rent.append(0.0)

        return free_rent
    
    def gen_second_generation_free_rent(self, units_leased: list[int], rents: list[float], timing: Timing) -> list[float]:
        free_rent = []
        for month in range(timing.analysis_length_months):
            if month >= timing.growth_begin_month:
                renewed_units = ((self.total_units - (self.total_units - units_leased[month])) / 12) * self.renew_probability
                new_units = ((self.total_units - (self.total_units - units_leased[month])) / 12) * (1 - self.renew_probability)

                amount = renewed_units * self.free_rent_renew * rents[month] + new_units * self.free_rent_new * rents[month]

                free_rent.append(amount) 
            else:
                free_rent.append(0.0)
        
        return free_rent

    def gen_downtime(self, units_leased: list[int], rents: list[float], timing: Timing):
        downtime_matrix = []
        blended_downtime = (self.downtime * (1 - self.renew_probability)) / 365
        for month in range(timing.analysis_length_months):
            if month >= timing.growth_begin_month:
                amount = blended_downtime * units_leased[month] * rents[month]
                downtime_matrix.append(amount)
            else:
                downtime_matrix.append(0.0)

        return downtime_matrix

    def rent_roll(self, timing: Timing):
        self.market_rents = self.gen_market_rents(timing)
        self.units_leased = self.gen_units_leased(timing)

        self.total_rent = [self.market_rents[month] * self.units_leased[month] for month in range(len(self.market_rents))]
        self.loss_to_lease = self.gen_loss_to_lease(self.market_rents, self.units_leased, timing)

        self.make_ready_untrended = self.gen_untrended_make_ready(self.units_leased, timing)
        
        self.first_generation_free_rent = self.gen_first_generation_free_rent(self.units_leased, self.market_rents, timing)
        self.second_generation_free_rent = self.gen_second_generation_free_rent(self.units_leased, self.market_rents, timing)
        
        self.downtime_cost = self.gen_downtime(self.units_leased, self.market_rents, timing)

        return {
            "market_rents": np.array(self.market_rents),
            "units_leased": np.array(self.units_leased),
            "total_rent": np.array(self.total_rent),
            "loss_to_lease": np.array(self.loss_to_lease),
            "make_ready": np.array(self.make_ready_untrended),
            "first_generation_free_rent": np.array(self.first_generation_free_rent),
            "second_generation_free_rent":  np.array(self.second_generation_free_rent),
            "downtime_cost": np.array(self.downtime_cost)
        }

    def json(self):
        return self.__dict__

class ApartmentIncome:

    def __init__(self, name: str, cagr: float, percent_fixed: float, base_amount: float):
        self.name: str = name
        self.per_unit: float = 0.0
        self.cagr: float = cagr
        self.percent_fixed: float = percent_fixed
        self.base_amount: float = base_amount
        self.calculated = []

    def roll(self, physical_occupancy: list[float], timing: Timing):
        calculated_income = []
        for month in range(timing.analysis_length_months):
            year = month // timing.growth_begin_month
            month_income = (self.percent_fixed * self.base_amount / 12)+((1 - self.percent_fixed)*self.base_amount*physical_occupancy[month]/12)*(1+self.cagr)**year
            calculated_income.append(month_income)
        
        self.calculated = np.array(calculated_income)
        return self.calculated

    def json(self):
        return self.__dict__

class ExpenseType(Enum):
    CAPEX: str = "CapEx"
    OPEX: str = "OpEx"


class ApartmentExpense:

    def __init__(self, name: str, type: ExpenseType, cagr: float, percent_fixed: float, base_amount: float):
        self.name: str = name
        self.type: ExpenseType = type
        self.per_unit: float = 0.0
        self.cagr: float = cagr
        self.percent_fixed: float = percent_fixed
        self.base_amount: float = base_amount
        self.calculated = []

    def roll(self, physical_occupancy: list[float], timing: Timing):
        calculated_expense = []
        for month in range(timing.analysis_length_months):
            year = month // timing.growth_begin_month
            month_income = (self.percent_fixed * self.base_amount / 12)+((1 - self.percent_fixed)*self.base_amount*physical_occupancy[month]/12)*(1+self.cagr)**year
            calculated_expense.append(month_income)
        
        self.calculated = np.array(calculated_expense)
        return self.calculated
    
    def json(self):
        return self.__dict__
