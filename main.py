import os

import requests
import json
from pathlib import Path

"""
How to use it:
1. Get test app token from https://developers.amadeus.com/
2. My assumption is 2nd & 3rd flights' location and date are fixed, we search for potential 1st and 4th flight location and dates
3. After searching price, result will be stored in ./test or ./prod
4. Use view.py to view result
5. If you want to get real price, you need to activate prod token. 
   (need credit card & sign contract, but there is free quota)
"""

is_test = True
folder = "./test" if is_test else "./prod"

# Get access token from https://developers.amadeus.com/
# For production usage, you need to use credit card & sign contract to get token
# But there is free quota.
token = "XXX"

# Use test for testing script correctness, use prod for correct price
endpoint = (
    "https://test.api.amadeus.com/v2/shopping/flight-offers"
    if is_test
    else "https://api.amadeus.com/v2/shopping/flight-offers"
)

# Update the locations & dates you are interested 
FIRST_AND_LAST_FLIGHT_LOCATIONS = [
    "KIX",  # 日本大阪關西國際
    "NGO",  # 日本名古屋中部國際機場
    "OKA",  # 日本沖繩縣那霸機場
    "CTS",  # 日本北海道新千歲機場
    "SDJ",  # 日本仙台國際機場
    "HKD",  # 日本北海道函館機場
    "CNX",  # 泰國清邁國際機場
    "BKK",  # 泰國曼谷素萬那普機場
    "HAN",  # 越南河內內排國際機場
    "DAD",  # 越南峴港國際機場
    "SGN",  # 越南胡志明市國際機場
    "PEN",  # 馬來西亞檳城國際機場
    "HKG",  # 香港國際機場
]
FISRT_FLIGHT_DATES = ["2026-04-07", "2026-04-08"]
LAST_FLIGH_DATES = ["2026-09-23", "2026-09-24", "2026-10-22", "2026-10-23"]
SECOND_FLIGHT = {
    "id": "2",
    "originLocationCode": "TPE",
    "destinationLocationCode": "FCO",
    "departureDateTimeRange": {"date": "2026-07-18"},
}
THIRD_FLIGHT = {
    "id": "3",
    "originLocationCode": "MXP",
    "destinationLocationCode": "TPE",
    "departureDateTimeRange": {"date": "2026-07-31"},
},


# SGN: 胡志明市國際機場
# TPE: 台北桃園國際機場
# YVR: 溫哥華國際機場
# HAN: 河內國際機場

# CI: 中華航空
# BR: 長榮航空
# JX: 星宇航空


def search(first_location, first_date, last_location, last_date):
    try:
        payload = {
            "currencyCode": "TWD",
            "originDestinations": [
                # 4 flights
                {
                    "id": "1",
                    "originLocationCode": first_location,
                    "destinationLocationCode": "TPE",
                    "departureDateTimeRange": {"date": first_date},
                },

                # assume 2nd & 3rd flights are fixed
                SECOND_FLIGHT,
                THIRD_FLIGHT,

                {
                    "id": "4",
                    "originLocationCode": "TPE",
                    "destinationLocationCode": last_location,
                    "departureDateTimeRange": {"date": last_date},
                },
            ],
            "travelers": [
                {"id": "1", "travelerType": "ADULT"},
                {"id": "2", "travelerType": "ADULT"},
            ],
            "sources": ["GDS"],
            "searchCriteria": {
                "maxFlightOffers": 250,
                "flightFilters": {
                    "cabinRestrictions": [
                        {
                            "cabin": "ECONOMY",
                            "coverage": "MOST_SEGMENTS",
                            "originDestinationIds": ["1", "2", "3", "4"],
                        }
                    ],
                    "connectionRestriction": {"maxNumberOfConnections": 0},
                    "carrierRestrictions": {"includedCarrierCodes": ["BR", "CI", "JX"]},
                },
            },
        }

        res = requests.post(
            endpoint, headers={"Authorization": f"Bearer {token}"}, json=payload
        )
        res.raise_for_status()
        data = res.json()
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    for start_loc in FIRST_AND_LAST_FLIGHT_LOCATIONS:
        for start_date in FISRT_FLIGHT_DATES:
            for end_loc in FIRST_AND_LAST_FLIGHT_LOCATIONS:
                for end_date in LAST_FLIGH_DATES:
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    file_prefix = f"{folder}/{start_loc}_{start_date}_{end_loc}_{end_date}"
                    if Path(f"{file_prefix}_raw.json").exists():
                        print(f"Skip {start_loc}_{start_date}_{end_loc}_{end_date} because cached")
                        continue
                    data = search(start_loc, start_date, end_loc, end_date)
                    if not data:
                        print(f"No result for search: {file_prefix}")
                        continue
                    else:
                        print(f"Saved search result: {file_prefix}")
                    with open(f"{file_prefix}_raw.json", "w") as f:
                        f.write(json.dumps(data, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
