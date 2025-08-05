from dataclasses import dataclass
from .depth import Depth
from .exchange_info import ExchangeInfo
from .balances import Balances

@dataclass
class MarketData(Depth, ExchangeInfo, Balances):
  ...