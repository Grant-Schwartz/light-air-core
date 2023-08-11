from fastapi import FastAPI
from fastapi.responses import Response
from typing import Optional
from pydantic import BaseModel
from datetime import date
from property import PropertyType, Property, PropertyLocation
from analysis import Timing
from apartment import ApartmentTenant, RollToMarket, RollToMarketStrategy, ExpenseType, ApartmentIncome, ApartmentExpense
from utils import JSONHandler
import json

class PropertyLocationModel(BaseModel):
    address: str
    city: str
    state: str
    zipcode: str

class AnalysisTimingModel(BaseModel):
    analysis_length_years: int
    analysis_start_date: date
    growth_begin_month: int
    residual_months: Optional[int] = 12

class ApartmentRollToMarketModel(BaseModel):
    strategy: RollToMarketStrategy
    start_month: Optional[int]

class ApartmentTenantModel(BaseModel):
    unit_name: str
    beds: float
    bath: float
    unit_size: int
    total_units: int
    units_lease_initial: int
    lease_up_pace: int
    in_place_rent: int
    roll_to_market: ApartmentRollToMarketModel
    market_rent: float
    rent_growth_matrix: dict
    utility_reimbursement: float
    make_ready_new_cost: float
    make_ready_renew_cost: float
    free_rent_new: float
    free_rent_renew: float
    free_rent_second_generation: bool
    renew_probability: float
    downtime: int

class ApartmentIncomeModel(BaseModel):
    name: str
    cagr: float
    percent_fixed: float
    base_amount: float

class ApartmentExpenseModel(BaseModel):
    name: str
    type: ExpenseType
    cagr: float
    percent_fixed: float
    base_amount: float

class ApartmentModel(BaseModel):
    name: str
    property_type: PropertyType
    location: PropertyLocationModel
    acres: float
    gross_buildable_area: int
    vacancy_rate: float
    timing: AnalysisTimingModel
    year_built: str
    tenants: list[ApartmentTenantModel]
    incomes: list[ApartmentIncomeModel]
    expenses: list[ApartmentExpenseModel]

app = FastAPI()

@app.get("/status")
async def status():
    return {"status": True, "message": "API Running"}

@app.post("/multi/calculate")
async def calculate(property_data: ApartmentModel):
    print(property_data)
    property = Property(
        name=property_data.name,
        property_type=property_data.property_type,
        location=PropertyLocation(
            address=property_data.location.address,
            city=property_data.location.city,
            state=property_data.location.state,
            zipcode=property_data.location.zipcode
        ),
        acres=property_data.acres,
        gross_buildable_area=property_data.gross_buildable_area,
        vacancy_rate=property_data.vacancy_rate,
        timing=Timing(
            analysis_length_years=property_data.timing.analysis_length_years,
            analysis_start_date=property_data.timing.analysis_start_date,
            growth_begin_month=property_data.timing.growth_begin_month,
            residual_months=property_data.timing.residual_months
        ),
        year_built=property_data.year_built,
    )
    for tenant_data in property_data.tenants:
        tenant = ApartmentTenant(
            unit_name=tenant_data.unit_name,
            beds=tenant_data.beds,
            bath=tenant_data.bath,
            unit_size=tenant_data.unit_size,
            total_units=tenant_data.total_units,
            units_lease_initial=tenant_data.units_lease_initial,
            lease_up_pace=tenant_data.lease_up_pace,
            in_place_rent=tenant_data.in_place_rent,
            roll_to_market=RollToMarket(
                strategy=tenant_data.roll_to_market.strategy,
                start_month=tenant_data.roll_to_market.start_month
            ),
            market_rent=tenant_data.market_rent,
            rent_growth_matrix={int(k):v for k,v in tenant_data.rent_growth_matrix.items()},
            utility_reimbursement=tenant_data.utility_reimbursement,
            make_ready_new_cost=tenant_data.make_ready_new_cost,
            make_ready_renew_cost=tenant_data.make_ready_renew_cost,
            free_rent_new=tenant_data.free_rent_new,
            free_rent_renew=tenant_data.free_rent_renew,
            free_rent_second_generation=tenant_data.free_rent_second_generation,
            renew_probability=tenant_data.renew_probability,
            downtime=tenant_data.downtime
        )
        property.add_tenant(tenant)
    for income_data in property_data.incomes:
        income = ApartmentIncome(
            name=income_data.name,
            cagr=income_data.cagr,
            percent_fixed=income_data.percent_fixed,
            base_amount=income_data.base_amount
        )
        property.add_income(income)
    for expense_data in property_data.expenses:
        expense = ApartmentExpense(
            name=expense_data.name,
            type=expense_data.type,
            cagr=expense_data.cagr,
            percent_fixed=expense_data.percent_fixed,
            base_amount=expense_data.base_amount
        )
        property.add_expense(expense)
    
    property.rent_roll()
    property.income_roll()
    property.expense_roll()

    property_calc_data = json.dumps(property, default=JSONHandler)

    return Response(content=property_calc_data)