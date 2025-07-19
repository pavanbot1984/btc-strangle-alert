import requests
import time

BOT_TOKEN = '8046031500:AAGpTEu6uf6-I5fqOQ2h3SqBShZzs1bkSe8'
CHAT_ID = '6614671189'

LOWER_BREAK = 117079.11
UPPER_BREAK = 119520.88
EXPIRY_TIMESTAMP = 1753141800  # 21 July 2025 15:30 IST (10:00 UTC)

def get_btc_price():
    url = "https://api.india.delta.exchange/v2/tickers/BTCUSD"
    try:
        res = requests.get(url)
        data = res.json()
        return float(data['result']['spot_price'])  # or use mark_price
    except Exception as e:
        print("Price fetch error:", e)
        print("Response body:", res.text)
        return None

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram error:", e)

def is_expired():
    return time.time() > EXPIRY_TIMESTAMP

last_alert = None
last_status_time = time.time()

while not is_expired():
    price = get_btc_price()
    now = time.time()

    if price:
        if price > UPPER_BREAK and last_alert != "upper":
            send_telegram_alert(f"🔺 BTC crossed upper breakeven: {price} > {UPPER_BREAK}\n👉 Hedge CALL leg or roll up.")
            last_alert = "upper"
        elif price < LOWER_BREAK and last_alert != "lower":
            send_telegram_alert(f"🔻 BTC dropped below lower breakeven: {price} < {LOWER_BREAK}\n👉 Hedge PUT leg or roll down.")
            last_alert = "lower"
        elif LOWER_BREAK <= price <= UPPER_BREAK and last_alert != "safe":
            send_telegram_alert(f"✅ BTC is within safe zone: {price}\nNo adjustment needed.")
            last_alert = "safe"

        if now - last_status_time >= 3600:
            send_telegram_alert(f"🕒 Hourly Status: BTC = {price}\nRange: {LOWER_BREAK} – {UPPER_BREAK}\nCurrent status: {last_alert}")
            last_status_time = now

    time.sleep(300)

send_telegram_alert("⏰ Strategy expired — BTC strangle monitor stopped.")