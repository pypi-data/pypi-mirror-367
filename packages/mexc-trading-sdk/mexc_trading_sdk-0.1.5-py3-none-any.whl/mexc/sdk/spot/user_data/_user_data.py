from dataclasses import dataclass
from trading_sdk.spot.user_data import QueryOrders
from .my_trades import MyTrades
from .open_orders import OpenOrders
from .query_order import QueryOrder

@dataclass
class UserData(MyTrades, OpenOrders, QueryOrder, QueryOrders):
  ...