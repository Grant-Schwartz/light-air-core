from datetime import date
from dateutil.relativedelta import relativedelta

class Timing:

    def calc_growth_begin_date(
        self,
        growth_begin_month: int,
        analysis_start_date: date
    ) -> date:
        return analysis_start_date+relativedelta(months=growth_begin_month-1)

    
    def __init__(
        self,
        analysis_length_years: int,
        analysis_start_date: date,
        growth_begin_month: int,
        residual_months: int=12
    ):
        self.analysis_length_years = analysis_length_years
        self.analysis_length_months = analysis_length_years * 12

        self.analysis_start_date = analysis_start_date
        self.analysis_start_month = 1
        self.residual_months = residual_months

        self.growth_begin_month = growth_begin_month
        self.growth_begin_date = self.calc_growth_begin_date(growth_begin_month, analysis_start_date)