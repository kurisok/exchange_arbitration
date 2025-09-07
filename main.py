from binance import ThreadedWebsocketManager
from pybit.unified_trading import WebSocket
from datetime import datetime



binance_bids = 0 # покупку
binance_asks = 0 # продажу
bybit_bids = 0 # покупку
bybit_asks = 0 # продажу
difference = 0.2

num_whl = 0 # номер цыкла загрузки
num_sum_minus = 25 # какова длина загрузки
num_sum_anim = 0 # для анимации



# подсчет разницы в цене в %
def percent_valut(price1, price2):#1 - купил, 2 продал
    return (price2-price1)/price1*100


# обработка сообщений о торгах от Binance
# также основная логика так как сообщения от Binance приходят режем чем от ByBit
def handle_orderbook_binance(msg):
    global binance_bids, binance_asks, num_whl, num_sum_anim, num_sum_minus
    binance_bids = float(msg['b'][0][0])  # список ордеров на покупку
    binance_asks = float(msg['a'][0][0])  # список ордеров на продажу

    # проверка разницы цены на биржах
    if percent_valut(binance_bids, bybit_asks) >= difference or percent_valut(bybit_bids, binance_asks) >= difference:
        print(f"\r{'*' * 50}")
        print(f"\rI have {num_whl*25+num_sum_anim} steps, now is {datetime.now()}")
        print(f"\rBinance-ByBit: {percent_valut(binance_bids, bybit_asks)}%")
        print(f"\rByBit-Binance: {percent_valut(bybit_bids, binance_asks)}%")
        print(f"\rBinance Bid: {binance_bids}$")
        print(f"\rBinance Ask: {binance_asks}$")
        print(f"\rByBit Bid: {bybit_bids}$")
        print(f"\rByBit Ask: {bybit_asks}$")
        print(f"Now is {datetime.now()}")
        num_sum_anim, num_whl = 0, 0
        num_sum_minus = 25

    # анимация показывающая что код работает
    print(f"\r{num_whl}{'*' * num_sum_anim}{'-' * num_sum_minus}", flush=True, end="")
    num_sum_anim += 1
    num_sum_minus -= 1
    if num_sum_minus == -1:
        num_sum_anim = 0
        num_sum_minus = 25
        num_whl += 1

# обработка сообщений о торгах от ByBit
def handle_orderbook_bybit(msg):
    global bybit_bids, bybit_asks
    data = msg.get('data')
    if data:
        bids = data.get('b', [])
        asks = data.get('a', [])
        if bids and asks:
            bybit_bids = float(bids[0][0])  # список ордеров на покупку
            bybit_asks = float(asks[0][0])  # список ордеров на продажу




# создаём WebSocket менеджер для Binance
twm = ThreadedWebsocketManager()


# создаём WebSocket клиент для спотового рынка (spot) ByBit
ws = WebSocket(testnet=False,channel_type="spot")



if __name__ == "__main__":

    print("\r(желательно не меньше 0.2 что бы коммисия бирж не сожрала доход)")
    try:
        difference = float(input("\rВведите какую минимальную разница в цене искать: "))
    except ValueError:
        print("\rНужно вводить число дроби! Например: 0.25")
        input("...")
        exit(print('Выход из системы'))

    twm.start() # запуск менеджера для Binance
    twm.start_depth_socket(callback=handle_orderbook_binance, symbol='BTCUSDT') # указываем что мы хотим получать BTC/USDT

    ws.orderbook_stream(depth=50, symbol="BTCUSDT", callback=handle_orderbook_bybit) # запуск менеджера для ByBit а также указываем что будем слушать

    # чистая формальность что бы код продолжал работать
    try:
        while True:
            pass
    except KeyboardInterrupt:
        twm.stop()
        exit()