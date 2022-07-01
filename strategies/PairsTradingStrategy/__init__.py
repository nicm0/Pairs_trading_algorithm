from jesse.strategies import Strategy, cached
import jesse.indicators as ta
from jesse import utils
from analysis.config import pairs_trading_groups
import talib
import numpy as np

class PairsTradingStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.vars['is_cointegrated'] = True
        self.vars['minimum_candles'] = 12

    def hyperparameters(self):
        return [
            {'name': 'stddev_period', 'type': int, 'min': 1, 'max': 38, 'default': 12},
            {'name': 'spread_sma_period', 'type': int, 'min': 1, 'max': 38, 'default': 4},
        ]

    # def before(self, spread, thresholds) -> None:
    #     self.vars['is_cointegrated'] = utils.are_cointegrated(utils.prices_to_returns(self.candles), utils.prices_to_returns(self.get_candles(self.exchange, 'ETH-USDT', self.timeframe)), cutoff=0.05)
# Instrument A
    def should_long(self) -> bool:
        if self.vars['is_cointegrated'] and len(self.candles) >= self.vars['minimum_candles']: 
            channel_bottom = self.spread_sma_indicator[-1] - self.stddev_indicator[-1]
            channel_bottom_prev = self.spread_sma_indicator[-2] - self.stddev_indicator[-2]
            current_spread = self.spread_indicator[-1]
            prev_spread = self.spread_indicator[-2]
            return current_spread > channel_bottom and prev_spread <= channel_bottom_prev
        return False
        
    def should_short(self) -> bool:
        if self.vars['is_cointegrated'] and len(self.candles) >= self.vars['minimum_candles']: 
            channel_top = self.spread_sma_indicator[-1] + self.stddev_indicator[-1]
            channel_top_prev = self.spread_sma_indicator[-2] + self.stddev_indicator[-2]
            current_spread = self.spread_indicator[-1]
            prev_spread = self.spread_indicator[-2]
            return current_spread < channel_top and prev_spread >= channel_top_prev
        return False

    def should_cancel_entry(self) -> bool:
        return False

    def go_long(self):
        self.volume = utils.size_to_qty(0.01 * self.balance, self.price, precision=3, fee_rate=self.fee_rate)
        self.buy = (self.volume, self.price)

    def go_short(self):
        self.volume = utils.size_to_qty(0.01 * self.balance, self.price, precision=3, fee_rate=self.fee_rate)
        self.sell = (self.volume, self.price)
    
    def update_position(self):
        channel_top = self.spread_sma_indicator[-1] + self.stddev_indicator[-1]
        channel_top_prev = self.spread_sma_indicator[-2] + self.stddev_indicator[-2]
        channel_bottom = self.spread_sma_indicator[-1] - self.stddev_indicator[-1]
        channel_bottom_prev = self.spread_sma_indicator[-2] - self.stddev_indicator[-2]
        current_spread = self.spread_indicator[-1]
        prev_spread = self.spread_indicator[-2]
        current_mean = self.spread_sma_indicator[-1]
        prev_mean = self.spread_sma_indicator[-2]

        if self.is_long:
            if current_spread >= current_mean and prev_spread < prev_mean:
                self.liquidate()
            
        elif self.is_short:
            if current_spread <= current_mean and prev_spread > prev_mean:
                self.liquidate()

    @property
    def stddev_indicator(self):
        return talib.STDDEV(self.spread_sma_indicator, timeperiod=self.hp['stddev_period'], nbdev=1)
    
    @property
    def spread_sma_indicator(self):
        return ta.sma(self.spread_indicator, period=self.hp['spread_sma_period'], sequential=True)

    @property
    def spread_indicator(self):
        return np.divide(self.candles[:, 2], self.get_candles(self.exchange, pairs_trading_groups[self.symbol][-1], self.timeframe)[:, 2])
