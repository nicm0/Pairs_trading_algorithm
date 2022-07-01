from jesse.research import backtest, get_candles


def run_pairs_trading_backtest(exchange, symbol_A, symbol_B, timeframe, start_date, end_date, strategy):
    print(f'Backtest({strategy}) {exchange} {symbol_A} {symbol_B} {timeframe} {start_date} -> {end_date}')

    config = {
        'starting_balance': 100_000,
        'fee': 0.0004,
        'type': 'futures',
        'futures_leverage': 1,
        'futures_leverage_mode': 'cross',
        'exchange': exchange,
        'warm_up_candles': 0
    }

    routes = [
        {'exchange': exchange, 'strategy': strategy, 'symbol': symbol_A, 'timeframe': timeframe},
        {'exchange': exchange, 'strategy': strategy, 'symbol': symbol_B, 'timeframe': timeframe}
    ]

    extra_routes = []
    #     {'exchange': exchange, 'symbol': symbol_A, 'timeframe': '1m'},
    #     {'exchange': exchange, 'symbol': symbol_A, 'timeframe': '1h'},
    #     {'exchange': exchange, 'symbol': symbol_B, 'timeframe': '1m'},
    #     {'exchange': exchange, 'symbol': symbol_B, 'timeframe': '1h'}

    candles = {
        (f'{exchange}-{symbol_A}'): {
            'exchange': exchange,
            'symbol': symbol_A,
            'candles': get_candles(exchange, symbol_A, '1m', start_date, end_date)
        },
        (f'{exchange}-{symbol_B}'): {
            'exchange': exchange,
            'symbol': symbol_B,
            'candles': get_candles(exchange, symbol_B, '1m', start_date, end_date)
        }
    }

    result = backtest(config, routes, extra_routes, candles)

    log_file = f'{strategy}-{exchange}-{symbol_A}-{timeframe}-{start_date}-{end_date}.txt'

    with open(log_file, 'w') as out:
        out.write(str(result['metrics']))
        out.write('\n\n')
        for log in result['logs']:
            for key, value in log.items():
                out.write(f'{key}: {value}\n')


run_pairs_trading_backtest(exchange='Binance Perpetual Futures', symbol_A='BTC-USDT', symbol_B='ETH-USDT', timeframe='5m', start_date='2022-01-01', end_date='2022-01-31', strategy='PairsTradingStrategy')