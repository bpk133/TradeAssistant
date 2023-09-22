import requests
from requests.exceptions import RequestException
from typing import Union, List
from creds import tradier_api_creds
import logging

# prevent urllib from logging every single request
urllib_logger = logging.getLogger('urllib3.connectionpool')
urllib_logger.setLevel(logging.ERROR)


class ApiResponse:

    def __init__(self,
                 request_success: bool,
                 request_exception: Union[RequestException, None] = None,
                 response_valid: Union[bool, None] = None,
                 response: Union[requests.Response, None] = None):
        self.request_success = request_success
        self.request_exception = request_exception
        self.response_valid = response_valid
        self.response = response
        self.data = None
        self.flatten_keys = []
        if self.request_success and self.response_valid:
            self.data = self.response.json()

    @property
    def data_returned(self):
        return self.data is not None

    @property
    def data_status(self):
        if self.data_returned:
            if self.flatten_keys:
                if self.flattened_data():
                    output = 'ok'
                else:
                    output = 'empty'
            else:
                output = 'ok'
        else:
            output = None
        return output

    def set_flatten_keys(self, *args):
        self.flatten_keys = [arg for arg in args]

    def flattened_data(self):
        output = self.data
        if self.data and self.flatten_keys:
            for key in self.flatten_keys:
                if isinstance(output, dict):
                    output = output.get(key, {})
                else:
                    output = {}
        return output


class TradierApi:
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
    def request(cls, request_type, url, params, data):
        try:
            if request_type == 'delete':
                response = requests.delete(url, data=data, headers=cls._request_headers)
            elif request_type == 'post':
                response = requests.post(url, data=data, headers=cls._request_headers)
            else:
                # request_type == 'get':
                response = requests.get(url, params=params, headers=cls._request_headers)
            if response.status_code == 200:
                output = ApiResponse(request_success=True, response_valid=True, response=response)
            else:
                output = ApiResponse(request_success=True, response_valid=False, response=response)
        except RequestException as e:
            output = ApiResponse(request_success=True, request_exception=e)
        return output

    @classmethod
    def get_request(cls, url, params) -> ApiResponse:
        return cls.request(request_type='get', url=url, params=params, data=None)

    @classmethod
    def delete_request(cls, url, data) -> ApiResponse:
        return cls.request(request_type='delete', url=url, params=None, data=data)

    @classmethod
    def post_request(cls, url, data) -> ApiResponse:
        return cls.request(request_type='post', url=url, params=None, data=data)

    @classmethod
    def get_user_profile(cls) -> ApiResponse:
        url = f'{cls._request_endpoint}user/profile'
        params = {}
        return cls.get_request(url=url, params=params)

    @classmethod
    def get_account_balances(cls) -> ApiResponse:
        url = f'{cls._request_endpoint}accounts/{cls._account_id}/balances'
        params = {}
        request_response = cls.get_request(url=url, params=params)
        request_response.set_flatten_keys('balances')
        return request_response

    @classmethod
    def get_account_positions(cls) -> ApiResponse:
        url = f'{cls._request_endpoint}accounts/{cls._account_id}/positions'
        params = {}
        request_response = cls.get_request(url=url, params=params)
        request_response.set_flatten_keys('positions', 'position')
        return request_response

    @classmethod
    def get_account_history(cls, **params) -> ApiResponse:
        url = f'{cls._request_endpoint}accounts/{cls._account_id}/history'
        if not params:
            params = {}
        # {'page': '3', 'limit': '100',
        #  'type': 'trade, option, ach, wire, dividend, fee, tax, journal, check, transfer, adjustment, interest',
        #  'start': 'yyyy-mm-dd', 'end': 'yyyy-mm-dd', 'symbol': 'SPY', 'exactMatch': 'true'}
        request_response = cls.get_request(url=url, params=params)
        request_response.set_flatten_keys('history', 'event')
        return request_response

    @classmethod
    def get_account_gain_loss(cls, **kwargs) -> ApiResponse:
        url = f'{cls._request_endpoint}accounts/{cls._account_id}/gainloss'
        if kwargs:
            params = kwargs
        else:
            params = {}
        # {'page': '3', 'limit': '100', 'sortBy': 'closeDate', 'sort': 'desc',
        # 'start': 'yyyy-mm-dd', 'end': 'yyyy-mm-dd', 'symbol': 'SPY'}
        request_response = cls.get_request(url=url, params=params)
        request_response.set_flatten_keys('gainloss', 'closed_position')
        return request_response

    @classmethod
    def get_account_orders(cls, include_tags='true') -> ApiResponse:
        url = f'{cls._request_endpoint}accounts/{cls._account_id}/orders'
        params = {'includeTags': include_tags}
        request_response = cls.get_request(url=url, params=params)
        request_response.set_flatten_keys('orders', 'order')
        return request_response

    @classmethod
    def get_an_account_order(cls, order_id, include_tags='true') -> ApiResponse:
        url = f'{cls._request_endpoint}accounts/{cls._account_id}/orders/{order_id}'
        params = {'includeTags': include_tags}
        request_response = cls.get_request(url=url, params=params)
        request_response.set_flatten_keys('order')
        return request_response

    @classmethod
    def cancel_order(cls, order_id):
        url = f'{cls._request_endpoint}accounts/{cls._account_id}/orders/{order_id}'
        data = {}
        request_response = cls.delete_request(url=url, data=data)
        request_response.set_flatten_keys('order')
        return request_response

    @classmethod
    def get_quotes(cls, symbol: Union[List[str], str], greeks: str = 'false') -> ApiResponse:
        url = f'{cls._request_endpoint}markets/quotes'
        if isinstance(symbol, list):
            symbol = ",".join(symbol)
        params = {'symbols': symbol, 'greeks': greeks}
        request_response = cls.get_request(url=url, params=params)
        request_response.set_flatten_keys('quotes', 'quote')
        return request_response

    @classmethod
    def get_market_clock(cls, delayed: str = 'false') -> ApiResponse:
        url = f'{cls._request_endpoint}markets/clock'
        params = {'delayed': delayed}
        request_response = cls.get_request(url=url, params=params)
        request_response.set_flatten_keys('clock')
        return request_response

    @classmethod
    def get_market_calendar(cls, month, year) -> ApiResponse:
        url = f'{cls._request_endpoint}markets/calendar'
        params = {'month': month, 'year': year}
        request_response = cls.get_request(url=url, params=params)
        request_response.set_flatten_keys('calendar', 'days', 'day')
        return request_response

    @classmethod
    def symbol_lookup(cls, symbol) -> ApiResponse:
        url = f'{cls._request_endpoint}markets/lookup'
        # exchanges = 'Q,N'
        # types = "'stock', 'option', 'etf', 'index'"
        # params = {'q': symbol, 'exchanges': exchanges, 'types': types}
        # params = {'q': symbol, 'types': 'option'}
        params = {'q': symbol}
        return cls.get_request(url=url, params=params)

    @classmethod
    def get_option_chains(cls, symbol, expiration, greeks='true') -> ApiResponse:
        url = f'{cls._request_endpoint}markets/options/chains'
        params = {'symbol': symbol, 'expiration': expiration, 'greeks': greeks}
        request_response = cls.get_request(url=url, params=params)
        request_response.set_flatten_keys('options', 'option')
        return request_response

    @classmethod
    def get_option_symbols(cls, underlying):
        url = f'{cls._request_endpoint}markets/options/lookup'
        params = {'underlying': underlying}
        return cls.get_request(url=url, params=params)

    @classmethod
    def post_option_order(cls, underlying_symbol, option_symbol, side, quantity, order_type='market', duration='day', price=None, stop=None, tag=None, preview=True):
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
        request_response = cls.post_request(url=url, data=data)
        request_response.set_flatten_keys('order')
        return request_response


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
        self.cash_available = kwargs.get('cash_available', None)
        self.sweep = kwargs.get('sweep', None)
        self.unsettled_funds = kwargs.get('unsettled_funds', None)

