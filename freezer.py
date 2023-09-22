from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
from tradier_api import TradierApi
from time import sleep
from typing import Union


def should_continue(start_time: datetime, time_limit_sec: int = 30) -> bool:
    # function to determine if app should continue running
    if (datetime.now() - start_time).total_seconds() >= time_limit_sec:
        return False
    else:
        return True


def get_market_calendar(start_time: datetime, n_months: int = 3):
    mkt_cal = []
    # number of months
    n = n_months
    for i in range(0, n + 1, 1):
        temp_date = start_time + relativedelta(months=i)
        api_response = TradierApi.get_market_calendar(month=temp_date.month, year=temp_date.year)
        mkt_cal_temp = api_response.flattened_data()
        mkt_cal += mkt_cal_temp
    return mkt_cal


def market_open(mkt_cal) -> bool:
    current_dts = datetime.now()
    mkt_cal_day = [day for day in mkt_cal if date.fromisoformat(day['date']) == current_dts.date()][0]
    if mkt_cal_day['status'] == 'open':
        if time.fromisoformat(mkt_cal_day['open']['start']) <= current_dts.time() <= time.fromisoformat(mkt_cal_day['open']['end']):
            output = True
        else:
            output = False
    else:
        output = False
    return output


def time_to_market_close(mkt_cal):
    output = None
    current_dts = datetime.now()
    mkt_cal_day = [day for day in mkt_cal if date.fromisoformat(day['date']) == current_dts.date()][0]
    if mkt_cal_day['status'] == 'open':
        close_dts = datetime.combine(date=current_dts.date(), time=time.fromisoformat(mkt_cal_day['open']['end']))
        if close_dts > current_dts:
            output = (close_dts - current_dts).total_seconds()
    return output


def market_close_time(mkt_cal, input_date: date):
    output = None
    mkt_cal_day = [day for day in mkt_cal if date.fromisoformat(day['date']) == input_date][0]
    if mkt_cal_day['status'] == 'open':
        output = datetime.combine(date=input_date, time=time.fromisoformat(mkt_cal_day['open']['end']))
    return output

# expiration = q.expiration_dt()
# position_profit_loss_pct = (current_price - position_cost_per_contract) / position_cost_per_contract
# is_friday = datetime.now().isoweekday() == 5
# seconds_to_close = time_to_market_close(market_calendar)
# sec_to_expiry = (market_close_time(mkt_cal=market_calendar, input_date=expiration) - datetime.now()).total_seconds()





