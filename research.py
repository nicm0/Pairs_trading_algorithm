from pickle import TRUE

import numpy as np

import jesse.indicators as ta

import matplotlib.pyplot as plt

from jesse import research

from datetime import datetime, timezone

import talib


def plot(exchange, instrument_A, instrument_B, timeperiod, start_date, end_date):
    filename = instrument_A + '_' + instrument_B + '_' + timeperiod + '_' + start_date + '-' + end_date + '_' + exchange

    print(filename)

    fig = plt.figure(figsize=(200, 65))

    gs = fig.add_gridspec(3, hspace=0)

    axs = gs.subplots(sharex=True, sharey=False)

    fig.suptitle(instrument_A)

    candles_A = research.get_candles(exchange, instrument_A, timeperiod, start_date, end_date)
    candles_B = research.get_candles(exchange, instrument_B, timeperiod, start_date, end_date)

    times = []

    for candle in candles_A:
        times.append(datetime.fromtimestamp((candle[0] / 1000.0), tz=timezone.utc))
    
    closes_spread = np.divide(candles_A[:, 2], candles_B[:, 2])
    spread_sma = ta.sma(closes_spread, period=4, sequential=True)
    mean_stddev_indicator = talib.STDDEV(spread_sma, timeperiod=12, nbdev=1)



    spread_sma_top = np.multiply(spread_sma, 1.05)
    spread_sma_bottom = np.multiply(spread_sma, 0.95)


    sma_A = ta.sma(candles_A[:, 2], period=4, sequential=True)
    sma_B = ta.sma(candles_B[:, 2], period=4, sequential=True)

    axs[0].plot(times, candles_A[:, 2], color='black', label='CLOSES')
    axs[0].plot(times, sma_A, color='blue', label='CLOSES')

    axs[1].plot(times, candles_B[:, 2], color='black', label='CLOSES')
    axs[1].plot(times, sma_B, color='blue', label='CLOSES')
    
    axs[2].plot(times, closes_spread, color='black', label='SPREAD')

    axs[2].plot(times, spread_sma, color='dimgray', label='SPREAD')
    axs[2].plot(times, np.subtract(spread_sma, mean_stddev_indicator), color='red', label='SPREAD')
    axs[2].plot(times, np.add(spread_sma, mean_stddev_indicator), color='red', label='SPREAD')


    for ax in axs:
        ax.label_outer()

    fig.legend()

    fig.savefig('plots/' + filename + '.png')

plot('Binance Perpetual Futures', 'BTC-USDT', 'ETH-USDT', '5m', '2022-01-01', '2022-01-03')
plot('Binance Perpetual Futures', 'ETH-USDT', 'BTC-USDT', '5m', '2022-01-01', '2022-01-03')

# Entry conditions: real spread exits channel and enter upon re-entry of channel (mean std.dev channel)
#   when spread crosses from above channel into channel -> short A long B
#   when spread crosses from below channel into channel -> short B long A
# Exit conditions: real spread (after re-entry of channel) exits channel (on other side of where it re-entered)


