# Program to test API calls to the fuel pricing data scheme API here in australia

import requests
import json
from statistics import mean

def get_min_avg_fuel_price_by_id(fuel_id):
    url = "https://fppdirectapi-prod.safuelpricinginformation.com.au/Price/GetSitesPrices?countryId=21&geoRegionLevel=2&geoRegionId=189"
    headers = {
        "Authorization": "FPDAPI SubscriberToken=X",
        "Content-type": "application/json"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = json.loads(response.text)
        prices = [site["Price"] for site in data["SitePrices"] if site["FuelId"] == fuel_id]
        if not prices:
            print(f"No prices found for Fuel ID {fuel_id}")
            return None, None
        min_price = min(prices)
        avg_price = round(mean(prices), 2)
        return min_price, avg_price
    else:
        print(f"Error: Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        return None, None

fuel_id = 2  # Unleaded fuel
min_fuel_price, average_fuel_price = get_min_avg_fuel_price_by_id(fuel_id)
if min_fuel_price is not None and average_fuel_price is not None:
    print(f"Minimum Fuel Price for Fuel ID {fuel_id}: " + str(min_fuel_price))
    print(f"Average Fuel Price for Fuel ID {fuel_id}: " + str(average_fuel_price))
else:
    print("Failed to fetch fuel prices.")
