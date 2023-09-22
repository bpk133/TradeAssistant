from sys import platform
import logging
import os
import time
from datetime import datetime
from app_logging import get_online_logger
from tradier_api import TradierApi, MarketCalendar
from primary_functions import wait


# determine machine OS
machine_os = None
if platform == "linux" or platform == "linux2":
    machine_os = 'linux'
elif platform == "darwin":
    machine_os = 'mac'
elif platform == "win32":
    machine_os = 'win'

# if linux and not EST, set timezone to EST (applying to python environment only)
if machine_os == 'linux':
    if time.tzname == ('UTC', 'UTC'):
        os.environ['TZ'] = 'US/Eastern'
        time.tzset()


# initialize logger
app_logger = get_online_logger(name='primary_logger', level=logging.DEBUG)

# initialize global variables
app_start_time = datetime.now()
current_dts = datetime.now()
main_loop_counter = 0
app_time_limit_in_seconds = 24 * 60 * 60
app_loop_limit = 20000
app_logger.info(f"global variables initialized")

# initialize market calendar (shouldn't need refreshed unless app running for weeks)
market_calendar = MarketCalendar(calendar_days=TradierApi.get_market_calendar_range(base_date=current_dts))

# don't want to log everything, only when something changes or goes wrong
# has day changed?
# has market state changed?
# has positions state changed?
# has profitability changed?


def conditional_info_log(message: str, condition: bool = True):
    if condition:
        app_logger.info(message)


cur_state = {'loop_started': None, 'date_state': None, 'day_type': None, 'market_state': None, 'position_state': None}
prev_state = cur_state.copy()

while True:
    main_loop_counter += 1
    cur_state.update({'loop_started': True})  # logging
    conditional_info_log(message=f"Main loop initialized", condition=cur_state != prev_state)  # logging
    current_dts = datetime.now()
    today = market_calendar.get_day(day=current_dts)
    if today.is_market_open_day():
        cur_state.update({'date_state': f'open on {current_dts.date().isoformat()}'})  # logging
        conditional_info_log(message=f"Market open today", condition=cur_state != prev_state)  # logging
        if today.open_market.start <= current_dts <= today.open_market.end:
            cur_state.update({'market_state': 'open'})  # logging
            conditional_info_log(message=f"Market currently open", condition=cur_state != prev_state)  # logging
            positions = TradierApi.get_account_positions()
            if positions:
                cur_state.update({'position_state': 'open'})  # logging
                conditional_info_log(message=f"Positions currently open", condition=cur_state != prev_state)  # logging
                quotes = TradierApi.get_quotes(symbols=[p.symbol for p in positions])
                for quo, pos in zip(quotes, positions):
                    if quo.symbol == pos.symbol:
                        if quo.type == 'option':
                            conditional_info_log(message=f"Option position open for: {quo.description}",
                                                 condition=main_loop_counter % 20 == 0)  # logging
                            option_purchase_price = pos.unit_cost() / 100
                            option_current_price = quo.last
                            option_profit_pct = (option_current_price - option_purchase_price) / option_purchase_price
                            conditional_info_log(message=f'Option current profit: {option_profit_pct}',
                                                 condition=main_loop_counter % 20 == 0)  # logging
                            # also need to check for open orders
                            if option_profit_pct >= 0.20:
                                app_logger.info(f"Option position profitible enough to sell")  # logging
                                # sell option - first preview, then execute (required order of operations by API)
                                response_sell_preview = TradierApi.post_option_order(underlying_symbol=quo.underlying,
                                                                                     option_symbol=quo.symbol,
                                                                                     side='sell_to_close',
                                                                                     quantity=pos.quantity,
                                                                                     order_type='market',
                                                                                     duration='day')
                                app_logger.info(f"Option sell order preview {response_sell_preview}")  # logging
                                response_sell = TradierApi.post_option_order(underlying_symbol=quo.underlying,
                                                                             option_symbol=quo.symbol,
                                                                             side='sell_to_close',
                                                                             quantity=pos.quantity,
                                                                             order_type='market',
                                                                             duration='day',
                                                                             preview=False)
                                app_logger.info(f"Option sell order created: {response_sell}")  # logging
                            else:
                                conditional_info_log(message=f"Option position not profitable enough to sell",
                                                     condition=main_loop_counter % 20 == 0)  # logging
                                # move on for now
                                pass
                        else:
                            conditional_info_log(message=f"Position is not an option position",
                                                 condition=main_loop_counter % 20 == 0)  # logging
                            # not an option, check the next position
                            pass
                    else:
                        app_logger.debug(f"Mismatch in position and quote list order")  # logging
                        app_logger.debug(f"Position symbol: {pos.symbol} Quote symbol: {quo.symbol}")  # logging
                # after checking all positions, need to wait again
                # open positions so don't wait long
                conditional_info_log(message=f"All positions evaluated", condition=main_loop_counter % 20 == 0)  # logging
                wait(sleep_time_sec=5)
            else:
                cur_state.update({'position_state': 'none open'})  # logging
                conditional_info_log(message=f"No open positions", condition=cur_state != prev_state)  # logging
                wait(sleep_time_sec=15)
        elif current_dts <= today.open_market.start:
            cur_state.update({'market_state': 'before_open'})  # logging
            conditional_info_log(message=f"Market not yet open today", condition=cur_state != prev_state)  # logging
            time_until_market_open = (today.open_market.start - current_dts).total_seconds()
            app_logger.info(f"Time til market open {round(time_until_market_open)} seconds")  # logging
            if time_until_market_open >= 2 * 3600:
                # more than 2 hours, wait 1 hour
                wait(sleep_time_sec=3600)
            elif time_until_market_open >= 3600:
                # more than 1 hour, wait 30 minutes
                wait(sleep_time_sec=1800)
            elif time_until_market_open >= 1800:
                # more than 30 minutes, wait 15 minutes
                wait(sleep_time_sec=900)
            elif time_until_market_open >= 900:
                # more than 15 minutes, wait 5 minute
                wait(sleep_time_sec=300)
            elif time_until_market_open >= 300:
                # more than 5 minutes, wait 1 minute
                wait(sleep_time_sec=60)
            elif time_until_market_open >= 60:
                # more than 1 minute, wait 30 seconds
                wait(sleep_time_sec=30)
            else:
                wait(sleep_time_sec=5)
        elif current_dts >= today.open_market.end:
            cur_state.update({'market_state': 'after_close'})  # logging
            conditional_info_log(message=f"Market already closed for the day", condition=cur_state != prev_state)  # logging
            # market closed for the day, wait a while
            wait(sleep_time_sec=3600)
        else:
            app_logger.warning(f"Market status for day / time mismatch")  # logging
            app_logger.debug(f"Today market status: {today.status}")  # logging
            app_logger.debug(f"Today market description {today.description}")  # logging
            app_logger.debug(f"Today Market Open Time: {today.open_market.start.isoformat()}")  # logging
            app_logger.debug(f"Today Market Close Time: {today.open_market.end.isoformat()}")  # logging
            app_logger.debug(f"Current Time: {current_dts.isoformat()}")  # logging
    else:
        cur_state.update({'date_state': f'open on {current_dts.date().isoformat()}'})  # logging
        cur_state.update({'market_state': 'closed'})  # logging
        conditional_info_log(message=f"Market closed today", condition=cur_state != prev_state)  # logging
        wait(sleep_time_sec=3600)
    if (current_dts - app_start_time).total_seconds() >= app_time_limit_in_seconds:
        app_logger.info(f"Main loop ending due to time limit being reached")  # logging
        break
    elif main_loop_counter >= app_loop_limit:
        app_logger.info(f"Main loop ending due to loop limit being reached")  # logging
        break
    prev_state = cur_state.copy()  # logging


app_logger.info(f"App terminated")  # logging





