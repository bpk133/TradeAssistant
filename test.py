import primary_functions
from tradier_api import TradierApiBase, TradierApi
from datetime import datetime


# response for trying to sell to close options I don't have
# {'errors':
#      {'error': 'Sell order cannot be placed unless you are closing a long position, please check open orders. '}}

# params = {'class': 'option', 'symbol': 'MSFT', 'option_symbol': 'MSFT230922P00325000', 'side': 'sell_to_close', 'quantity': 1.0, 'type': 'market', 'duration': 'day'}
# positions = primary_functions.get_position_list()
# print(positions)
# response = TradierApi.get_account_positions()
# print(response.request_success)
# print(response.response_valid)
# print(response.data_returned)
# print(response.data_status)
# print(response.data)
# print(response.flattened_data())

print(TradierApiBase.get_account_positions())


