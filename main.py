from timezone_correction import adjust_timezone
from app_logging import get_online_logger
from datetime import datetime
from tradier_api import TradierApi, MarketCalendar
from primary_functions import wait


# correct for timezone discrepancies
adjust_timezone()
# initialize logger - currently only a single logger at debug level
app_logger = get_online_logger(name='primary_logger')

def conditional_info_log(message: str, condition: bool = True):
    if condition:
        app_logger.info(message)


# initialize global variables
app_start_time = datetime.now()
current_dts = datetime.now()
main_loop_counter = 0
app_time_limit_in_seconds = 24 * 60 * 60
app_loop_limit = 20000
app_logger.info(f"global variables initialized")

# initialize market calendar (shouldn't need refreshed unless app running for weeks)
market_calendar = MarketCalendar(base_date=current_dts.date(), mo_hist=3, mo_fut=3)
current_market_state = market_calendar.get_market_state(eval_dts=current_dts, n_future=0)
next_market_state = market_calendar.get_market_state(eval_dts=current_dts, n_future=1)
next_market_state_at = next_market_state.start_dts
next_tradeable_market_state = market_calendar.get_tradeable_market_state(eval_dts=current_dts, n_future=1)
next_tradeable_market_state_at = next_tradeable_market_state.start_dts
app_logger.info(f"Current Market State: {current_market_state.name} is tradeable: {current_market_state.tradeable}")
# current_positions = TradierApi.get_account_positions()
# current_orders = TradierApi.get_account_orders()
# current_balances = TradierApi.get_account_balances()



cur_state = {'loop_started': None, 'date_state': None, 'day_type': None, 'market_state': None, 'position_state': None}
prev_state = cur_state.copy()

while True:
    main_loop_counter += 1
    # current_dts = datetime.now()
    # refresh market state if necessary (this is to limit the need to look up the market state every loop)
    # info_update = False
    # if current_dts >= next_market_state_at:
    #     current_market_state = market_calendar.get_market_state(eval_dts=current_dts, n_future=0)
    #     next_market_state = market_calendar.get_market_state(eval_dts=current_dts, n_future=1)
    #     next_market_state_at = next_market_state.start_dts
    #     next_tradeable_market_state = market_calendar.get_market_state(eval_dts=current_dts, n_future=1)
    #     next_tradeable_market_state_at = next_tradeable_market_state.start_dts
    #     app_logger.info(f"Current Market State: {current_market_state.name} Tradeable: {current_market_state.tradeable}")
    # if current_market_state.tradeable:
    #
    # else:
    #     time_until_next_tradeable_state = (next_tradeable_market_state.start_dts - current_dts).total_seconds()
    #     app_logger.info(f"Next Tradeable Market State: {next_tradeable_market_state.name}")
    #     app_logger.info(f"Time Until Next Tradeable Market State: {time_until_next_tradeable_state}")
    cur_state.update({'loop_started': True})  # logging
    conditional_info_log(message=f"Main loop initialized", condition=cur_state != prev_state)  # logging
    current_dts = datetime.now()
    today = market_calendar.get_day(day=current_dts)
    if today.is_market_day():
        cur_state.update({'date_state': f'open on {current_dts.date().isoformat()}'})  # logging
        conditional_info_log(message=f"Market open today", condition=cur_state != prev_state)  # logging
        if today.market_open <= current_dts <= today.market_close:
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
        elif current_dts <= today.market_open:
            cur_state.update({'market_state': 'before_open'})  # logging
            conditional_info_log(message=f"Market not yet open today", condition=cur_state != prev_state)  # logging
            time_until_market_open = (today.market_open - current_dts).total_seconds()
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
        elif current_dts >= today.market_close:
            cur_state.update({'market_state': 'after_close'})  # logging
            conditional_info_log(message=f"Market already closed for the day", condition=cur_state != prev_state)  # logging
            # market closed for the day, wait a while
            wait(sleep_time_sec=3600)
        else:
            app_logger.warning(f"Market status for day / time mismatch")  # logging
            app_logger.debug(f"Today market status: {today.status}")  # logging
            app_logger.debug(f"Today market description {today.description}")  # logging
            app_logger.debug(f"Today Market Open Time: {today.market_open.isoformat()}")  # logging
            app_logger.debug(f"Today Market Close Time: {today.market_close.isoformat()}")  # logging
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





