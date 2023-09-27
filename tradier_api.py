import requests
from requests.exceptions import RequestException
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
from typing import Union, List, Dict
from creds import tradier_api_creds
import logging

# prevent urllib from logging every single request
urllib_logger = logging.getLogger('urllib3.connectionpool')
urllib_logger.setLevel(logging.ERROR)


def dict_to_list_of_dict(data: Union[List, Dict, None]) -> Union[List[Dict], None]:
    if data:
        if isinstance(data, dict):
            data = [data]
    return data


class TradierApiBase:
    _brokerage_request_endpoint = r'https://api.tradier.com/v1/'
    _brokerage_streaming_endpoint = r'https://stream.tradier.com/v1/'
    _sandbox_request_endpoint = r'https://sandbox.tradier.com/v1/'
    _brokerage_api_key = tradier_api_creds['brokerage']['key']
    _brokerage_account_id = tradier_api_creds['brokerage']['account']
    _sandbox_api_key = tradier_api_creds['sandbox']['key']
    _sandbox_account_id = tradier_api_creds['sandbox']['account']
    _legacy_sandbox_api_key = tradier_api_creds['legacy_sandbox']['key']
    _legacy_sandbox_account_id = tradier_api_creds['legacy_sandbox']['account']
    _request_endpoint = _brokerage_request_endpoint
    _streaming_endpoint = _brokerage_streaming_endpoint
    _api_key = _brokerage_api_key
    _account_id = _brokerage_account_id
    _request_headers = {'Authorization': f"Bearer {_api_key}", 'Accept': 'application/json'}

    @classmethod
    def use_brokerage(cls) -> None:
        cls._request_endpoint = cls._brokerage_request_endpoint
        cls._streaming_endpoint = cls._brokerage_streaming_endpoint
        cls._api_key = cls._brokerage_api_key
        cls._account_id = cls._brokerage_account_id
        cls._request_headers = {'Authorization': f"Bearer {cls._api_key}", 'Accept': 'application/json'}

    @classmethod
    def use_sandbox(cls) -> None:
        cls._request_endpoint = cls._sandbox_request_endpoint
        # cls._streaming_endpoint = cls._brokerage_streaming_endpoint
        cls._api_key = cls._sandbox_api_key
        cls._account_id = cls._sandbox_account_id
        cls._request_headers = {'Authorization': f"Bearer {cls._api_key}", 'Accept': 'application/json'}

    @classmethod
    def use_legacy_sandbox(cls) -> None:
        cls._request_endpoint = cls._sandbox_request_endpoint
        # cls._streaming_endpoint = cls._brokerage_streaming_endpoint
        cls._api_key = cls._legacy_sandbox_api_key
        cls._account_id = cls._legacy_sandbox_account_id
        cls._request_headers = {'Authorization': f"Bearer {cls._api_key}", 'Accept': 'application/json'}

    @classmethod
    def request(cls, method, url, **kwargs) -> Union[Dict, None]:
        results = None
        try:
            response = requests.request(method=method, url=url, headers=cls._request_headers, **kwargs)
            if response.status_code == 200:
                results = response.json()
            else:
                raise RuntimeError(f"Unexpected Response"
                                   f"\nStatus code: {response.status_code} "
                                   f"\nStatus reason: {response.reason}")
        except RuntimeError as e1:
            urllib_logger.error(str(e1))
        except RequestException as e2:
            urllib_logger.error(str(e2))
        return results

    @classmethod
    def get_user_profile(cls) -> Union[List[Dict], Dict]:
        url = f'{cls._request_endpoint}user/profile'
        params = {}
        results = cls.request(method='GET', url=url, params=params)
        return None if results is None else results.get('profile', {}).get('account', None)

    @classmethod
    def get_account_balances(cls) -> Dict:
        url = f'{cls._request_endpoint}accounts/{cls._account_id}/balances'
        params = {}
        results = cls.request(method='GET', url=url, params=params)
        return None if results is None else results.get('balances', None)

    @classmethod
    def get_account_positions(cls) -> Union[List[Dict], None]:
        url = f'{cls._request_endpoint}accounts/{cls._account_id}/positions'
        params = {}
        results = cls.request(method='GET', url=url, params=params)
        if results:
            for key in ['positions', 'position']:
                if isinstance(results, dict):
                    results = results.get(key, {})
                else:
                    results = {}
        return None if not results else dict_to_list_of_dict(results)

    @classmethod
    def get_account_history(cls, **params) -> Union[List[Dict], None]:
        url = f'{cls._request_endpoint}accounts/{cls._account_id}/history'
        if not params:
            params = {}
        # {'page': '3', 'limit': '100',
        #  'type': 'trade, option, ach, wire, dividend, fee, tax, journal, check, transfer, adjustment, interest',
        #  'start': 'yyyy-mm-dd', 'end': 'yyyy-mm-dd', 'symbol': 'SPY', 'exactMatch': 'true'}
        results = cls.request(method='GET', url=url, params=params)
        if results:
            for key in ['history', 'event']:
                if isinstance(results, dict):
                    results = results.get(key, {})
                else:
                    results = {}
        return None if not results else dict_to_list_of_dict(results)

    @classmethod
    def get_account_gain_loss(cls, **kwargs) -> Union[List[Dict], None]:
        url = f'{cls._request_endpoint}accounts/{cls._account_id}/gainloss'
        if kwargs:
            params = kwargs
        else:
            params = {}
        # {'page': '3', 'limit': '100', 'sortBy': 'closeDate', 'sort': 'desc',
        # 'start': 'yyyy-mm-dd', 'end': 'yyyy-mm-dd', 'symbol': 'SPY'}
        results = cls.request(method='GET', url=url, params=params)
        if results:
            for key in ['gainloss', 'closed_position']:
                if isinstance(results, dict):
                    results = results.get(key, {})
                else:
                    results = {}
        return None if not results else dict_to_list_of_dict(results)

    @classmethod
    def get_account_orders(cls, include_tags='true') -> Union[List[Dict], None]:
        url = f'{cls._request_endpoint}accounts/{cls._account_id}/orders'
        params = {'includeTags': include_tags}
        results = cls.request(method='GET', url=url, params=params)
        if results:
            for key in ['orders', 'order']:
                if isinstance(results, dict):
                    results = results.get(key, {})
                else:
                    results = {}
        return None if not results else dict_to_list_of_dict(results)

    @classmethod
    def get_an_account_order(cls, order_id, include_tags='true') -> Union[Dict, None]:
        url = f'{cls._request_endpoint}accounts/{cls._account_id}/orders/{order_id}'
        params = {'includeTags': include_tags}
        results = cls.request(method='GET', url=url, params=params)
        return None if results is None else results.get('order', None)

    @classmethod
    def cancel_order(cls, order_id) -> Union[Dict, None]:
        url = f'{cls._request_endpoint}accounts/{cls._account_id}/orders/{order_id}'
        data = {}
        results = cls.request(method='DELETE', url=url, data=data)
        return None if results is None else results.get('order', None)

    @classmethod
    def get_quotes(cls, symbols: Union[List[str], str], greeks: str = 'false') -> Union[List[Dict], None]:
        url = f'{cls._request_endpoint}markets/quotes'
        if isinstance(symbols, list):
            symbols = ",".join(symbols)
        params = {'symbols': symbols, 'greeks': greeks}
        results = cls.request(method='GET', url=url, params=params)
        if results:
            for key in ['quotes', 'quote']:
                if isinstance(results, dict):
                    results = results.get(key, {})
                else:
                    results = {}
        return None if not results else dict_to_list_of_dict(results)

    @classmethod
    def get_market_clock(cls, delayed: str = 'false') -> Union[Dict, None]:
        url = f'{cls._request_endpoint}markets/clock'
        params = {'delayed': delayed}
        results = cls.request(method='GET', url=url, params=params)
        return None if results is None else results.get('clock', None)

    @classmethod
    def get_market_calendar(cls, month, year) -> Union[List[Dict], None]:
        url = f'{cls._request_endpoint}markets/calendar'
        params = {'month': month, 'year': year}
        results = cls.request(method='GET', url=url, params=params)
        return None if results is None else results.get('calendar', {}).get('days', {}).get('day', None)

    @classmethod
    def get_option_chains(cls, symbol, expiration, greeks='true') -> Union[List[Dict], None]:
        url = f'{cls._request_endpoint}markets/options/chains'
        params = {'symbol': symbol, 'expiration': expiration, 'greeks': greeks}
        results = cls.request(method='GET', url=url, params=params)
        return None if results is None else results.get('options', {}).get('option', None)

    @classmethod
    def post_option_order(cls, underlying_symbol, option_symbol, side, quantity, order_type='market', duration='day',
                          price=None, stop=None, tag=None, preview=True) -> Union[Dict, None]:
        url = f'{cls._request_endpoint}accounts/{cls._account_id}/orders'
        # for equity orders
        # side = ['buy', 'buy_to_cover', 'sell', 'sell_short']
        # for option orders
        # side = ['buy_to_open', 'buy_to_close', 'sell_to_open', 'sell_to_close']
        # type = ['market', 'limit', 'stop', 'stop_limit']
        # duration = ['day', 'gtc', 'pre', 'post']
        # price - limit price - required for limit and stop limit orders
        # stop - stop price - required for stop and stop limit orders
        # tag - optional order tag
        data = {'class': 'option',
                'symbol': underlying_symbol,
                'option_symbol': option_symbol,
                'side': side,
                'quantity': quantity,
                'type': order_type,
                'duration': duration}
        if price:
            data.update({'price': price})
        if stop:
            data.update({'stop': stop})
        if tag:
            data.update({'tag': tag})
        if preview:
            data.update({'preview': 'true'})
        results = cls.request(method='POST', url=url, data=data)
        return None if results is None else results.get('order', None)


class UserProfileResponse:

    def __init__(self, **kwargs):
        self.account_number = kwargs.get('account_number', None)
        self.classification = kwargs.get('classification', None)
        self.date_created = datetime.strptime(kwargs.get('date_created', None), "%Y-%m-%dT%H:%M:%S.%fZ")
        self.day_trader = kwargs.get('day_trader', None)
        self.option_level = kwargs.get('option_level', None)
        self.status = kwargs.get('status', None)
        self.type = kwargs.get('type', None)
        self.last_update_date = datetime.strptime(kwargs.get('last_update_date', None), "%Y-%m-%dT%H:%M:%S.%fZ")


class Position:

    def __init__(self, **kwargs):
        self.cost_basis = kwargs.get('cost_basis', None)
        self.date_acquired = datetime.strptime(kwargs.get('date_acquired', None), "%Y-%m-%dT%H:%M:%S.%fZ")
        self.id = kwargs.get('id', None)
        self.quantity = kwargs.get('quantity', None)
        self.symbol = kwargs.get('symbol', None)

    def unit_cost(self) -> float:
        return self.cost_basis / self.quantity


class Quote:

    def __init__(self, **kwargs):
        self.symbol = kwargs.get('symbol', None)
        self.description = kwargs.get('description', None)
        self.exch = kwargs.get('exch', None)
        self.type = kwargs.get('type', None)
        self.last = kwargs.get('last', None)
        self.change = kwargs.get('change', None)
        self.volume = kwargs.get('volume', None)
        self.open = kwargs.get('open', None)
        self.high = kwargs.get('high', None)
        self.low = kwargs.get('low', None)
        self.close = kwargs.get('close', None)
        self.bid = kwargs.get('bid', None)
        self.ask = kwargs.get('ask', None)
        self.change_percentage = kwargs.get('change_percentage', None)
        self.average_volume = kwargs.get('average_volume', None)
        self.last_volume = kwargs.get('last_volume', None)
        self.trade_date = kwargs.get('trade_date', None)
        self.prevclose = kwargs.get('prevclose', None)
        self.week_52_high = kwargs.get('week_52_high', None)
        self.week_52_low = kwargs.get('week_52_low', None)
        self.bidsize = kwargs.get('bidsize', None)
        self.bidexch = kwargs.get('bidexch', None)
        self.bid_date = kwargs.get('bid_date', None)
        self.asksize = kwargs.get('asksize', None)
        self.askexch = kwargs.get('askexch', None)
        self.ask_date = kwargs.get('ask_date', None)
        self.root_symbols = kwargs.get('root_symbols', None)
        self.underlying = kwargs.get('underlying', None)
        self.strike = kwargs.get('strike', None)
        self.open_interest = kwargs.get('open_interest', None)
        self.contract_size = kwargs.get('contract_size', None)
        self.expiration_date = kwargs.get('expiration_date', None)
        self.expiration_type = kwargs.get('expiration_type', None)
        self.option_type = kwargs.get('option_type', None)
        self.root_symbol = kwargs.get('root_symbol', None)

    def expiration_dt(self) -> Union[None, date]:
        return None if not self.expiration_date else date.fromisoformat(self.expiration_date)


class MarginBalances:

    def __init__(self, **kwargs):
        self.fed_call = kwargs.get('fed_call', None)
        self.maintenance_call = kwargs.get('maintenance_call', None)
        self.option_buying_power = kwargs.get('option_buying_power', None)
        self.stock_buying_power = kwargs.get('stock_buying_power', None)
        self.stock_short_value = kwargs.get('stock_short_value', None)
        self.sweep = kwargs.get('sweep', None)


class CashBalances:

    def __init__(self, **kwargs):
        self.cash_available = kwargs.get('cash_available', None)
        self.sweep = kwargs.get('sweep', None)
        self.unsettled_funds = kwargs.get('unsettled_funds', None)


class PdtBalances:

    def __init__(self, **kwargs):
        self.fed_call = kwargs.get('fed_call', None)
        self.maintenance_call = kwargs.get('maintenance_call', None)
        self.option_buying_power = kwargs.get('option_buying_power', None)
        self.stock_buying_power = kwargs.get('stock_buying_power', None)
        self.stock_short_value = kwargs.get('stock_short_value', None)
        self.sweep = kwargs.get('sweep', None)


class AccountBalances:

    def __init__(self, **kwargs):
        self.option_short_value = kwargs.get('option_short_value', None)
        self.total_equity = kwargs.get('total_equity', None)
        self.account_number = kwargs.get('account_number', None)
        self.account_type = kwargs.get('account_type', None)
        self.close_pl = kwargs.get('close_pl', None)
        self.current_requirement = kwargs.get('current_requirement', None)
        self.equity = kwargs.get('equity', None)
        self.long_market_value = kwargs.get('long_market_value', None)
        self.market_value = kwargs.get('market_value', None)
        self.open_pl = kwargs.get('open_pl', None)
        self.option_long_value = kwargs.get('option_long_value', None)
        self.option_requirement = kwargs.get('option_requirement', None)
        self.pending_orders_count = kwargs.get('pending_orders_count', None)
        self.short_market_value = kwargs.get('short_market_value', None)
        self.stock_long_value = kwargs.get('stock_long_value', None)
        self.total_cash = kwargs.get('total_cash', None)
        self.uncleared_funds = kwargs.get('uncleared_funds', None)
        self.pending_cash = kwargs.get('pending_cash', None)
        self.margin = MarginBalances(**kwargs.get('margin', {}))
        self.cash = CashBalances(**kwargs.get('cash', {}))
        self.pdt = PdtBalances(**kwargs.get('pdt', {}))


class MarketState:

    def __init__(self, name: str, tradeable: bool, start_dts: datetime, end_dts: datetime):
        self.name = name
        self.tradeable = tradeable
        self.start_dts = start_dts
        self.end_dts = end_dts
        self.id = f'{self.name}_{self.start_dts.timestamp()}'

    def __lt__(self, other):
        return None if not isinstance(other, MarketState) else self.start_dts < other.start_dts

    def __le__(self, other):
        return None if not isinstance(other, MarketState) else self.start_dts <= other.start_dts

    def __gt__(self, other):
        return None if not isinstance(other, MarketState) else self.start_dts > other.start_dts

    def __ge__(self, other):
        return None if not isinstance(other, MarketState) else self.start_dts >= other.start_dts


class MarketCalendarDay:

    def __init__(self, **kwargs):
        self._date = date.fromisoformat(kwargs.get('date'))
        self.status = kwargs.get('status')
        self.description = kwargs.get('description')
        self.start_of_day = datetime.combine(date=self._date, time=time(hour=0, minute=0, second=0))
        self.end_of_day = self.start_of_day + timedelta(days=1)
        premarket_start = kwargs.get('premarket', {}).get('start', None)
        # premarket_end = kwargs.get('premarket', {}).get('end', None)
        open_start = kwargs.get('open', {}).get('start', None)
        open_end = kwargs.get('open', {}).get('end', None)
        # postmarket_start = kwargs.get('postmarket', {}).get('start', None)
        postmarket_end = kwargs.get('postmarket', {}).get('end', None)
        self.premarket_open = datetime.combine(date=self.date, time=time.fromisoformat(premarket_start)) if premarket_start else None
        self.market_open = datetime.combine(date=self.date, time=time.fromisoformat(open_start)) if open_start else None
        self.market_close = datetime.combine(date=self.date, time=time.fromisoformat(open_end)) if open_end else None
        self.postmarket_close = datetime.combine(date=self.date, time=time.fromisoformat(postmarket_end)) if postmarket_end else None
        self.market_states = []
        if kwargs.get('status') == 'open':
            self.market_states.append(MarketState(name='prepremarket', tradeable=False, start_dts=self.start_of_day, end_dts=self.premarket_open))
            self.market_states.append(MarketState(name='premarket', tradeable=False, start_dts=self.premarket_open,
                                                  end_dts=self.market_open))
            self.market_states.append(MarketState(name='open', tradeable=True, start_dts=self.market_open,
                                                  end_dts=self.market_close))
            self.market_states.append(MarketState(name='postmarket', tradeable=False, start_dts=self.market_close,
                                                  end_dts=self.postmarket_close))
            self.market_states.append(MarketState(name='postpostmarket', tradeable=False, start_dts=self.postmarket_close,
                                                  end_dts=self.end_of_day))
        else:
            self.market_states.append(MarketState(name='Closed all day', tradeable=False, start_dts=self.start_of_day, end_dts=self.end_of_day))

    @property
    def date(self) -> date:
        return self._date

    def is_market_day(self) -> bool:
        return self.status == 'open'

    def late_open(self) -> bool:
        return None if not self.is_market_day() else self.market_open.time() > time(hour=9, minute=30)

    def early_close(self) -> bool:
        return None if not self.is_market_day() is None else self.market_close.time() < time(hour=16, minute=0)

    def get_market_state_at_time(self, eval_ts: time):
        return [x for x in self.market_states if x.start_dts.time() <= eval_ts < x.end_dts.time()][0]

    def __repr__(self):
        return f'MarketCalendarDay(date={self.date.isoformat()}, status={self.status})'

    def __lt__(self, other):
        return None if not isinstance(other, MarketCalendarDay) else self.date < other.date

    def __le__(self, other):
        return None if not isinstance(other, MarketCalendarDay) else self.date <= other.date

    def __gt__(self, other):
        return None if not isinstance(other, MarketCalendarDay) else self.date > other.date

    def __ge__(self, other):
        return None if not isinstance(other, MarketCalendarDay) else self.date >= other.date


class TradierApi(TradierApiBase):

    @classmethod
    def get_account_positions(cls) -> Union[List[Position], None]:
        data = super().get_account_positions()
        return None if data is None else [Position(**d) for d in data]

    @classmethod
    def get_quotes(cls, symbols: Union[List[str], List[Position], str], greeks: str = 'false') -> Union[List[Quote], None]:
        if isinstance(symbols, list):
            symbols = [s.symbol if isinstance(s, Position) else s for s in symbols]
        data = super().get_quotes(symbols=symbols, greeks=greeks)
        return None if data is None else [Quote(**d) for d in data]

    @classmethod
    def get_market_calendar(cls, month, year) -> Union[List[MarketCalendarDay], None]:
        data = super().get_market_calendar(month=month, year=year)
        return None if data is None else [MarketCalendarDay(**d) for d in data]

    @classmethod
    def get_market_calendar_range(cls, base_date: Union[date, datetime], mo_hist: int = 3, mo_fut: int = 3) -> List[MarketCalendarDay]:
        if isinstance(base_date, datetime):
            base_date = base_date.date()
        data = []
        for x in range(-mo_hist, mo_fut + 1, 1):
            loop_date = base_date + relativedelta(months=x)
            data += cls.get_market_calendar(month=loop_date.month, year=loop_date.year)
        return data


class MarketCalendar:

    def __init__(self, base_date: Union[date, None] = None, mo_hist: int = 3, mo_fut: int = 3):
        if base_date is None:
            base_date = date.today()
        self._days = TradierApi.get_market_calendar_range(base_date=base_date, mo_hist=mo_hist, mo_fut=mo_fut)
        self._days.sort()

    @property
    def days(self) -> List[MarketCalendarDay]:
        return self._days

    @property
    def days_dict(self) -> Dict[date, MarketCalendarDay]:
        return {d.date: d for d in self.days}

    def get_day(self, day: Union[date, datetime, MarketCalendarDay]) -> MarketCalendarDay:
        if isinstance(day, datetime) or isinstance(day, MarketCalendarDay):
            day = day.date
        return self.days_dict.get(day, None)

    def get_future_market_states(self, eval_dts: datetime) -> List[MarketState]:
        market_states = []
        for d in self.days:
            if d.date >= eval_dts.date():
                for ms in d.market_states:
                    if ms.start_dts >= eval_dts:
                        market_states.append(ms)
        market_states.sort()
        return market_states

    def get_tradeable_future_market_states(self, eval_dts: datetime) -> List[MarketState]:
        return [ms for ms in self.get_future_market_states(eval_dts=eval_dts) if ms.tradeable]

    def get_non_tradeable_future_market_states(self, eval_dts: datetime) -> List[MarketState]:
        return [ms for ms in self.get_future_market_states(eval_dts=eval_dts) if not ms.tradeable]

    def get_market_state(self, eval_dts: datetime, n_future: int = 0) -> MarketState:
        return self.get_future_market_states(eval_dts=eval_dts)[n_future]

    def get_tradeable_market_state(self, eval_dts: datetime, n_future: int = 0) -> MarketState:
        return self.get_tradeable_future_market_states(eval_dts=eval_dts)[n_future]

    def get_non_tradeable_market_state(self, eval_dts: datetime, n_future: int = 0) -> MarketState:
        return self.get_non_tradeable_future_market_states(eval_dts=eval_dts)[n_future]

    def get_next_open_day(self, start_day: Union[date, datetime, MarketCalendarDay]) -> MarketCalendarDay:
        if isinstance(start_day, datetime):
            start_day = start_day.date()
        elif isinstance(start_day, MarketCalendarDay):
            start_day = start_day.date
        day_list = [d for d in self.days if d.date > start_day and d.is_market_day()]
        day_list.sort()
        return day_list[0]



