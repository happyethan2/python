# Testing pushover app using their python library

from pushover import init, Client

pushover_app_token = "X"
pushover_user_key = "X"

buying_decision = "buy"
adelaide_buying_tip = "prices are decreasing but they are likely to decrease further"

def send_push_notification(message):
    init(pushover_app_token)
    client = Client(pushover_user_key)
    client.send_message(message, title="Fuel Price Alert")

if buying_decision == "buy":
    send_push_notification(f"Fuel Price Alert: {adelaide_buying_tip}")
